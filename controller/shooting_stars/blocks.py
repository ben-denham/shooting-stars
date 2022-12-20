import dataclasses
import logging
from queue import SimpleQueue
from threading import Thread, Lock
from time import sleep, monotonic

import numpy as np
import tetris
from tetris import MinoType

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
# Number of seconds to wait between AI moves
AI_MOVE_WAIT_SECONDS = 0.75


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


class BlocksTrainer:

    def __init__(self):
        self.train_queue = SimpleQueue()
        self.test_queue = SimpleQueue()
        self.stopped = False
        self.move = None
        self.move_lock = Lock()

    def start(self):
        """Run the trainer in a new thread"""
        monitor_thread = Thread(target=self.run)
        monitor_thread.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            try:
                self.train(*self.train_queue.get_nowait())
            except:
                pass
            try:
                self.test(*self.test_queue.get_nowait())
            except:
                pass

    def train(self, board, piece):
        # TODO
        pass

    def test(self, board, piece):
        # TODO
        y = 0
        r = 1
        self.set_move((y, r))

    def set_move(self, move):
        with self.move_lock:
            self.move = move


class TrainableBlocksGame(tetris.BaseGame):

    @classmethod
    def new_game(cls, trainer):
        return cls(board_size=(GAME_ROWS, COLS),
                   trainer=trainer)

    def __init__(self, *args, trainer: BlocksTrainer, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.trainer = trainer
        self.ai_mode = False

    def _lock_piece(self) -> None:
        # Train the AI when a user places a piece
        if not self.ai_mode:
            self.trainer.train_queue.put((self.board.copy(), dataclasses.replace(self.piece)))
        self.trainer.set_move(None)
        return super()._lock_piece()


def run_blocks(*, device, inputs_sub, trainer):
    """Render frames in a continuous loop, raising device errors """
    last_input_timestamp = 0
    next_time = monotonic()
    last_input_time = monotonic()
    last_ai_time = monotonic()
    web_updates_enabled = True
    while True:
        game = TrainableBlocksGame.new_game(trainer)

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
                        game = TrainableBlocksGame.new_game(trainer)
                    elif game_input['type'] == 'left':
                        game.left()
                    elif game_input['type'] == 'right':
                        game.right()
                    elif game_input['type'] == 'rotate':
                        game.rotate()
                    elif game_input['type'] == 'drop':
                        game.hard_drop()

                    latest_input_timestamp = max(latest_input_timestamp, game_input['timestamp'])
            last_input_timestamp = latest_input_timestamp

            # Update game state
            if (monotonic() - last_input_time) > AI_TIMEOUT_SECONDS:
                game.ai_mode = True

            # Only run the game if the device is connected or someone is playing
            if device.connected or not game.ai_mode:
                if game.ai_mode and trainer.move is not None and ((monotonic() - last_ai_time) > AI_MOVE_WAIT_SECONDS):
                    last_ai_time = monotonic()
                    # Move towards the chosen move, one step at a time.
                    target_y, target_r = trainer.move
                    if game.piece.r != target_r:
                        game.rotate()
                    elif game.piece.y > target_y:
                        game.left()
                    elif game.piece.y < target_y:
                        game.right()
                    else:
                        game.hard_drop()

                game.tick()

                if game.ai_mode and trainer.move is None:
                    # Start choosing the next move
                    trainer.test_queue.put((game.board.copy(), dataclasses.replace(game.piece)))

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
