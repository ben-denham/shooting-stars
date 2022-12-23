from datetime import datetime, timezone
import dataclasses
import logging
from queue import SimpleQueue, Empty
from threading import Thread, Lock
from time import sleep, monotonic
from typing import Iterator

import numpy as np
import river.naive_bayes
import tetris
from tetris import MinoType, Piece
from tetris.engine import RotationSystem
from tetris.types import Board, Minos

from .device import FRAME_DTYPE, DeviceDisconnected

DEBUG = False

FRAMES_PER_SECOND = 5
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

    border_colour = (127, 127, 127) if game.ai_mode else (127, 25, 25)
    for col_i in range(COLS):
        frame[get_frame_index(0, col_i), RGB] = border_colour
        frame[get_frame_index(ROWS - 1, col_i), RGB] = border_colour

    # Points for orientation.
    # frame[0, RGB] = (255, 0, 0)
    # frame[99, RGB] = (0, 255, 0)
    # frame[100, RGB] = (0, 0, 255)
    # frame[199, RGB] = (255, 255, 0)

    device.set_frame_array(frame)


@dataclasses.dataclass(frozen=True)
class GameState:
    """Represents the current state of a blocks game."""
    rs: RotationSystem
    board: Board
    piece: Piece


@dataclasses.dataclass(frozen=True)
class Move:
    """Represents a possible move of a piece to a given y/horizontal
    position and rotation."""
    y: int
    r: int


class BlocksTrainer:
    """Runs a separate thread for training and applying the AI model.

    Note that a board's 0/x dimension is vertical/rows going
    top-to-bottom, and the 1/y dimension is horizontal/columns going
    right-to-left.
    """

    def __init__(self):
        self.train_queue = SimpleQueue()
        self.test_queue = SimpleQueue()
        self.stopped = False
        self.move = None
        self.move_lock = Lock()
        self.reset_flag = False
        self.reset_model()

    def reset_model(self):
        logging.info('Model reset')
        self.model = river.naive_bayes.GaussianNB()

    def start(self):
        """Run the trainer in a new thread"""
        monitor_thread = Thread(target=self.run)
        monitor_thread.start()

    def stop(self):
        """Called from the main thread to tell the trainer thread to stop."""
        self.stopped = True

    def run(self):
        while not self.stopped:
            # Reset the model if the main thread set the reset_flag
            if self.reset_flag:
                try:
                    self.reset_model()
                    self.reset_flag = False
                except:
                    logging.exception('Reset failed')
            # Process the next training record
            try:
                self.train(self.train_queue.get_nowait())
            except Empty:
                pass
            except:
                logging.exception('Train failed')
            # Process the next test record
            try:
                self.test(self.test_queue.get_nowait())
            except Empty:
                pass
            except:
                logging.exception('Test failed')

    def get_possible_moves(self, state: GameState) -> Iterator[Move]:
        """For a given state, return the list of possible moves that could be
        made by the AI - excludes moves that would place the piece out
        of bounds on the y axis."""
        board_min_y = 0
        board_max_y = state.board.shape[1] - 1
        for r in range(4):
            minos = state.rs.shapes[state.piece.type][r]
            min_y = board_min_y - min([y for _, y in minos])
            max_y = board_max_y - max([y for _, y in minos])
            for y in range(min_y, max_y + 1):
                yield Move(y=y, r=r)

    def overlaps(self, *, board: Board, minos: Minos, x: int, y: int) -> bool:
        """Checks whether a piece with the given minos, x, and y overlaps the
        top/bottom edges of the board or another piece.

        No need to check y-axis currently because we do not suggest
        moves that could be out of bounds.

        """
        for mx, my in minos:
            if (x + mx) not in range(board.shape[0]):
                return True
            if board[x + mx, y + my] != 0:
                return True
        return False

    def get_board_stats(self, board: Board) -> dict[str, float]:
        """
        Get stats about the current board state.
        """
        max_height = 0
        hole_count = 0

        # Convert piece numbers to Boolean
        for col in (board > 0).T:
            # Skip empty columns
            if not any(col):
                continue

            # First non-zero index in column
            highest_filled_idx = np.argmax(col)
            # Indexes start at the top, so height is (board height - index)
            height = board.shape[0] - highest_filled_idx
            if height > max_height:
                max_height = height
            # Count zero values after highest_filled_index
            hole_count += np.sum(~col[highest_filled_idx:])

        return {
            'max_height': max_height,
            'hole_count': hole_count,
        }

    def get_move_features(self, state: GameState, move: Move,
                          pre_move_stats: dict[str, float]) -> dict[str, float]:
        """
        Get a dictionary of features to represent a possible move in the AI model.

        Features inspired by: https://levelup.gitconnected.com/tetris-ai-in-python-bd194d6326ae
        """
        y = move.y
        minos = state.rs.shapes[state.piece.type][move.r]
        # Start at the top of the board to avoid initial check for illegal moves.
        start_x = 0 - min([x for x, _ in minos])
        # Find the x after dropping
        x = start_x
        for possible_x in range(start_x + 1, state.board.shape[0]):
            if self.overlaps(board=state.board, minos=minos, x=possible_x, y=y):
                break
            x = possible_x

        post_move_board = state.board.copy()
        for mx, my in minos:
            post_move_board[x + mx, y + my] = state.piece.type

        post_move_stats = self.get_board_stats(post_move_board)
        return {
            'height_diff': post_move_stats['max_height'] - pre_move_stats['max_height'],
            'hole_diff': post_move_stats['hole_count'] - pre_move_stats['hole_count'],
            # Count rows that are completely full.
            'lines_cleared': np.sum(np.all(post_move_board, axis=1)),
        }

    def train(self, state: GameState) -> None:
        """Taking a state that represents a piece positioned just before it
        locks, train the AI that the piece's current position represents the
        user-chosen move, against all other possible moves not chosen being
        chosen."""
        pre_move_stats = self.get_board_stats(state.board)
        for move in self.get_possible_moves(state):
            features = self.get_move_features(state, move, pre_move_stats)
            chosen = (move.y == state.piece.y) and (move.r == state.piece.r)
            label = ('CHOSEN' if chosen else 'NOT_CHOSEN')
            logging.info(f'TRAIN: {features}, {label}')
            self.model.learn_one(x=features, y=label)

    def test(self, state: GameState) -> Move:
        """Use the AI to select the best Move to make given the current game
        state."""
        pre_move_stats = self.get_board_stats(state.board)
        moves = list(self.get_possible_moves(state))
        scores = []
        for move in moves:
            features = self.get_move_features(state, move, pre_move_stats)
            prediction = self.model.predict_proba_one(features)
            score = prediction.get('CHOSEN', 0)
            scores.append(score)
        logging.info(f'TEST: {scores}')
        scores = np.array(scores)
        best_indexes = np.argwhere(scores == np.amax(scores)).flatten()
        selected_move_index = np.random.choice(best_indexes)
        self.set_move(moves[selected_move_index])

    def set_move(self, move):
        """Allow the main and trainer threads to safely set/unset the move."""
        with self.move_lock:
            self.move = move


class TrainableBlocksGame(tetris.BaseGame):
    """Keeps track of an ai_mode attribute. When not in AI mode, the
    position of each locked piece is passed to the given trainer."""

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
            self.trainer.train_queue.put(GameState(
                rs=self.rs,
                board=self.board.copy(),
                piece=dataclasses.replace(self.piece),
            ))
        # Clear any current move the trainer has prepared
        # NOTE: We may theoretically get an outdated move if this runs
        # while a move is being processed, but this is unlikely given
        # how long it takes for a piece to move vs how long it takes to
        # compute a Move.
        self.trainer.set_move(None)
        return super()._lock_piece()


def get_inputs(inputs_sub):
    """Utility to get the current set of inputs from inputs_sub."""
    return list(inputs_sub.state.values())[0]['inputs']


def run_blocks(*, device, inputs_sub, trainer):
    """Render frames in a continuous loop, raising device errors """
    # Ignore any initial inputs
    last_input_timestamp = None
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
            if inputs_sub.state:
                if last_input_timestamp is None:
                    # Ignore the first inputs on start - as they are probably stale
                    last_input_timestamp = max(game_input['timestamp'] for game_input in get_inputs(inputs_sub))
                latest_input_timestamp = last_input_timestamp
                for game_input in get_inputs(inputs_sub):
                    # Ignore previously handled inputs.
                    if game_input['timestamp'] <= last_input_timestamp:
                        continue

                    last_input_time = monotonic()
                    web_updates_enabled = True
                    if game.ai_mode:
                        # If coming out of ai mode, start a new game
                        # and model, and ignore the first input.
                        game = TrainableBlocksGame.new_game(trainer)
                        trainer.reset_model()
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

            # Update game mode based on user activity
            if (monotonic() - last_input_time) > AI_TIMEOUT_SECONDS:
                game.ai_mode = True

            # Only run the game if the device is connected or someone is playing
            if device.connected or (not game.ai_mode) or DEBUG:
                # If in ai_mode, and the trainer has a move ready,
                # then move toward that move state every
                # AI_MOVE_WAIT_SECONDS.
                if game.ai_mode and trainer.move is not None and ((monotonic() - last_ai_time) > AI_MOVE_WAIT_SECONDS):
                    last_ai_time = monotonic()
                    # Move towards the chosen move, one step at a time.
                    move = trainer.move
                    if game.piece.r != move.r:
                        game.rotate()
                    elif game.piece.y > move.y:
                        game.left()
                    elif game.piece.y < move.y:
                        game.right()
                    else:
                        game.hard_drop()

                game.tick()

                if game.ai_mode and trainer.move is None:
                    # Start choosing the next move
                    trainer.test_queue.put(GameState(
                        rs=game.rs,
                        board=game.board.copy(),
                        piece=dataclasses.replace(game.piece),
                    ))

                # Send game to device
                try:
                    render_game(
                        device=device,
                        game=game,
                    )
                except DeviceDisconnected:
                    logging.info('Device disconnected')

            # Send game to web (web_updates_enabled is set to False
            # after entering AI mode).
            if web_updates_enabled or DEBUG:
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
