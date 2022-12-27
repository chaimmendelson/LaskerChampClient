import socketio
from aiohttp import web
import secrets
import re as re
from stockfish import Stockfish
import chess_rooms as rooms
PATH = 'src/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe'
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
WAITING_ROOM = []
COOKIE_NAME = 'chess-cookie'
class Clients():
    def __init__(self, username, cookie, sid=None):
        self.username = username
        self.cookie = cookie
        self.sid = sid
    
    def set_sid(self, sid):
        self.sid = sid

CLIENTS: list[Clients] = []


def get_client(sid) -> Clients|None:
    for client in CLIENTS:
        if client.sid == sid:
            return client
    return None


def does_cookie_exist(cookie):
    for client in CLIENTS:
        if client.cookie == cookie:
            return True
    return False

def create_cookie():
    cookie = secrets.token_hex(16)
    while does_cookie_exist(cookie):
        cookie = secrets.token_hex(16)
    return cookie


def get_stockfish_move(fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
    stockfish = Stockfish(PATH)
    stockfish.set_fen_position(fen)
    return stockfish.get_best_move()


async def task(sid):
    await sio.sleep(5)
    resault = await sio.call('mult', {'numbers': [2, 3]}, to=sid)
    print(resault)


async def game_page(request: web.Request):
    """Serve the client-side application."""
    print(request)
    cookies = request.cookies
    if COOKIE_NAME in cookies:
        cookie = cookies[COOKIE_NAME]
        if does_cookie_exist(cookie):
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
            if does_cookie_exist(token):
                for client in CLIENTS:
                    if client.cookie == token:
                        client.set_sid(sid)
                        print("connect ", sid)
                        return True
    return False
    # sio.start_background_task(task, sid)

@sio.event
async def start_game(sid, data):
    if rooms.is_in_room(sid):
        return False
    if data.get('type') == 'stockfish':
        rooms.add_room(player1=sid)
        white_player = rooms.get_white_player(sid)
        if white_player == sid:
            color = 'white'
        else:
            color = 'black'
        await sio.emit('game_started', color, to=sid)
        if color == 'black':
            await send_stockfish_move(sid)
    else:
        if len(WAITING_ROOM):
            player1 = sid
            player2 = WAITING_ROOM[0]
            rooms.add_room(player1=player1, player2=player2)
            WAITING_ROOM.pop(0)
            white_player = rooms.get_white_player(player1)
            black_player = rooms.get_black_player(player1)
            await sio.emit('game_started', 'white', to=white_player)
            await sio.emit('game_started', 'black', to=black_player)
        else:
            WAITING_ROOM.append(sid)
            return 'searching for opponent'

@sio.event
async def send_stockfish_move(sid):
    move = str(get_stockfish_move(rooms.get_fen(sid)))
    rooms.commit_move(sid, move)
    move_d = {'move': move}
    move_d['from'] = move[:2]
    move_d['to'] = move[2:4]
    if len(move) == 5:
        move_d['promotion'] = move[4]
    await send_move_to_opponent(sid, move_d)


@sio.event
async def my_move(sid, data):
    opponent = rooms.get_opponent(sid)
    move = data.get('move')
    if not validate_move(move):
        return False
    move_d = validate_move(move)
    move_d['move'] = move
    rooms.commit_move(sid, move)
    if opponent == 'stockfish':
        await send_stockfish_move(sid)
    # print('sending move to opponent')
    else:
        await send_move_to_opponent(opponent, move_d)



async def send_move_to_opponent(sid, move_d):
    resault_d = {0: 'lost', 1: 'won', -1: 'tie'}
    await sio.emit('opponent_move', move_d, to=sid)
    if not rooms.is_game_over(sid):
        return
    player_resault = rooms.get_game_results(sid)
    await sio.emit('game_over', resault_d[player_resault], to=sid)
    if rooms.is_pvp_room(sid):
        opponent = rooms.get_opponent(sid)
        await sio.emit('game_over', resault_d[player_resault], to=opponent)
    rooms.close_room(sid)

@sio.event
async def disconnect(sid):
    global CLIENTS   
    print('disconnect ', sid)
    client = get_client(sid=sid)
    print("searching for client")
    if client:
        print("client found")
        CLIENTS.remove(client)
        print("removing client")
        if rooms.is_in_room(sid):
            opponent = rooms.get_opponent(sid)
            rooms.close_room(sid)
            if opponent !='stockfish':
                print("sending quit message")
                await sio.emit("opponent_quit", to=opponent)


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


async def login_validation(request: web.Request):
    headers = request.headers
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data:
            if data['username'] == 'test' and data['password'] == 'test':
                cookie = create_cookie()
                CLIENTS.append(Clients(data['username'], cookie))
                response = web.json_response({'status': 'ok'})
                response.set_cookie(COOKIE_NAME, cookie)
                print(cookie)
                return response
    return web.json_response({'status': 'error'})

app.add_routes([web.get('/', game_page),
                web.get('/login', login),
                web.post('/validate', login_validation),
                web.static('/scripts', 'src/scripts'),
                web.static('/styles', 'src/styles'),
                web.static('/images', 'src/images')])

if __name__ == '__main__':
    web.run_app(app, port=8000)