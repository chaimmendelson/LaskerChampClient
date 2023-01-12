import socketio
from aiohttp import web
import secrets
import re as re
from stockfish import Stockfish
import hashlib
from chess_rooms import *
from handle_database import *
PATH = 'src/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe'
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
WAITING_ROOM = []
CHESS_ROOMS:list[ChessRoom] = []
COOKIE_NAME = 'chess-cookie'
class Clients():
    def __init__(self, username, sid):
        self.username = username
        self.sid = sid

CLIENTS: list[Clients] = []


def get_sid(username) -> str:
    for client in CLIENTS:
        if client.username == username:
            return client.sid

def get_username(sid) -> str:
    for client in CLIENTS:
        if client.sid == sid:
            return client.username


def is_connected(username) -> bool:
    for client in CLIENTS:
        if client.username == username:
            return True
    return False


def get_stockfish_move(fen=START_FEN):
    stockfish = Stockfish(PATH)
    stockfish.set_fen_position(fen)
    return stockfish.get_best_move()


async def task(sid):
    await sio.sleep(5)
    resault = await sio.call('mult', {'numbers': [2, 3]}, to=sid)
    print(resault)

def add_room(player1:str, player2:str='stockfish', time_limit:int=10, bonus_time:int=0, fen:str=START_FEN, level:int=10) -> None:
    global CHESS_ROOMS
    CHESS_ROOMS.append(
    ChessRoom(
        player1=player1,
        player2=player2,
        time_limit=time_limit,
        bonus_time=bonus_time,
        fen=fen,
        level=int(level)
        )
    )


def is_in_room(player:str) -> bool:
    return get_room(player) != None


def get_room(player:str) -> ChessRoom|None:
    for room in CHESS_ROOMS:
        if player in room.players:
            return room
    return None


def close_room(player:str) -> None:
    global CHESS_ROOMS
    CHESS_ROOMS.remove(get_room(player))

async def game_page(request: web.Request):
    """Serve the client-side application."""
    cookies = request.cookies
    if COOKIE_NAME in cookies:
        cookie = cookies[COOKIE_NAME]
        if does_exist(COOKIE, cookie):
            if not is_connected(get_username_by_cookie(cookie)):
                with open('src/pages/client.html') as f:
                    return web.Response(text=f.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})

async def login(request: web.Request):
    """Serve the client-side application."""
    with open('src/pages/login.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.event
async def connect(sid, environ, auth):
    if auth:
        if 'token' in auth:
            token = auth['token']
            if does_exist(COOKIE, token):
                username = get_username_by_cookie(token)
                CLIENTS.append(Clients(username, sid))
                print("connect ", sid)
                return True
    return False
    # sio.start_background_task(task, sid)

@sio.event
async def start_game(sid, data):
    username = get_username(sid)
    if is_in_room(username):
        return False
    if data.get('stockfish'):
        add_room(player1=username)
        room = get_room(username)
        white_player = room.players[0]
        if white_player == username:
            color = 'white'
        else:
            color = 'black'
        await sio.emit('game_started', color, to=sid)
        if color == 'black':
            await send_stockfish_move(sid)
    else:
        if len(WAITING_ROOM):
            player1 = username
            player2 = WAITING_ROOM[0]
            add_room(player1=player1, player2=player2, time_limit=0.5)
            room = get_room(username)
            WAITING_ROOM.pop(0)
            await sio.emit('game_started', 'white', to=get_sid(room.players[0]))
            await sio.emit('game_started', 'black', to=get_sid(room.players[1]))
        else:
            WAITING_ROOM.append(username)
            return 'searching for opponent'

@sio.event
async def send_stockfish_move(sid):
    room = get_room(get_username(sid))
    room.start_clock()
    move = str(get_stockfish_move(str(room)))
    room.commit_move(move)
    move_d = {'move': move}
    move_d['from'] = move[:2]
    move_d['to'] = move[2:4]
    if len(move) == 5:
        move_d['promotion'] = move[4]
    await send_move_to_opponent(sid, move_d)


@sio.event
async def my_move(sid, data):
    username = get_username(sid)
    room = get_room(username)
    opponent = room.opponent(username)
    move = data.get('move')
    if not validate_move(move):
        return False
    move_d = validate_move(move)
    move_d['move'] = move
    room.commit_move(move)
    if opponent == 'stockfish':
        await send_stockfish_move(sid)
    # print('sending move to opponent')
    else:
        await send_move_to_opponent(opponent, move_d)



async def send_move_to_opponent(sid, move_d):
    username = get_username(sid)
    room = get_room(username)
    resault_d = {0: 'lost', 1: 'won', -1: 'tie'}
    await sio.emit('opponent_move', move_d, to=sid)
    room.start_clock()
    if not room.is_game_over():
        return
    player_resault = room.get_game_results()
    opponent = room.opponent(username)
    await sio.emit('game_over', resault_d[player_resault[username]], to=sid)
    if room.pvp:
        await sio.emit('game_over', resault_d[player_resault[opponent]], to=get_sid(opponent))
    close_room(username)


@sio.event
async def quit_game(sid):
    await handle_quit(get_username(sid))


@sio.event
async def disconnect(sid):
    global CLIENTS, WAITING_ROOM   
    print('disconnect ', sid)
    username = get_username(sid)
    for client in CLIENTS.copy():
        if client.username == username:
            CLIENTS.remove(client)
            break
    print(f"removing client ({username})")
    if username in WAITING_ROOM:
        WAITING_ROOM.remove(username)
    if is_in_room(username):
        await handle_quit(username)


async def handle_quit(username):
    opponent = get_room(username).opponent(username)
    close_room(username)
    if opponent !='stockfish':
        print(f'sending quit message to opponent ({opponent})')
        await sio.emit("opponent_quit", to=get_sid(opponent))


def validate_move(move) -> dict|None:
    if isinstance(move, str):
        move = move.lower()
        move_d = {}
        regex = r'^[a-h][1-8][a-h][1-8][q,r,b,n]?$'
        if not re.fullmatch(regex, move):
            return None
        move_d["from"] = move[:2]
        move_d["to"] = move[2:4]
        if len(move) == 5:
            move_d["promotion"] = move[4]
        return move_d
    if isinstance(move, dict):
        move_l = ['from', 'to']
        move_l2 = move_l.copy().append("promotion")
        if move_l == move.keys() or move_l2 == move:
            return move
    return None


def check_for_timeout():
    for room in CHESS_ROOMS:
        if room.is_timeout():
            handle_quit(room.timeout_player())
            

async def login_validation(request: web.Request):
    headers = request.headers
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data:
            username = data['username']
            password = data['password']
            if does_exist(USERNAME, username):
                if check_password(username, password):
                    if not is_connected(username):
                        response = web.json_response({'status': 'ok'})
                        response.set_cookie(COOKIE_NAME, get_value(username, COOKIE))
                        return response
    return web.json_response({'status': 'error'})

app.add_routes([web.get('/', game_page),
                web.get('/login', login),
                web.post('/validate', login_validation),
                web.static('/scripts', 'src/scripts'),
                web.static('/styles', 'src/styles'),
                web.static('/images', 'src/images')])

if __name__ == '__main__':
    web.run_app(app, port=5678)