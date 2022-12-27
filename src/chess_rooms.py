import re
import chess.engine
import chess
from random import shuffle
from stockfish import Stockfish
import threading

import os_values

START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
WHITE = 0
BLACK = 1


class ChessRoom:

    def __init__(self, player1, player2='stockfish', fen=START_FEN, engine_level=10):
        self.players:list = [player1, player2]
        shuffle(self.players)
        self.board : chess.Board = chess.Board(fen)
        self.turn:str = self.players[0]
        self.waiting:bool = False
        self.level:int = engine_level

    def __len__(self) -> int:
        return len(self.board.move_stack)

    def __str__(self) -> str:
        return self.board.fen()

    def __repr__(self) -> str:
        return f'chess.Board({self.board.fen()})'

    def update_turn(self) -> None:
        if self.turn == self.players[0]:
            self.turn = self.players[1]
        else:
            self.turn = self.players[0]
        self.update_status()

    def update_status(self) -> None:
        self.waiting = not self.waiting


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
    return player == get_room(player).turn


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


def add_room(player1, player2='', fen=START_FEN, level=10) -> None:
    global CHESS_ROOMS
    if player2:
        CHESS_ROOMS.append(ChessRoom(player1, player2, fen))
    else:
        CHESS_ROOMS.append(ChessRoom(player1, 'stockfish', fen, int(level)))


def is_in_room(player) -> bool:
    for room in CHESS_ROOMS:
        if player in room.players:
            return True
    return False


def get_room(player) -> ChessRoom|None:
    for room in CHESS_ROOMS:
        if player in room.players:
            return room
    return None


def close_room(player) -> None:
    global CHESS_ROOMS
    CHESS_ROOMS.remove(get_room(player))


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
