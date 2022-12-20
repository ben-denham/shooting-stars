import dataclasses
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

# Number of seconds to wait for a new input before switching to AI mode
AI_TIMEOUT_SECONDS = 15


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

    border_colour = (75, 75, 75) if game.ai_mode else (127, 127, 127)
    for col_i in range(COLS):
        frame[get_frame_index(0, col_i), RGB] = border_colour
        frame[get_frame_index(ROWS - 1, col_i), RGB] = border_colour

    # Points for orientation.
    # frame[0, RGB] = (255, 0, 0)
    # frame[99, RGB] = (0, 255, 0)
    # frame[100, RGB] = (0, 0, 255)
    # frame[199, RGB] = (255, 255, 0)

    device.set_frame_array(frame)


class TrainableBlocksGame(tetris.BaseGame):

    @classmethod
    def new_game(cls):
        return cls(board_size=(GAME_ROWS, COLS))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ai_mode = False

    def _lock_piece(self) -> None:
        """
        Extend the original _lock_piece() that is called whenever a piece is "placed".
        """
        assert self.delta
        piece = self.piece
        for x in range(piece.x + 1, self.board.shape[0]):
            if self.rs.overlaps(dataclasses.replace(piece, x=x)):
                break

            piece.x = x
            self.delta.x += 1

        for x, y in piece.minos:
            self.board[x + piece.x, y + piece.y] = piece.type

        # If all tiles are out of view (half of the internal size), it's a lock-out
        for x, y in piece.minos:
            if self.piece.x + x > self.height:
                break
        else:
            self._lose()

        for i, row in enumerate(self.board):
            if all(row):
                self.board[0] = 0
                self.board[1 : i + 1] = self.board[:i]
                self.delta.clears.append(i)

        self.piece = self.rs.spawn(self.queue.pop())

        # If the new piece overlaps, it's a block-out
        if self.rs.overlaps(self.piece):
            self._lose()

        self.hold_lock = False


def run_blocks(*, device, inputs_sub):
    """Render frames in a continuous loop, raising device errors """
    last_input_timestamp = 0
    next_time = monotonic()
    last_input_time = monotonic()
    web_updates_enabled = True
    while True:
        game = TrainableBlocksGame.new_game()

        while True:
            next_time = next_time + FRAME_DELAY_SECONDS
            sleep(max(0, next_time - monotonic()))

            frame_start_time = monotonic()

            # Handle inputs
            latest_input_timestamp = last_input_timestamp
            if inputs_sub.state:
                game_inputs = list(inputs_sub.state.values())[0]['inputs']
                for game_input in game_inputs:
                    if game_input['timestamp'] <= last_input_timestamp:
                        continue

                    last_input_time = monotonic()
                    web_updates_enabled = True
                    if game.ai_mode:
                        # If coming out of ai mode, start a new game,
                        # and ignore the first input.
                        game = TrainableBlocksGame.new_game()
                    elif game_input['type'] == 'left':
                        game.push(Move.left())
                    elif game_input['type'] == 'right':
                        game.push(Move.right())
                    elif game_input['type'] == 'rotate':
                        game.push(Move.rotate(1))
                    elif game_input['type'] == 'drop':
                        game.push(Move.hard_drop())

                    latest_input_timestamp = max(latest_input_timestamp, game_input['timestamp'])
            last_input_timestamp = latest_input_timestamp

            # Update game state
            if (monotonic() - last_input_time) > AI_TIMEOUT_SECONDS:
                game.ai_mode = True

            game.tick()

            # Send game to device and inputs_sub
            try:
                render_game(
                    device=device,
                    game=game,
                )
            except DeviceDisconnected:
                logging.info('Device disconnected')

            if web_updates_enabled:
                try:
                    inputs_sub.call('blocks.updateState', [inputs_sub.token, {
                        'score': game.score,
                        'playfield': game.playfield.tolist(),
                        'aiMode': game.ai_mode,
                    }])
                    if game.ai_mode:
                        web_updates_enabled = False
                except Exception as ex:
                    logging.info(f'updateState failed: {ex}')

            logging.info(f'Frame render time: {monotonic() - frame_start_time}')

            if game.lost:
                break
