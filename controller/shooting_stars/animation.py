import logging
from time import sleep, monotonic
import numpy as np

FRAMES_PER_SECOND = 2
FRAME_DELAY_SECONDS = 1 / FRAMES_PER_SECOND

LED_COUNT = 190
COMPONENT_COUNT = 4
W = 0
R = 1
G = 2
B = 3


def render_frame(*, device, lights, frame_idx):
    frame = np.zeros((LED_COUNT, COMPONENT_COUNT), dtype=np.ubyte)
    frame[:, (frame_idx % COMPONENT_COUNT)] = 255
    device.set_frame_array(frame)


def run_animation(*, device, lights):
    """Render frames in a continuous loop, raising device errors """
    next_time = monotonic()
    frame_idx = 0
    while True:
        frame_start_time = monotonic()
        render_frame(
            device=device,
            lights=lights,
            frame_idx=frame_idx,
        )
        logging.info(f'Frame render time: {monotonic() - frame_start_time}')

        # Prevent frame_idx from reaching infinity
        frame_idx = (frame_idx + 1) % 10_000

        next_time = next_time + FRAME_DELAY_SECONDS
        sleep(max(0, next_time - monotonic()))
