import asyncio
import threading
import socketio
from aiohttp import web
import re as re
from stockfish import Stockfish
from chess_rooms import *
from handle_database import *
PATH = 'src/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe'
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
WAITING_ROOM = []
CHESS_ROOMS:list[ChessRoom] = []
COOKIE_NAME = 'chess-cookie'
STOP_THREAD = False
class Clients():
    def __init__(self, username: str, sid: str):
        self.username = username
        self.sid = sid

CLIENTS: list[Clients] = []


def get_sid(username: str) -> str:
    """
    returns the sid of the given username.
    """
    return [client.sid for client in CLIENTS if client.username == username][0]

def get_username(sid: str) -> str:
    """
    returns the username of the given sid.
    """
    return [client.username for client in CLIENTS if client.sid == sid][0]


def get_opponent(username: str) -> str:
    """
    returns the opponent of the given username.
    """
    room = get_room(username)
    return room.opponent(username)


def is_connected(username:str) -> bool:
    """
    returns True if the given username is connected to the server.
    """
    return username in [client.username for client in CLIENTS]


def get_stockfish_move(fen=START_FEN):
    """
    returns the best move for the given fen position.
    """
    stockfish = Stockfish(PATH)
    stockfish.set_fen_position(fen)
    return stockfish.get_best_move()


def add_room(player1:str, player2:str='stockfish', time_limit:int=10, bonus_time:int=0, fen:str=START_FEN, level:int=10) -> None:
    global CHESS_ROOMS
    CHESS_ROOMS.append(ChessRoom(
        player1=player1,
        player2=player2,
        time_limit=time_limit,
        bonus_time=bonus_time,
        fen=fen,
        level=int(level)
        )
    )
    

def is_in_room(player:str) -> bool:
    """
    returns True if the given player is in a room.
    """
    for room in CHESS_ROOMS:
        if player in room.players:
            return True
    return False


def get_room(player:str) -> ChessRoom:
    """
    this function returns a ChessRoom object for the given player.
    """
    return [room for room in CHESS_ROOMS if player in room.players][0]
    
    
def close_room(player:str) -> None:
    """
    this function removes the room of the given player from the CHESS_ROOMS list.
    """
    global CHESS_ROOMS
    CHESS_ROOMS = [room for room in CHESS_ROOMS if player not in room.players]


async def game_page(request: web.Request):
    """
    Serve the client-side application.
    """
    cookies = request.cookies
    if COOKIE_NAME in cookies:
        cookie = cookies[COOKIE_NAME]
        if does_exist(COOKIE, cookie):
            if not is_connected(get_username_by_cookie(cookie)):
                with open('src/pages/client.html') as f:
                    return web.Response(text=f.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})


async def login(request: web.Request):
    """
    Serve the client-side application.
    """
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
                return True
    return False


@sio.event
async def get_data(sid):
    """
    returns the username and elo of the given sid.
    """
    username = get_username(sid)
    return {'username': username, 'elo': get_value(username, ELO)}

@sio.event
async def start_game(sid, data):
    """
    opens a new chess room for the given sids username,
    if the data stockfish key is True, the opponent will be stockfish.
    else the opponent will be the one in the waiting room
    then it will start the game.
    """
    username = get_username(sid)
    if is_in_room(username):
        return False
    if data.get('stockfish'):
        add_room(player1=username, time_limit=0.1)
        room = get_room(username)
        white_player = room.players[0]
        if white_player == username:
            await sio.emit('game_started', 'white', to=sid)
            room.start_clock()
        else:
            await sio.emit('game_started', 'black', to=sid)
            await send_stockfish_move(sid)
    else:
        if len(WAITING_ROOM):
            player1 = username
            player2 = WAITING_ROOM[0]
            add_room(player1=player1, player2=player2, time_limit=1)
            room = get_room(username)
            WAITING_ROOM.pop(0)
            await sio.emit('game_started', 'white', to=get_sid(room.players[0]))
            await sio.emit('game_started', 'black', to=get_sid(room.players[1]))
            room.start_clock()
        else:
            WAITING_ROOM.append(username)
            return 'searching for opponent'
    

@sio.event
async def send_stockfish_move(sid: str):
    room = get_room(get_username(sid))
    room.start_clock()
    move = get_stockfish_move(room.fen())
    room.commit_move(move)
    move_d = validate_move(move)
    await send_move_to_opponent(sid, move_d)


@sio.event
async def my_move(sid: str, data):
    username = get_username(sid)
    if not is_in_room(username):
        return False
    room = get_room(username)
    if not room.is_players_turn(username):
        return False
    opponent = room.opponent(username)
    move = validate_move(data.get('move'))
    if not move:
        return False
    room.commit_move(move.get('move'))
    if opponent == 'stockfish':
        await send_stockfish_move(sid)
    else:
        await send_move_to_opponent(opponent, move)



async def send_move_to_opponent(sid: str, move_d: dict[str, str]):
    print(move_d)
    username = get_username(sid)
    room = get_room(username)
    await sio.emit('opponent_move', move_d, to=sid)
    if not room.is_game_over():
        room.start_clock()
    else:
        player_resault = room.get_game_results()
        opponent = room.opponent(username)
        await sio.emit('game_over', player_resault.get(username), to=sid)
        if room.pvp:
            await sio.emit('game_over', player_resault.get(opponent), to=get_sid(opponent))
        close_room(username)



@sio.event
async def quit_game(sid):
    username = get_username(sid)
    if is_in_room(username):
        await handle_quit(username)


@sio.event
async def disconnect(sid):
    global CLIENTS, WAITING_ROOM   
    username = get_username(sid)
    CLIENTS = [client for client in CLIENTS if client.username != username]
    if username in WAITING_ROOM:
        WAITING_ROOM.remove(username)
    if is_in_room(username):
        await handle_quit(username)


async def handle_quit(username):
    opponent = get_opponent(username)
    close_room(username)
    if opponent !='stockfish':
        await sio.emit('opponent_quit', to=get_sid(opponent))


async def handle_timeout(username: str) -> None:
    opponent = get_opponent(username)
    close_room(username)
    await sio.emit('timeout', to=get_sid(username))
    if opponent !='stockfish':
        await sio.emit('opponent_quit', to=get_sid(opponent))
        
        
def validate_move(move: dict[str, str]|str) -> dict[str, str]|None:
    if isinstance(move, str):
        move = move.lower()
        regex = r'^[a-h][1-8][a-h][1-8][q,r,b,n]?$'
        if not re.fullmatch(regex, move):
            return None
        move_d: dict[str, str] = dict(move=move, src=move[:2], dst=move[2:4])
        if len(move) == 5:
            move_d.update(promotion=move[4])
        return move_d
    
    move_l = ['src', 'dst']
    move_l2 = ['src', 'dst', 'promotion']
    key_list = list(move.keys())
    if move_l == key_list or move_l2 == key_list:
        move_str = str(move.get('src')) + str(move.get('dst'))
        if 'promotion' in list(move.keys()):
            move_str += str(move.get('promotion'))
        move.update(move=move_str)
        return move
    return None


def check_for_timeout():
    while not STOP_THREAD:
        time.sleep(0.1)
        for room in CHESS_ROOMS:
            if room.is_timeout():
                asyncio.run(handle_timeout(room.timeout_player()))
            

async def login_validation(request: web.Request):
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data:
            username = data.get('username')
            password = data.get('password')
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


def main():
    global STOP_THREAD
    thread = threading.Thread(target=check_for_timeout)
    try:
        thread.start()
        web.run_app(app, port=5678)
    except KeyboardInterrupt:
        pass
    STOP_THREAD = True
    thread.join()
    print('the server has been shut down')
    
    
if __name__ == '__main__':
    main()