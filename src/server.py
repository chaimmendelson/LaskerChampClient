import socketio
from aiohttp import web
import secrets
import random
from stockfish import Stockfish
PATH = 'src/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe'
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
CLIENTS = []
COOKIE_NAME = 'chess-cookie'
class Clients():
    def __init__(self, username, cookie, sid=None):
        self.username = username
        self.cookie = cookie
        self.sid = sid
    
    def set_sid(self, sid):
        self.sid = sid

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


def get_move(fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
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
            with open('src/client.html') as f:
                return web.Response(text=f.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})

async def login(request: web.Request):
    """Serve the client-side application."""
    with open('src/login.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.event
async def connect(sid, environ, auth):
    if auth:
        if 'token' in auth:
            token = auth['token']
            print(token)
            if does_cookie_exist(token):
                for client in CLIENTS:
                    if client.cookie == token:
                        client.set_sid(sid)
                        print("connect ", sid)
                        return True
    return False
    # sio.start_background_task(task, sid)

@sio.event
async def start_game(sid):
    color = random.choice(['white', 'black'])
    return {'color': color}

@sio.event
async def get_opponent_move(sid, data):
    move = str(get_move(data.get('fen')))
    move_d = {'move': move}
    move_d['from'] = move[:2]
    move_d['to'] = move[2:4]
    if len(move) == 5:
        move_d['promotion'] = move[4]
    await sio.emit('opponent_move', move_d, to=sid)


@sio.event
async def disconnect(sid):
    global CLIENTS   
    print('disconnect ', sid)
    if sid in CLIENTS:
        CLIENTS.remove(sid)


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