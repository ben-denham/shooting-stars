from collections import deque
from dataclasses import dataclass
from functools import cache
from time import sleep, monotonic
import logging
from typing import Any, Sequence

import cv2 as cv
import numpy as np

from .device import FRAME_DTYPE, DeviceDisconnected
from .utils import hexstring_to_rgb

COMPONENT_COUNT = 4
W = slice(0, 1)
RGBW = slice(0, 4)
RGB = slice(1, 4)

FRAME_DELAY_MILLISECONDS = 80
FRAME_DELAY_SECONDS = FRAME_DELAY_MILLISECONDS / 1000

LOCAL_PRESENCE_MAP_SIZE = (30, 30)


@dataclass
class Presence:
    colour: np.ndarray
    last_timestamp: int
    presence_maps: deque[np.ndarray]


class PresenceState:

    def __init__(self, *, light_positions: np.ndarray, local_config: dict[str, Any]):
        self.light_positions = light_positions
        self.local_colour = hexstring_to_rgb(local_config['colour'])
        self.local_presence_map = np.zeros(LOCAL_PRESENCE_MAP_SIZE)
        self.remote_id_to_presence = {}
        self.last_image = None
        self.cap = None
        self.frame = np.zeros((len(self.light_positions), COMPONENT_COUNT), dtype=FRAME_DTYPE)
        self.twinkles = {}

    def __enter__(self):
        cap_opened = False
        while not cap_opened:
            logging.info('Opening video capture')
            self.cap = cv.VideoCapture(-1)
            cap_opened = self.cap.isOpened()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cap.release()

    def update_local_presence_map(self):
        ret, image = self.cap.read()
        if not ret:
            logging.info('Failed to capture image')
            return None

        image = cv.resize(image, (500, 500))
        image = cv.GaussianBlur(image, (19, 19), 0)
        image = cv.resize(image, LOCAL_PRESENCE_MAP_SIZE)
        # Flip along both axes so that 0,0 is bottom left
        image = cv.flip(image, -1)

        if self.last_image is not None:
            image_delta = cv.absdiff(self.last_image, image)
            image_delta = cv.cvtColor(image_delta, cv.COLOR_BGR2GRAY)
            _, image_delta = cv.threshold(image_delta, 10, 255, cv.THRESH_BINARY)
            image_delta = cv.dilate(image_delta, None, iterations=2)
            image_delta = cv.GaussianBlur(image_delta, (21, 21), 0)
            self.local_presence_map = image_delta

        if self.last_image is None:
            self.last_image = image
        else:
            self.last_image = cv.addWeighted(self.last_image, 0.5, image, 0.5, 0)

        return self.local_presence_map

    def update_remote_presences(self, remote_presences: Sequence[dict]):
        for remote_presence in remote_presences:
            remote_id = remote_presence['id']
            if remote_id not in self.remote_id_to_presence:
                # If no previous data for this remote, ignore all
                # existing events by setting last_timestamp to their
                # max timestamp
                prev_timestamps = [event['timestamp'] for event in remote_presence['presenceEvents']]
                self.remote_id_to_presence[remote_id] = Presence(
                    colour=hexstring_to_rgb(remote_presence['config']['colour']),
                    last_timestamp=(max(prev_timestamps) if prev_timestamps else 0),
                    # Only keep a fixed number of recent maps
                    presence_maps=deque(maxlen=10)
                )
            presence = self.remote_id_to_presence[remote_id]
            presence.colour = hexstring_to_rgb(remote_presence['config']['colour'])

            for event in remote_presence['presenceEvents']:
                # Only add an event if it is more recent than all
                # previous events
                if event['timestamp'] <= presence.last_timestamp:
                    continue
                presence.presence_maps.append(np.array(event['presenceMap']))

    @cache
    def get_light_map_indexes(self, map_shape: tuple[int, int]) -> np.ndarray:
        position_range = (self.light_positions.max(axis=0) - self.light_positions.min(axis=0))
        zero_one_indexes = np.divide(
            (self.light_positions - self.light_positions.min(axis=0)),
            position_range,
            out=np.zeros_like(self.light_positions),
            where=(position_range != 0),
        )
        max_indexes = np.array(map_shape) - 1
        indexes = np.floor(zero_one_indexes * max_indexes).astype(int)
        return indexes

    def get_frame_component(self, *, presence_map, colour):
        light_indexes = self.get_light_map_indexes(presence_map.shape)
        scaled_presence_map = (presence_map / 255) * 0.02
        light_brightness = scaled_presence_map[light_indexes[:, 0], light_indexes[:, 1]]
        return (
            np.broadcast_to(
                light_brightness,
                (colour.shape[0], light_brightness.shape[0]),
            ).T
            *
            np.broadcast_to(
                colour,
                (light_brightness.shape[0], colour.shape[0]),
            )
        )

    def tick_frame(self):
        self.frame = self.frame.astype(float)

        components = [
            self.get_frame_component(
                presence_map=self.local_presence_map,
                colour=self.local_colour,
            ),
        ]
        for remote_presence in self.remote_id_to_presence.values():
            try:
                presence_map = remote_presence.presence_maps.popleft()
            except IndexError:
                pass
            else:
                components.append(self.get_frame_component(
                    presence_map=presence_map,
                    colour=remote_presence.colour,
                ))

        # Fade-out any light+colour that isn't being added to.
        fadeout_mask = np.full(self.frame[:, RGB].shape, True)
        for component in components:
            fadeout_mask = fadeout_mask & (component == 0)
        fadeout = 1 - (fadeout_mask * 0.25)
        self.frame[:, RGB] = self.frame[:, RGB] * fadeout

        # Add motion to lights
        for component in components:
            self.frame[:, RGB] += component

        # Fade last twinkles
        self.frame[:, W] = self.frame[:, W] * 0.85
        # Randomly add new twinkles
        if np.random.rand() > 0.3:
            for _ in range(2):
                self.twinkles[np.random.randint(self.frame.shape[0])] = 0
        # Grow each twinkle to max brightness over `twinkle_steps` steps
        twinkle_steps = 15
        self.twinkles = {
            twinkle_idx: twinkle_step + 1
            for twinkle_idx, twinkle_step in self.twinkles.items()
            if twinkle_step < twinkle_steps
        }
        for twinkle_idx, twinkle_step in self.twinkles.items():
            self.frame[twinkle_idx, W] += int((1.1 / twinkle_steps) * 255)

        self.frame = np.clip(self.frame, 0, 255).astype(FRAME_DTYPE)


def run_presence(*, device, presence_sub):
    next_time = monotonic()

    while not presence_sub.ready:
        sleep(1)
    local_config_promise = presence_sub.call('presence.getConfig', [presence_sub.token])
    local_config = local_config_promise.await_result()

    while True:
        if device.connected:
            layout = device.get_layout()
            break
        logging.info('Waiting for layout')
        sleep(1)

    # Keep only 2 dimensions
    light_positions = np.array([
        [point['y'], point['x']]
        for point in layout['coordinates']
    ])

    with PresenceState(light_positions=light_positions, local_config=local_config) as presence_state:
        while True:
            next_time = next_time + FRAME_DELAY_SECONDS
            sleep(max(0, next_time - monotonic()))
            frame_start_time = monotonic()

            # Update remote presence_maps
            if presence_sub.state:
                remote_presences = list(presence_sub.state.values())
                presence_state.update_remote_presences(remote_presences)

            # Get local presence_map from webcam and send to server
            local_presence_map = presence_state.update_local_presence_map()
            if local_presence_map is not None:
                try:
                    presence_sub.call('presence.sendPresence', [
                        presence_sub.token,
                        local_presence_map.tolist(),
                    ])
                except Exception as ex:
                    logging.info(f'sendPresence failed: {ex}')

            # Animate a frame of animation
            presence_state.tick_frame()

            try:
                device.set_frame_array(presence_state.frame)
            except DeviceDisconnected:
                logging.info(f'Device disconnected')
            logging.info(f'Frame render time: {monotonic() - frame_start_time}')
