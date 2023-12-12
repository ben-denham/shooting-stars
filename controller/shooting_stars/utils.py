import numpy as np
import colorsys

from .device import FRAME_DTYPE


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


def indexes_to_mask(indexes, shape):
    mask = np.zeros(shape, dtype=bool)
    mask[indexes] = True
    return mask
