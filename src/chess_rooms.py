"""
chess room class and chess clocks for the server
"""

import platform
from time import time
from random import shuffle
import chess
from stockfish import Stockfish
from chess import engine

STOCKFISH_W_PATH: str = r'./src/engines/stockfish-windows-2022-x86-64-avx2.exe'
STOCKFISH_L_PATH: str = r'./src/engines/stockfish-ubuntu-20.04-x86-64-avx2'
STOCKFISH_PATH: str = STOCKFISH_W_PATH if platform.system() == 'Windows' else STOCKFISH_L_PATH
NEPO_L_PATH: str = r'./src/engines/NepoChessTests'
START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
WHITE = 0
BLACK = 1
DEAFULT_CLOCK = '5|0'

WON: int = 1
LOST: int = -1
DRAW: int = 0

class ChessClock(object):
    """
    A chess clock that can be started and stopped and keeps track of time left.
    """

    def __init__(self, clock: str) -> None:
        time_limit, addition = [int(x) for x in clock.split('|')]
        self.time_left: float = time_limit * 60
        self.start_time: float | None = None
        self.addition: float = addition

    def start(self) -> None:
        """
        save the current time as the start time
        """
        self.start_time = time()

    def get_time_used(self) -> float:
        """
        return the time that passed since the clock was started
        """
        if self.start_time is None:
            return 0
        return time() - self.start_time

    def stop(self) -> None:
        """
        subtract the time that passed since the clock was started from the time left.
        """
        self.time_left -= self.get_time_used()
        self.start_time = None
        self.time_left += self.addition

    def get_time_left(self) -> float:
        """
        return the time left for the player.
        """
        return self.time_left - self.get_time_used()

    def is_timeout(self) -> bool:
        """
        true if the time left is less than or equal to 0
        """
        return self.get_time_left() <= 0


class ChessRoom:
    """
    has all the information about a single chess game.
    """

    def __init__(self, player1: str, player2: str, clock: str) -> None:
        self.players: list[str] = [player1, player2]
        self.clock = clock
        self.clocks: list[ChessClock] = [
            ChessClock(clock),
            ChessClock(clock)
        ]
        shuffle(self.players)
        self.board: chess.Board = chess.Board(START_FEN)
        self.turn: int = 0
        self.closed: bool = False

    def __len__(self) -> int:
        return len(self.board.move_stack)

    def __str__(self) -> str:
        return self.fen()

    def __repr__(self) -> str:
        return f'chess.Board({self.fen()})'

    def update_turn(self) -> None:
        """
        flip turn from 1 to 0 or 0 to 1
        """
        self.stop_clock()
        self.turn = 1 - self.turn

    def opponent(self, player: str) -> str:
        """
        return the other player (not the given one)
        """
        return self.players[1 - self.players.index(player)]

    def commit_move(self, move_str: str) -> bool:
        """
        if the move is legal, push it to the board and update the turn.
        """
        move: chess.Move = chess.Move.from_uci(move_str)
        if move not in self.board.legal_moves:
            return False
        self.board.push(move)
        self.update_turn()
        return True

    def stop_clock(self) -> None:
        """
        stop the clock of the current player
        """
        self.clocks[self.turn].stop()

    def start_clock(self) -> None:
        """
        start the clock of the current player
        """
        self.clocks[self.turn].start()

    def is_timeout(self) -> bool:
        """
        true if the current player is out of time
        """
        return self.clocks[self.turn].is_timeout()

    def timeout_player(self) -> str:
        """
        return the player that is out of time
        """
        return self.players[self.turn]

    def get_time_left(self, player: str) -> float:
        """
        return the time left for the given player
        """
        return self.clocks[self.players.index(player)].get_time_left()

    def last_move(self) -> str:
        """
        return the last move in uci format
        """
        return str(self.board.peek())

    def color(self, player: str) -> int:
        """
        return the color of the given player
        """
        return self.players.index(player)

    def is_game_over(self) -> bool:
        """
        true if the game is over
        """
        return self.board.result() != '*'

    def get_game_results(self) -> dict[str, int]:
        """
        return the game results as a dictionary
        """
        resault = [DRAW, DRAW]
        resault_d = {'1': WON, '0': LOST, '1/2': DRAW}
        if self.is_game_over():
            resault = [resault_d[x] for x in self.board.result().split('-')]
        return {self.players[0]: resault[0], self.players[1]: resault[1]}

    def is_players_turn(self, player: str) -> bool:
        """
        true if it is the given player's turn
        """
        return self.players[self.turn] == player

        
    def fen(self) -> str:
        """
        return the fen of the current board
        """
        return self.board.fen()

    def close(self) -> None:
        """
        mark the room as closed
        """
        self.closed = True


class EngineRoom(ChessRoom):
    """
    a chess room with a stockfish engine against a player
    """

    def __init__(self, player1: str, level: int = 10, clock: str=DEAFULT_CLOCK):
        super().__init__(player1, 'stockfish', clock)
        self.stockfish = Stockfish(STOCKFISH_W_PATH if platform.system() == 'Windows' else STOCKFISH_L_PATH)
        self.stockfish.set_skill_level(level)

    def make_stockfish_move(self) -> str:
        """
        calculate the best move for the stockfish engine and commit it to the board.
        """
        self.start_clock()
        self.stockfish.set_fen_position(self.fen())
        move = self.stockfish.get_best_move()
        self.commit_move(move) # type: ignore
        return move # type: ignore


class PlayerRoom(ChessRoom):

    """
    a chess room with two players
    """

    def __init__(self, player1: str, player2: str, clock: str=DEAFULT_CLOCK):
        super().__init__(player1, player2, clock)


CHESS_ROOMS: set[PlayerRoom | EngineRoom] = set()