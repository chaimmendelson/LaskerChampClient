import re
import chess.engine
import chess
from random import shuffle
from stockfish import Stockfish
import threading
import time

import os_values

START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
WHITE = 0
BLACK = 1


class ChessClock(object):
    def __init__(self, time_limit=10, addition=0):
        self.time_left = time_limit * 60
        self.start_time = None
        self.addition = addition

    def start(self):
        self.start_time = time.time()
    
    def get_time_used(self):
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def stop(self):
        print(type(self.time_left), self.time_left)
        self.time_left -= self.get_time_used()
        self.start_time = None
        self.time_left += self.addition
    
    def get_time_left(self):
        return self.time_left - self.get_time_used()

    def is_time_over(self):
        return not self.get_time_left() > 0


class ChessRoom:
    def __init__(self, player1, player2='stockfish', time_limit=10, bonus_time=0, fen=START_FEN, level=10):
        self.players:tuple(str) = [player1, player2]
        self.clocks:tuple(ChessClock) = (ChessClock(time_limit, bonus_time), ChessClock(time_limit, bonus_time))
        shuffle(self.players)
        self.board : chess.Board = chess.Board(fen)
        self.turn:str = 0
        self.level:int = level
        self.closed = False

    def __len__(self) -> int:
        return len(self.board.move_stack)

    def __str__(self) -> str:
        return self.board.fen()

    def __repr__(self) -> str:
        return f'chess.Board({self.board.fen()})'

    def update_turn(self) -> None:
        # flip turn from 1 to 0 or 0 to 1
        self.stop_clock()
        self.turn = int(not self.turn)
    
    def stop_clock(self) -> None:
        self.clocks[self.turn].stop()
    
    def start_clock(self) -> None:
        self.clocks[self.turn].start()


CHESS_ROOMS:list[ChessRoom] = []


def is_pvp_room(player) -> bool:
    return 'stockfish' not in get_room(player).players


def get_fen(player) -> str:
    return str(get_room(player))


def get_white_player(player) -> str:
    return get_room(player).players[0]

def get_black_player(player) -> str:
    return get_room(player).players[1]


def get_opponent(player) -> str:
    players = get_room(player).players
    if player == players[0]:
        return players[1]
    return players[0]


def get_last_move(player) -> str:
    board = get_room(player).board
    move = board.pop()
    board.push(move)
    return str(move)


def is_client_turn(player) -> bool:
    room = get_room(player)
    return room.players.index(player) == room.turn


def color(player) -> int:
    return get_room(player).players.index(player)


def is_game_over(player) -> bool:
    return get_room(player).board.result() != '*'


def get_game_results(player) -> int|None:
    room = get_room(player)
    if is_game_over(player):
        result = room.board.result().split('-')
        if result[0] == '1/2':
            return -1
        if color(player):
            return int(result[1])
        return int(result[0])
    return None


def commit_move(player, move) -> bool:
    regex = r'^[a-h][1-8][a-h][1-8][q,r,b,n]?$'
    if not re.fullmatch(regex, move):
        return False
    room = get_room(player)
    if not chess.Move.from_uci(move) in room.board.legal_moves:
        return False
    # if not is_client_turn(player):
    #     return False
    room.board.push(chess.Move.from_uci(move))
    room.update_turn()
    return True


def add_room(player1, player2='stockfish', time_limit=10, bonus_time=0, fen=START_FEN, level=10) -> None:
    global CHESS_ROOMS
    CHESS_ROOMS.append(ChessRoom(player1, player2, time_limit=time_limit, bonus_time=bonus_time, fen=fen, level=int(level)))


def is_in_room(player) -> bool:
    return get_room(player) != None


def get_room(player) -> ChessRoom|None:
    for room in CHESS_ROOMS:
        if player in room.players:
            return room
    return None


def close_room(player) -> None:
    global CHESS_ROOMS
    CHESS_ROOMS.remove(get_room(player))


def start_clock(player) -> None:
    get_room(player).start_clock()


def get_engine_move(player) -> str|None:
    try:
        stockfish = Stockfish(os_values.get_stockfish_path())
        room = get_room(player)
        fen = str(get_room(player))
        stockfish.set_skill_level(room.level)
        stockfish.set_fen_position(fen)
        move = stockfish.get_best_move()
        room.board.push(chess.Move.from_uci(move))
        room.update_turn()
        return move
    except:
        return None


def update_status(player) -> None:
    get_room(player).update_status()


def is_waiting(player) -> bool:
    return get_room(player).waiting


def test():
    print("")


def main():
    test()

if __name__ == '__main__':
    main()
