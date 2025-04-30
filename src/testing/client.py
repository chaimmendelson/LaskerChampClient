import requests
import asyncio
import socketio
import os
import stat
import chess
import chess.engine
from src.models.chess_room import NEPO_L_PATH

os.chmod(NEPO_L_PATH, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
     
sio: socketio.AsyncClient = socketio.AsyncClient()
URL: str = 'http://localhost:5678'
BOARD = chess.Board()
ENGINE: chess.engine.SimpleEngine = None
LEVEL = 1

def connect_loop():
    global ENGINE
    try:
        ENGINE = chess.engine.SimpleEngine.popen_uci(NEPO_L_PATH)
    except Exception:
        connect_loop()
    finally:
        return
    
def connect_engine():
    print('connecting engine...')
    connect_loop()
    print('engine connected')
        
        
def test_nepo():
    global BOARD
    BOARD = chess.Board()
    print('game started')
    for i in range(100):
        if BOARD.is_game_over():
            break
        best_move = get_best_nepo()
        BOARD.push(best_move)
    print(BOARD.result())
            

def get_best_nepo():
    global ENGINE
    try:
        return ENGINE.play(BOARD, chess.engine.Limit(time=600)).move
    except chess.engine.EngineTerminatedError:
        connect_engine()
        return get_best_nepo()


def print_board(reverse=False):
    # print the board with the numbers and letters
    board_list = str(BOARD).splitlines()
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

def commit_move(move):
    global BOARD
    BOARD.push_san(move)
    #print_board()
    
async def test_connection():
    r = requests.get(URL)
    assert r.status_code == 200
    
    payload = dict(username='chaim', password='test1234')
    r = requests.post(URL + '/validate', json=payload)
    assert r.status_code == 200
    assert 'Set-Cookie' in r.headers
    cookie = r.headers['Set-Cookie'].split(';')[0].split('=')[1]
    assert len(cookie) == 64
    
    await sio.connect(URL, auth={'token': cookie}, wait_timeout=10)
    print('connected')


async def get_cookie(user='chaim', pw='test1234'):
    payload = dict(username=user, password=pw)
    r = requests.post(URL + '/validate', json=payload)
    print(r.json()['status'])
    if r.json()['status'] != 200:
        raise Exception('connection failed')
    cookie = r.headers['Set-Cookie'].split(';')[0].split('=')[1]
    return cookie


async def connect():
    cookie = await get_cookie()
    await sio.connect(URL, auth={'token': cookie}, wait_timeout=10)
    print('connected to server')
    
@sio.event
async def user_data(data):
    #print(data)
    pass

@sio.event
async def game_started(data):
    BOARD.reset()
    print(f'game started, you are the {data} player, playing against stockfish level {LEVEL - 1}')
    if data == 'white':
        await get_send_move()

@sio.event
async def opponent_move(data):
    move = data['move']
    #print('opponent move:', move)
    print(move)
    commit_move(move)
    if not BOARD.is_game_over() or 'game_over' in data:
        await get_send_move()

@sio.event
async def game_over(data):
    result_d = {1: 'you won', 0.5: 'its a tie', 0: 'you lost'}
    print(f'game over, {result_d[data]}')
    await start_game()
    
async def get_send_move():
    # move = input('enter move: ')
    # while not board.is_legal(chess.Move.from_uci(move)):
    #     print('illegal move')
    #     move = input('enter move: ')
    #print(board.fen())
    move = str(get_best_nepo())
    #print('my move:', move)
    print(move)
    commit_move(move)
    await sio.emit('my_move', {'move': move})
    
async def start_game():
    global LEVEL
    await sio.emit('start_game', dict(game_mode='engine', level=LEVEL))
    if LEVEL < 20:
        LEVEL += 1


async def try_injection():
    with open('src/sqli.txt', 'r') as f:
        for line in f.readlines():
            await get_cookie(user=line.strip(), pw='test1234')
            
            
async def main():
    try:
        connect_engine()
        await connect()
        await start_game()
        await sio.wait()
    except KeyboardInterrupt:
        pass
    except Exception:
        pass
    print('disconnecting')
    await sio.disconnect()
    os.kill(os.getpid(), 9)
    
    
if __name__ == '__main__':
    asyncio.run(main())