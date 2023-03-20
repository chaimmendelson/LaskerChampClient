import chess
import chess.engine as engine
import sys
import os
import math
from stockfish import Stockfish
sys.path.append('./')
from src.chess_rooms import NEPO_L_PATH, STOCKFISH_L_PATH

board = chess.Board()
nepo_turn = True
stockfish = Stockfish(STOCKFISH_L_PATH)
ENGINE: engine.SimpleEngine = None
ascii_chess_pieces = dict(zip('PNBRQKpnbrqk', '♟♞♝♜♛♚♙♘♗♖♕♔'))

def connect_loop():
    global ENGINE
    try:
        ENGINE = engine.SimpleEngine.popen_uci(NEPO_L_PATH)
    except Exception:
        connect_loop()
    finally:
        return
    
def connect_engine():
    print('connecting engine...')
    connect_loop()
    print('engine connected')
    
def print_board(reverse=False):
    # print the board with the numbers and letters
    board_list = str(board).splitlines()
    for i in range(8):
        board_list[i] = ''.join([ascii_chess_pieces.get(c, c) for c in board_list[i]])
    letters = 'abcdefgh' if not reverse else 'hgfedcba'
    line = '  +' + '-' * 17 + '+'
    print(line)
    for i in range(8):
        if not reverse:
            print(f'{8-i} | {board_list[i]} |')
        else:
            print(f'{i + 1} | {board_list[7 - i][::-1]} |')
    print(line)
    print(f"{4 * ' '}{' '.join(letters)}")
    

def custom_print():
    os.system('clear')
    print(f"stockfish: {'thinking ...' if not nepo_turn else 'waiting'}")
    print_board()
    print(f"nepo: {'thinking ...' if nepo_turn else 'waiting'}")
    print(f"{board.fullmove_number} moves passed")

def run_test(min_elo: int=0, max_elo: int=3000):
    global nepo_turn
    half_elo = math.floor((min_elo + max_elo) / 2)
    print('searching for nepo elo...')
    while True:
        # reset data
        board.reset()
        stockfish.set_fen_position(board.fen())
        stockfish.set_elo_rating(half_elo)
        print(f"trying {half_elo}")
        while not board.is_game_over():
            move = ENGINE.play(board, engine.Limit(20)).move if nepo_turn else chess.Move.from_uci(stockfish.get_best_move())
            board.push(move)
            stockfish.make_moves_from_current_position([move])
            nepo_turn = not nepo_turn
        print(board.result())
        if board.result() != '0-1':
            min_elo = half_elo
        else:
            max_elo = half_elo
        half_elo = math.floor((min_elo + max_elo) / 2)
        if max_elo - min_elo < 10:
            break
    print(f"nepo elo: {half_elo}")
    
if __name__ == '__main__':
    connect_loop()
    run_test()