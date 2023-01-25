import re
import chess.engine
import chess
from random import shuffle
import time

START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
WHITE = 0
BLACK = 1


class ChessClock(object):
    def __init__(self, time_limit:float=10, addition: float=0) -> None:
        self.time_left: float = time_limit * 60
        self.start_time: float|None = None
        self.addition: float = addition

    def start(self) -> None:
        self.start_time = time.time()
    
    def get_time_used(self) -> float:
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def stop(self) -> None:
        self.time_left -= self.get_time_used()
        self.start_time = None
        self.time_left += self.addition
    
    def get_time_left(self) -> float:
        return self.time_left - self.get_time_used()

    def is_timeout(self) -> bool:
        return not self.get_time_left() > 0


class ChessRoom:
    def __init__(self, player1:str, player2:str='stockfish', time_limit:int=10, bonus_time:int=0, fen:str=START_FEN, level:int=10):
        self.players: list[str] = [player1, player2]
        self.clocks: list[ChessClock] = [ChessClock(time_limit, bonus_time), ChessClock(time_limit, bonus_time)]
        shuffle(self.players)
        self.board: chess.Board = chess.Board(fen)
        self.turn: int = 0
        self.level: int = level
        self.closed: bool = False
        self.pvp: bool = not (player2 == 'stockfish')

    def __len__(self) -> int:
        return len(self.board.move_stack)

    def __str__(self) -> str:
        return self.fen()

    def __repr__(self) -> str:
        return f'chess.Board({self.fen()})'


    def update_turn(self) -> None:
        # flip turn from 1 to 0 or 0 to 1
        self.stop_clock()
        self.turn = int(not self.turn)

    def opponent(self, player: str) -> str:
        if player == self.players[0]:
            return self.players[1]
        return self.players[0]
    
    def commit_move(self, move_str: str) -> bool:
        regex = r'^[a-h][1-8][a-h][1-8][q,r,b,n]?$'
        if not re.fullmatch(regex, move_str):
            return False
        move: chess.Move = chess.Move.from_uci(move_str)
        if not move in self.board.legal_moves:
            return False
        self.board.push(move)
        self.update_turn()
        return True

    def stop_clock(self) -> None:
        self.clocks[self.turn].stop()
    
    def start_clock(self) -> None:
        self.clocks[self.turn].start()

    def is_timeout(self) -> bool:
        return self.clocks[self.turn].is_timeout()

    def timeout_player(self) -> str:
        return self.players[self.turn]

    def last_move(self) -> str:
        return str(self.board.peek())

    def color(self, player: str) -> int:
        return self.players.index(player)

    def is_game_over(self) -> bool:
        return self.board.result() != '*'

    def get_game_results(self) -> dict:
        resault = ['0.5', '0.5']
        if self.is_game_over():
            resault = self.board.result().split('-')
        return {self.players[0]: float(resault[0]), self.players[1]: float(resault[1])}

    def is_players_turn(self, player: str) -> bool:
        return self.players[self.turn] == player

    def fen(self) -> str:
        return self.board.fen()

    def close(self) -> None:
        self.closed = True


def main():
    pass

if __name__ == '__main__':
    main()
