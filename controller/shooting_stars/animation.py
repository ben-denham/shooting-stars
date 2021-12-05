import logging
from time import sleep, monotonic
import numpy as np
from itertools import cycle
from operator import itemgetter

from .utils import hsv_to_rgb, hue_to_rgb
from .device import FRAME_DTYPE

FRAMES_PER_SECOND = 20
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


class AnimationState:

    def __init__(self):
        self.rainbow_colours = self.get_random_colours()
        self.gradual_hue = 0
        self.twinkle_brightness = np.arange(0, LED_COUNT) % 2 == 0
        self.rain_brightness = np.zeros(LED_COUNT)
        self.wave_brightness = np.zeros(LED_COUNT)

    def tick(self, frame_idx):
        # Rainbow
        seconds_between_rainbow = 1
        if (frame_idx % (FRAMES_PER_SECOND * seconds_between_rainbow)) == 0:
            self.rainbow_colours = self.get_random_colours()

        # Twinkle
        seconds_between_twinkle = 1
        if (frame_idx % (FRAMES_PER_SECOND * seconds_between_twinkle)) == 0:
            self.twinkle_brightness = ~self.twinkle_brightness

        # Rain
        seconds_between_rain = 1 / FRAMES_PER_SECOND
        rain_drops_per_second = 20
        rain_fade_seconds = 2
        rain_drops = int(round(rain_drops_per_second / FRAMES_PER_SECOND))
        rain_fade = (1 / (FRAMES_PER_SECOND * rain_fade_seconds))
        self.rain_brightness = np.maximum(0, self.rain_brightness - rain_fade)
        if (frame_idx % (FRAMES_PER_SECOND * seconds_between_rain)) == 0:
            self.rain_brightness[np.random.randint(LED_COUNT, size=rain_drops)] = 1

        # Gradual
        gradual_cycle_seconds = 10
        self.gradual_hue += 1 / (FRAMES_PER_SECOND * gradual_cycle_seconds)

        # Wave
        wave_width = 10
        self.wave_brightness = np.maximum(0, self.wave_brightness - (1 / wave_width))
        # Negative index switches direction of lights
        next_wave_icicle_idx = -(frame_idx % len(ICICLE_LEDS))
        self.wave_brightness[ICICLE_LEDS[next_wave_icicle_idx]] = 1

    def get_random_colours(self):
        hues = np.random.rand(LED_COUNT)
        return hue_to_rgb(hues)


def render_frame(*, device, lights, animation_state, frame_idx):
    animation_state.tick(frame_idx)

    frame = np.zeros((LED_COUNT, COMPONENT_COUNT), dtype=FRAME_DTYPE)
    brightness = np.ones(LED_COUNT)

    for light in sorted(lights.values(), key=itemgetter('idx')):
        light_idx = light['idx']
        if light_idx >= len(SEGMENT_LEDS):
            logging.warn('Light idx out of range')
            continue

        light_leds = SEGMENT_LEDS[light_idx]

        # Colour mode
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

        # Animation
        if light['animation'] == 'static':
            # Default full brightness
            pass
        elif light['animation'] == 'twinkle':
            brightness[light_leds] = animation_state.twinkle_brightness[light_leds]
        elif light['animation'] == 'rain':
            brightness[light_leds] = animation_state.rain_brightness[light_leds]
        elif light['animation'] == 'wave':
            brightness[light_leds] = animation_state.wave_brightness[light_leds]

    frame = (frame * brightness[:, np.newaxis]).astype(FRAME_DTYPE)
    #print(frame, flush=True)
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
