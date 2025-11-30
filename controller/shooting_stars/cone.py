from collections import deque
from dataclasses import dataclass
import logging
from time import sleep, monotonic
from typing import Optional

import numpy as np

from .utils import hsv_to_rgb, indexes_to_mask
from .device import FRAME_DTYPE, DeviceDisconnected

COMPONENT_COUNT = 3
RGB = slice(0, 3)

STEP_DURATION_MILLISECONDS = 200
STEP_DURATION_SECONDS = STEP_DURATION_MILLISECONDS / 1000
FRAME_DELAY_SECONDS = STEP_DURATION_SECONDS

EXCLUDED_LIGHT_INDEXES = [
    *range(0, 14),
    *range(200, 211),
]
MAX_ILLUMINATION_DISTANCE = 0.3


@dataclass(frozen=True)
class Colour:
    hue: float
    saturation: float

    @classmethod
    def from_movement(cls, movement):
        return cls(
            hue=movement['colour']['hue'],
            saturation=movement['colour']['saturation'],
        )

    @classmethod
    def interpolate(cls, *, from_colour, to_colour, n_steps):
        return [
            cls(hue=hue, saturation=saturation)
            for hue, saturation
            in zip(
                np.linspace(from_colour.hue, to_colour.hue, n_steps),
                np.linspace(from_colour.saturation, to_colour.saturation, n_steps),
            )
        ]


@dataclass(frozen=True)
class PainterStep:
    colour: Colour
    direction: np.ndarray
    timestamp: int


@dataclass(frozen=True)
class PainterState:
    colour: Colour
    direction: np.ndarray

    def update(self, *, step):
        # Never allow the direction to point downward by clipping the
        # z value to zero.
        direction = step.direction
        direction[2] = np.max([0, direction[2]])
        direction_magnitude = np.linalg.norm(direction)
        direction = (
            direction / direction_magnitude
            if direction_magnitude > 0
            else self.direction
        )

        return PainterState(
            colour=step.colour,
            direction=direction,
        )


INITIAL_STATE = PainterState(
    colour=Colour(hue=0, saturation=0),
    direction=np.array([0, 0, 1]),
)


class PaintState:

    def __init__(self, *, light_positions):
        # Get the positions of lights that aren't excluded
        included_lights_mask = ~indexes_to_mask(EXCLUDED_LIGHT_INDEXES, light_positions.shape[0])
        included_light_positions = light_positions[included_lights_mask, :]
        # Find the midpoint of the included lights
        lights_origin = (np.max(included_light_positions, axis=0) + np.min(included_light_positions, axis=0)) / 2
        # Set up/down midpoint to the bottom
        lights_origin[2] = 0
        # Get the vector from the origin to each light
        relative_light_positions = light_positions - lights_origin
        # Normalise the magnitude of the relative light positions so
        # that they are on a unit sphere
        light_directions = relative_light_positions / np.linalg.norm(relative_light_positions, axis=1)[:, np.newaxis]

        self.light_directions = light_directions
        self.last_movement_timestamp = None
        self.painter_to_steps = {}
        self.painter_to_state = {}

        self.full_value_frame = np.full((light_positions.shape[0], COMPONENT_COUNT), 255, dtype=FRAME_DTYPE)
        self.frame = np.zeros((light_positions.shape[0], COMPONENT_COUNT), dtype=FRAME_DTYPE)

    def add_movements(self, painter_movements):
        # Ignore the first movements on start - as they are probably stale
        if self.last_movement_timestamp is None:
            self.last_movement_timestamp = max([
                movement['timestamp']
                for movements in painter_movements.values()
                for movement in movements
            ], default=0)

        for painter_id, movements in painter_movements.items():
            painter_steps = self.painter_to_steps.get(painter_id, deque())
            new_movements = [m for m in movements if m['timestamp'] > self.last_movement_timestamp]
            for movement in new_movements:
                step_count = len(movement['velocities'])
                movement_colour = Colour.from_movement(movement)
                if len(painter_steps) == 0:
                    painter_steps.append(PainterStep(
                        colour=movement_colour,
                        direction=np.array([0, 0, 0]),
                        timestamp=movement['timestamp'],
                    ))
                current_step = painter_steps[-1]

                # When the colour changes in a movement, make the
                # colour change gradual over the steps within that
                # movement.
                if movement_colour != current_step.colour:
                    step_colours = Colour.interpolate(
                        from_colour=current_step.colour,
                        to_colour=movement_colour,
                        n_steps=step_count,
                    )
                else:
                    step_colours = [movement_colour for _ in range(step_count)]

                for step_direction, step_colour in zip(movement['velocities'], step_colours):
                    direction_vector = np.array([
                        step_direction['x'],
                        step_direction['y'],
                        step_direction['z'],
                    ])
                    painter_steps.append(PainterStep(
                        colour=step_colour,
                        direction=direction_vector,
                        timestamp=movement['timestamp'],
                    ))
            self.painter_to_steps[painter_id] = painter_steps

        self.last_movement_timestamp = max([
            step.timestamp
            for steps in self.painter_to_steps.values()
            for step in steps
        ], default=self.last_movement_timestamp)

    def tick_state(self):
        painter_ids = set([*self.painter_to_steps.keys(), *self.painter_to_state.keys()])
        for painter_id in painter_ids:
            try:
                step = self.painter_to_steps.get(painter_id, deque()).popleft()
            except IndexError:
                # Remove the painter if there are no steps left for it
                self.painter_to_steps.pop(painter_id, None)
                self.painter_to_state.pop(painter_id, None)
                continue
            painter_state = self.painter_to_state.get(painter_id, INITIAL_STATE)
            painter_state = painter_state.update(step=step)
            self.painter_to_state[painter_id] = painter_state

    def tick_frame(self):
        active_frame_mask = np.full(self.light_directions.shape[0], False)
        active_frame = np.zeros((self.light_directions.shape[0], COMPONENT_COUNT))
        for painter_id, painter_state in self.painter_to_state.items():
            distances = np.linalg.norm(self.light_directions - painter_state.direction, axis=1)
            # Linearly scale from weight 1 to 0 between distance 0 and MAX_ILLUMINATION_DISTANCE
            weights = 1 - (distances / MAX_ILLUMINATION_DISTANCE)
            mask = weights > 0
            active_frame[mask, RGB] = hsv_to_rgb(h=painter_state.colour.hue, s=painter_state.colour.saturation, v=1)
            active_frame_mask = active_frame_mask | mask
        self.full_value_frame[active_frame_mask, RGB] = np.clip(active_frame[active_frame_mask, RGB], 0, 255)
        self.frame = self.full_value_frame.copy()
        self.frame[~active_frame_mask] = self.frame[~active_frame_mask] * 0.25
        self.frame = self.frame.round().astype(FRAME_DTYPE)


def render_cone(*, device, paint_state):
    device.set_frame_array(paint_state.frame)


def run_cone(*, device, paint_sub):
    """Render frames in a continuous loop"""
    next_time = monotonic()

    while True:
        if device.connected:
            layout = device.get_layout()
            break
        logging.info('Waiting for layout')
        sleep(1)

    # Re-orient dimensions so that axis z/2 is up/down
    light_positions = np.array([
        [point['z'], point['x'], point['y']]
        for point in layout['coordinates']
    ])
    paint_state = PaintState(light_positions=light_positions)

    while True:
        next_time = next_time + FRAME_DELAY_SECONDS
        sleep(max(0, next_time - monotonic()))
        frame_start_time = monotonic()

        if paint_sub.state:
            paint_records = list(paint_sub.state.values())
            if len(paint_records) > 0:
                paint_state.add_movements(paint_records[0]['painterMovements'])

        paint_state.tick_state()
        paint_state.tick_frame()

        try:
            render_cone(
                device=device,
                paint_state=paint_state,
            )
        except DeviceDisconnected:
            logging.info(f'Device disconnected')
        logging.info(f'Frame render time: {monotonic() - frame_start_time}')
