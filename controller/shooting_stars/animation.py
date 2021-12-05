import logging
from time import sleep, monotonic
import numpy as np
from itertools import cycle
from operator import itemgetter
import colorsys

from .device import FRAME_DTYPE

FRAMES_PER_SECOND = 2
FRAME_DELAY_SECONDS = 1 / FRAMES_PER_SECOND

COMPONENT_COUNT = 4
W = 0
RGB = slice(1, 4)
LED_COUNT = 190
ICICLE_SCHEMA = [2, 4, 6, 2, 5]

ICICLE_LEDS = []
led_idx = 0
for icicle_size in cycle(ICICLE_SCHEMA):
    ICICLE_LEDS.append(np.arange(
        led_idx,
        min(led_idx + icicle_size, LED_COUNT)
    ))
    led_idx += icicle_size
    if led_idx >= LED_COUNT:
        break

assert len(ICICLE_LEDS) == 50
SEGMENT_LEDS = list(reversed([
    np.concatenate(ICICLE_LEDS[0:5]),
    np.concatenate(ICICLE_LEDS[5:10]),
    np.concatenate(ICICLE_LEDS[10:15]),
    np.concatenate(ICICLE_LEDS[15:20]),
    np.concatenate(ICICLE_LEDS[20:25]),
    np.concatenate(ICICLE_LEDS[25:30]),
    np.concatenate(ICICLE_LEDS[30:35]),
    np.concatenate(ICICLE_LEDS[35:40]),
    np.concatenate(ICICLE_LEDS[40:45]),
    np.concatenate(ICICLE_LEDS[45:50]),
]))


def hsv_to_rgb(h, s, v):
    rgb = np.array(colorsys.hsv_to_rgb(h, s, v))
    return (rgb * 255).round().astype(FRAME_DTYPE)


def hue_to_rgb(hues):
    """Takes a vector array of hues in range [0, 1], and returns a 3
    column array of RGB values (for max saturation and value). Based
    on: matplotlib.colors.hsv_to_rgb
    """
    i = (hues * 6.0).astype(int)
    t = (hues * 6.0) - i
    q = 1.0 - t

    r = np.empty_like(hues)
    g = np.empty_like(hues)
    b = np.empty_like(hues)

    idx = i % 6 == 0
    r[idx] = 1
    g[idx] = t[idx]
    b[idx] = 0

    idx = i == 1
    r[idx] = q[idx]
    g[idx] = 1
    b[idx] = 0

    idx = i == 2
    r[idx] = 0
    g[idx] = 1
    b[idx] = t[idx]

    idx = i == 3
    r[idx] = 0
    g[idx] = q[idx]
    b[idx] = 1

    idx = i == 4
    r[idx] = t[idx]
    g[idx] = 0
    b[idx] = 1

    idx = i == 5
    r[idx] = 1
    g[idx] = 0
    b[idx] = q[idx]

    rgb = np.stack([r, g, b], axis=-1)
    return (rgb * 255).round().astype(FRAME_DTYPE)


class AnimationState:

    def __init__(self):
        self.rainbow_colours = self.get_random_colours()
        self.gradual_hue = 0

    def tick(self, frame_idx):
        # Update rainbow colours
        seconds_between_rainbow_change = 1
        if (frame_idx % (FRAMES_PER_SECOND * seconds_between_rainbow_change)) == 0:
            self.rainbow_colours = self.get_random_colours()

        gradual_cycle_seconds = 10
        self.gradual_hue += 1 / (FRAMES_PER_SECOND * gradual_cycle_seconds)

    def get_random_colours(self):
        hues = np.random.rand(LED_COUNT)
        return hue_to_rgb(hues)


def render_frame(*, device, lights, animation_state, frame_idx):
    animation_state.tick(frame_idx)

    frame = np.zeros((LED_COUNT, COMPONENT_COUNT), dtype=FRAME_DTYPE)

    for light in sorted(lights.values(), key=itemgetter('idx')):
        light_idx = light['idx']
        if light_idx >= len(SEGMENT_LEDS):
            logging.warn('Light idx out of range')
            continue

        light_leds = SEGMENT_LEDS[light_idx]

        if light['colourMode'] == 'white':
            frame[light_leds, W] = 255
        elif light['colourMode'] == 'colour':
            frame[light_leds, RGB] = hsv_to_rgb(h=light['colourHue'], s=light['colourSaturation'], v=1)
        elif light['colourMode'] == 'rainbow':
            frame[light_leds, RGB] = animation_state.rainbow_colours[light_leds]
        elif light['colourMode'] == 'gradual':
            frame[light_leds, RGB] = hsv_to_rgb(h=animation_state.gradual_hue, s=1, v=1)
        else:
            logging.warn('Unrecognised colour mode')

    print(frame, flush=True)
    device.set_frame_array(frame)


def run_animation(*, device, lights, animation_state):
    """Render frames in a continuous loop, raising device errors """
    next_time = monotonic()
    frame_idx = 0
    while True:
        frame_start_time = monotonic()
        render_frame(
            device=device,
            lights=lights,
            animation_state=animation_state,
            frame_idx=frame_idx,
        )
        logging.info(f'Frame render time: {monotonic() - frame_start_time}')

        # Prevent frame_idx from reaching infinity
        frame_idx = (frame_idx + 1) % 10_000

        next_time = next_time + FRAME_DELAY_SECONDS
        sleep(max(0, next_time - monotonic()))
