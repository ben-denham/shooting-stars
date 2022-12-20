import logging
from time import sleep, monotonic

import numpy as np
import tetris
from tetris import MinoType, Move

from .device import FRAME_DTYPE, DeviceDisconnected

FRAMES_PER_SECOND = 10
FRAME_DELAY_SECONDS = 1 / FRAMES_PER_SECOND

LED_COUNT = 200
COMPONENT_COUNT = 3
RGB = slice(0, 3)

ROWS = 20
COLS = 10
if COLS % 2 != 0:
    raise ValueError('Rendering logic expects an even number of columns.')
MID_COL = int(COLS / 2)
MAX_ROW = ROWS - 1

GAME_ROWS = 18
GAME_ROW_OFFSET = 1

COLOURS = {
    MinoType.EMPTY: (0, 0, 0),
    MinoType.I: (255, 216, 0),
    MinoType.J: (255, 0, 0),
    MinoType.L: (0, 127, 0),
    MinoType.O: (75, 0, 130),
    MinoType.S: (100, 50, 0),
    MinoType.T: (0, 250, 171),
    MinoType.Z: (0, 100, 250),
    MinoType.GHOST: (0, 0, 0),
    MinoType.GARBAGE: (0, 0, 0),
}

def get_frame_index(row_i, col_i):
    # The first row in the top, the first col is the left.
    if col_i < MID_COL:
         # Left side of the board:
         # * Starts at (MAX_ROW, (MID_COL - 1)) -> frame[0]
         # * Then snakes up and down until (0, 0) -> frame[99]
         col_min_frame_i = ((MID_COL - 1) - col_i) * ROWS
         col_goes_up = (col_i % 2) == 0
    else:
        # Right side of the board:
        # * Starts at (MAX_ROW, MID_COL) -> frame[100]
        # * Then snakes up and down until (0, 9) -> frame[199]
        col_min_frame_i = col_i * ROWS
        col_goes_up = (col_i % 2) == 1
    frame_i_within_col = (MAX_ROW - row_i) if not col_goes_up else row_i
    frame_i = col_min_frame_i + frame_i_within_col
    # logging.info(f'({row_i}, {col_i}), {col_min_frame_i}, {frame_i_within_col}, {frame_i}')
    return frame_i

def render_game(*, device, game):
    # The frame
    frame = np.zeros((LED_COUNT, COMPONENT_COUNT), dtype=FRAME_DTYPE)

    # The playfield is GAME_ROWS x COLS, with the first row being the top
    # and the first col being the left.
    for row_i, row in enumerate(game.playfield, start=GAME_ROW_OFFSET):
        for col_i, pixel in enumerate(row):
            # Short-circuit for majority of empty/zero pixels
            if pixel == MinoType.EMPTY:
                continue
            frame_i = get_frame_index(row_i, col_i)
            frame[frame_i, RGB] = COLOURS[pixel]

    for col_i in range(COLS):
        frame[get_frame_index(0, col_i), RGB] = (127, 127, 127)
        frame[get_frame_index(ROWS - 1, col_i), RGB] = (127, 127, 127)

    # Points for orientation.
    # frame[0, RGB] = (255, 0, 0)
    # frame[99, RGB] = (0, 255, 0)
    # frame[100, RGB] = (0, 0, 255)
    # frame[199, RGB] = (255, 255, 0)

    device.set_frame_array(frame)


def run_blocks(*, device, inputs_sub):
    """Render frames in a continuous loop, raising device errors """
    last_input_timestamp = 0
    next_time = monotonic()
    while True:
        game = tetris.BaseGame(board_size=(GAME_ROWS, COLS))

        while True:
            next_time = next_time + FRAME_DELAY_SECONDS
            sleep(max(0, next_time - monotonic()))
            game.tick()

            latest_input_timestamp = last_input_timestamp
            if inputs_sub.state:
                game_inputs = list(inputs_sub.state.values())[0]['inputs']
                for game_input in game_inputs:
                    if game_input['timestamp'] <= last_input_timestamp:
                        continue

                    if game_input['type'] == 'left':
                        game.push(Move.left())
                    elif game_input['type'] == 'right':
                        game.push(Move.right())
                    elif game_input['type'] == 'rotate':
                        game.push(Move.rotate(1))
                    elif game_input['type'] == 'drop':
                        game.push(Move.hard_drop())

                    latest_input_timestamp = max(latest_input_timestamp, game_input['timestamp'])
            last_input_timestamp = latest_input_timestamp

            frame_start_time = monotonic()

            try:
                render_game(
                    device=device,
                    game=game,
                )
            except DeviceDisconnected:
                logging.info('Device disconnected')

            try:
                inputs_sub.call('blocks.updateState', [inputs_sub.token, {
                    'score': game.score,
                    'playfield': game.playfield.tolist(),
                }])
            except Exception as ex:
                logging.info(f'updateState failed: {ex}')

            logging.info(f'Frame render time: {monotonic() - frame_start_time}')

            if game.lost:
                break
