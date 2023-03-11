import requests
import asyncio
from aiohttp import web
import socketio
import chess
sio: socketio.AsyncClient = socketio.AsyncClient()
url: str = 'http://localhost:5678'
board = chess.Board()


def print_board(reverse=False):
    # print the board with the numbers and letters
    board_list = str(board).splitlines()
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
    board.push_san(move)
    print_board()
    
async def test_connection():
    r = requests.get(url)
    assert r.status_code == 200
    
    payload = dict(username='chaim', password='test1234')
    r = requests.post(url + '/validate', json=payload)
    assert r.status_code == 200
    assert 'Set-Cookie' in r.headers
    cookie = r.headers['Set-Cookie'].split(';')[0].split('=')[1]
    assert len(cookie) == 64
    
    await sio.connect(url, auth={'token': cookie}, wait_timeout=10)
    print('connected')


async def get_cookie(user='chaim', pw='test1234'):
    payload = dict(username=user, password=pw)
    r = requests.post(url + '/validate', json=payload)
    print(r.json()['status'])
    if r.json()['status'] != 200:
        return None
    cookie = r.headers['Set-Cookie'].split(';')[0].split('=')[1]
    return cookie


async def connect():
    cookie = await get_cookie()
    await sio.connect(url, auth={'token': cookie}, wait_timeout=10)
    print('connected')
    
@sio.event
async def user_data(data):
    print(data)

@sio.event
async def game_started(data):
    board.reset()
    print_board()
    if data == 'white':
        print('you are white')
        await get_send_move()

@sio.event
async def opponent_move(data):
    move = data['move']
    print('opponent move:', move)
    commit_move(move)
    await get_send_move()
    
async def get_send_move():
    move = input('enter move: ')
    while not board.is_legal(chess.Move.from_uci(move)):
        print('illegal move')
        move = input('enter move: ')
    commit_move(move)
    await sio.emit('my_move', {'move': move})
    
async def start_game():
    await sio.emit('start_game', dict(game_mode='engine', level=1))


async def try_injection():
    with open('src/sqli.txt', 'r') as f:
        for line in f.readlines():
            await get_cookie(user=line.strip(), pw='test1234')
            
            
async def main():
    try:
        await connect()
        await start_game()
        await sio.wait()
    except KeyboardInterrupt:
        print('disconnecting')
        await sio.disconnect()
    
    
if __name__ == '__main__':
    asyncio.run(try_injection())
    