import os
import stat
import chess
import chess.engine
from chess_rooms import NEPO_L_PATH, STOCKFISH_L_PATH

#os.chmod(NEPO_L_PATH, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
# with chess.engine.SimpleEngine.popen_uci(NEPO_L_PATH) as engine:
#     board = chess.Board()
#     for i in range(100):
#         best_move = engine.play(board, chess.engine.Limit(time=10)).move
#         board.push(best_move)
#         os.system('clear')
#         print(board)

print('hjvisvo jneiniwd'.isalnum())
        