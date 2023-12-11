from collections import deque
from dataclasses import dataclass
import logging
from time import sleep, monotonic
from typing import Optional

import numpy as np

from .utils import hsv_to_rgb
from .device import FRAME_DTYPE, DeviceDisconnected

COMPONENT_COUNT = 3
RGB = slice(0, 3)

STEP_DURATION_MILLISECONDS = 100
STEP_DURATION_SECONDS = STEP_DURATION_MILLISECONDS / 1000
FRAME_DELAY_SECONDS = STEP_DURATION_SECONDS

VELOCITY_MAGNITUDE = 0.01
MAX_ILLUMINATION_DISTANCE = 10
MAX_STORED_STEPS = 100


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
    velocity: np.ndarray
    timestamp: int


@dataclass(frozen=True)
class PainterState:
    colour: Colour
    velocity: np.ndarray
    position: np.ndarray
    last_step_timestamp: int
    steps: list[PainterStep]
    loaded: bool

    def update(self, *, step, light_positions):
        timestamp = step.timestamp if step else self.last_step_timestamp
        colour = step.colour if step else self.colour
        velocity = step.velocity if step else self.velocity
        if np.linalg.norm(velocity) <= 0:
            velocity = self.velocity

        # Check for a positive dot product between light positions
        # (relative to current position) and the direction of velocity
        # (dot product is positive when vectors are within 90 degrees)
        relative_light_positions = light_positions - self.position
        dot_products = np.sum(relative_light_positions * velocity, axis=1)
        same_direction_mask = dot_products > 0
        # Scale velocity to have a magnitude of VELOCITY_MAGNITUDE
        velocity_norm = np.linalg.norm(velocity)
        scaled_velocity = velocity / velocity_norm if velocity_norm > 0 else velocity
        scaled_velocity = scaled_velocity * VELOCITY_MAGNITUDE
        # Find distance between every point and (position + scaled_velocity)
        delta_position = self.position + scaled_velocity
        distances_to_delta_position = np.linalg.norm(light_positions - delta_position, axis=1)
        # Ignore distances to points we know are in the wrong direction.
        distances_to_delta_position[~same_direction_mask] = np.inf
        # Find nearest point to delta_position in the right direction
        nearest_index = np.argmin(distances_to_delta_position)
        # If no lights are in the right direction, stay at the current position
        if distances_to_delta_position[nearest_index] == np.inf:
            position = self.position
        else:
            position = light_positions[nearest_index]

        if self.loaded:
            steps = []
        elif step is None:
            steps = self.steps
        else:
            steps = [*self.steps, step][-MAX_STORED_STEPS:]

        return PainterState(
            last_step_timestamp=timestamp,
            colour=colour,
            velocity=velocity,
            position=position,
            steps=steps,
            loaded=self.loaded,
        )


INITIAL_STATE = PainterState(
    colour=Colour(hue=0, saturation=0),
    velocity=np.array([0, 0, 0]),
    position=np.array([0, 0, 0]),
    last_step_timestamp=0,
    steps=[],
    loaded=False,
)


class PaintState:

    def __init__(self, *, light_positions):
        axes_max = np.max(light_positions, axis=0)
        axes_min = np.min(light_positions, axis=0)
        self.light_positions = (light_positions - axes_min) / (axes_max - axes_min)
        self.last_movement_timestamp = None
        self.painter_to_steps = {}
        self.painter_to_state = {}
        self.frame = np.zeros((self.light_positions.shape[0], COMPONENT_COUNT), dtype=FRAME_DTYPE)

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
                        velocity=np.array([0, 0, 0]),
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

                velocity_vector = current_step.velocity
                for step_velocity, step_colour in zip(movement['velocities'], step_colours):
                    velocity_vector = np.array([
                        step_velocity['x'],
                        step_velocity['y'],
                        step_velocity['z'],
                    ])
                    painter_steps.append(PainterStep(
                        colour=step_colour,
                        velocity=velocity_vector,
                        timestamp=movement['timestamp'],
                    ))
            self.painter_to_steps[painter_id] = painter_steps

        self.last_movement_timestamp = max([
            step.timestamp
            for steps in self.painter_to_steps.values()
            for step in steps
        ], default=self.last_movement_timestamp)

    def tick_state(self):
        self.painter_to_steps = {
            painter_id: steps
            for painter_id, steps in self.painter_to_steps.items()
            if len(steps) > 0
        }
        painter_ids = set([*self.painter_to_steps.keys(), *self.painter_to_state.keys()])
        for painter_id in painter_ids:
            painter_state = self.painter_to_state.get(painter_id, INITIAL_STATE)
            try:
                step = self.painter_to_steps.get(painter_id, deque()).popleft()
            except IndexError:
                step = None
            new_painter_state = painter_state.update(
                step=step,
                light_positions=self.light_positions,
            )
            self.painter_to_state[painter_id] = new_painter_state

    def tick_frame(self):
        self.frame = self.frame * 0.1
        for painter_id, painter_state in self.painter_to_state.items():
            rgb = hsv_to_rgb(h=painter_state.colour.hue, s=painter_state.colour.saturation, v=1)
            distances = np.linalg.norm(self.light_positions - painter_state.position, axis=1)
            # weights = 1 / (9 * distances)
            # weights[weights < 0.5] = 0
            # Linearly scale from weight 1 to 0 between distance 0 and MAX_ILLUMINATION_DISTANCE
            weights = 1 - (distances * MAX_ILLUMINATION_DISTANCE)
            self.frame += np.outer(weights, rgb)
        self.frame = np.clip(self.frame, 0, 255).round().astype(FRAME_DTYPE)
        #self.frame = (np.ones((self.light_positions.shape[0], COMPONENT_COUNT), dtype=FRAME_DTYPE) * 100).astype(FRAME_DTYPE)

    def save_painters(self):
        # TODO
        pass

    def load_painters(self):
        # TODO
        pass


def render_cone(*, device, paint_state):
    #from pprint import pformat
    #logging.info(pformat(paint_state.painter_to_state))
    logging.info(f'{paint_state.frame.shape}, {np.isnan(paint_state.frame).sum()}')
    device.set_frame_array(paint_state.frame)


import json

def run_cone(*, device, paint_sub):
    """Render frames in a continuous loop"""
    next_time = monotonic()

    # TODO
    # while True:
    #     if True or device.connected:
            # layout = device.get_layout()
    with open('layout.json', 'r') as json_file:
        layout = json.loads(json_file.read())
    light_positions = np.array([
        [point['z'], point['x'], point['y']]
        for point in layout['coordinates']
    ])
    #break

    paint_state = PaintState(light_positions=light_positions)

    while True:
        next_time = next_time + FRAME_DELAY_SECONDS
        sleep(max(0, next_time - monotonic()))
        frame_start_time = monotonic()

        if paint_sub.state:
            paint_records = list(paint_sub.state.values())
            if len(paint_records) > 0:
                paint_state.add_movements(paint_records[0]['painterMovements'])

        paint_state.load_painters()
        paint_state.tick_state()
        paint_state.tick_frame()
        paint_state.save_painters()

        try:
            render_cone(
                device=device,
                paint_state=paint_state,
            )
        except DeviceDisconnected:
            logging.info(f'Device disconnected')
        logging.info(f'Frame render time: {monotonic() - frame_start_time}')
