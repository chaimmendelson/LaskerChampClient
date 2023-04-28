import chess
import chess.engine as engine
import sys
import os
from stockfish import Stockfish
sys.path.append('./')
from src.chess_rooms import NEPO_L_PATH, STOCKFISH_L_PATH

stockfish = Stockfish(STOCKFISH_L_PATH)
ENGINE: engine.SimpleEngine
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
    

def test_fen(fen: str):
    board = chess.Board(fen)
    stockfish.set_fen_position(fen)
    stockfish_move = stockfish.get_best_move()
    nepo_move = ENGINE.play(board, engine.Limit(20)).move
    print(f"stockfish: {stockfish_move}")
    print(f"nepo: {nepo_move}")

def test_eval():
    #ask stockfish to evaluate the given fen
    print(stockfish.get_fen_position())
    moves = ['a2a3', 'a7a6', 'a3a4', 'a6a5']
    for move in moves:
        print(f"stockfish eval: {stockfish.get_evaluation()}") # get the evaluation of the current position
        stockfish.make_moves_from_current_position([move])
    
def convert_pgn_to_fen(pgn: list) -> str:
    """
    convert the given pgn to fen.
    """
    board = chess.Board()
    for move in pgn:
        board.push_san(move)
    return board.fen()

def stockfish_vs_nepo():
    board = chess.Board()
    stockfish_a = engine.SimpleEngine.popen_uci(STOCKFISH_L_PATH)
    stockfish = Stockfish(STOCKFISH_L_PATH)
    stockfish.set_skill_level(5)
    while not board.is_game_over():
        nepo_move = ENGINE.play(board, engine.Limit(20)).move
        print(f"nepo: {nepo_move}")
        board.push(nepo_move)
        analyse(board)
        stockfish.make_moves_from_current_position([nepo_move])
        
        stockfish_move = chess.Move.from_uci(stockfish.get_best_move())
        print(f"stockfish: {stockfish_move}")
        board.push(stockfish_move)
        analyse(board)
        stockfish.make_moves_from_current_position([stockfish_move])


def analyse(board: chess.Board, depth: int = 20):
    """
    analyse the given board with the given depth.
    """
    en = engine.SimpleEngine.popen_uci(STOCKFISH_L_PATH)
    score = en.analyse(board, engine.Limit(depth=depth))['score'].white().score()
    print(score)
    en.quit()
    
    
def main():
    connect_engine()
    #stockfish_vs_nepo()
    # terminate engine
    stockfish_vs_nepo()
    os.system(f"kill -9 $(ps aux | grep {NEPO_L_PATH} | awk '{{print $2}}')")
if __name__ == '__main__':
    main()