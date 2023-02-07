"""
This file contains the server code for the chess game.
"""
import threading
import re
import asyncio
import time
import socketio
from aiohttp import web
from chess_rooms import EngineRoom, PlayerRoom, ChessRoom
import handle_database as hd

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


class Clients():
    """
    save the connection between the username and the sid.
    """

    def __init__(self, username: str, sid: str):
        self.username = username
        self.sid = sid


COOKIE_NAME: str = 'chess-cookie'

WAITING_ROOM: list[str] = []
CHESS_ROOMS: list[ChessRoom] = []
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


def is_connected(username: str) -> bool:
    """
    returns True if the given username is connected to the server.
    """
    return username in [client.username for client in CLIENTS]


def is_in_room(player: str) -> bool:
    """
    returns True if the given player is in a room.
    """
    for room in CHESS_ROOMS:
        if player in room.players:
            return True
    return False


def get_room(player: str) -> EngineRoom | PlayerRoom:
    """
    this function returns a ChessRoom object for the given player.
    """
    return [room for room in CHESS_ROOMS if player in room.players][0]


def is_engine_room(room: EngineRoom | PlayerRoom) -> bool:
    """
    return True if room is a engine room.
    """
    return isinstance(room, EngineRoom)


def close_room(player: str) -> None:
    """
    this function removes the room of the given player from the CHESS_ROOMS list.
    """
    CHESS_ROOMS.remove(get_room(player))


def add_engine_room(player: str, level: int = 10, time_limit: int = 10, bonus_time: int = 0) -> EngineRoom:
    """
    add a new engine room to the CHESS_ROOMS list.
    """
    CHESS_ROOMS.append(EngineRoom(player, level, time_limit, bonus_time))
    return get_room(player)


def add_player_room(player1: str, player2: str, time_limit: int = 10, bonus_time: int = 0) -> PlayerRoom:
    """
    add a player room to the CHESS_ROOMS list.
    """
    CHESS_ROOMS.append(PlayerRoom(player1, player2, time_limit, bonus_time))
    hd.update_games_played(player1)
    hd.update_games_played(player2)
    return get_room(player1)


async def game_page(request: web.Request):
    """
    Serve the client-side application.
    """
    cookies = request.cookies
    if COOKIE_NAME in cookies:
        cookie = cookies[COOKIE_NAME]
        if hd.does_exist(hd.COOKIE, cookie):
            if not is_connected(hd.get_username_by_cookie(cookie)):
                with open('src/pages/client.html', encoding='utf-8') as main_page:
                    return web.Response(text=main_page.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})


async def login(request: web.Request):
    """
    Serve the client-side application.
    """
    print(request)
    with open('src/pages/login.html', encoding='utf-8') as login_page:
        return web.Response(text=login_page.read(), content_type='text/html')


async def register(request: web.Request):
    """
    Serve the client-side application.
    """
    print(request)
    with open('src/pages/register.html', encoding='utf-8') as register_page:
        return web.Response(text=register_page.read(), content_type='text/html')


def update_elo(score_dict: dict[str, str]):
    """
    RatA + K * (score - (1 / (1 + 10**((RatB - RatA)/400))))
    K = 400 / games_played + 16
    """
    player1, player2 = tuple(score_dict.keys())
    player1_elo = float(hd.get_value(player1, hd.ELO))
    player2_elo = float(hd.get_value(player2, hd.ELO))
    player1_k = 400 / int(hd.get_value(player1, hd.GAMES_PLAYED)) + 16
    player2_k = 400 / int(hd.get_value(player2, hd.GAMES_PLAYED)) + 16
    player1_score = score_dict[player1]
    player2_score = score_dict[player2]
    player1_elo = player1_elo + player1_k * \
        (player1_score - (1 / (1 + 10 ** ((player2_elo - player1_elo) / 400))))
    player2_elo = player2_elo + player2_k * \
        (player2_score - (1 / (1 + 10 ** ((player1_elo - player2_elo) / 400))))
    hd.update_elo(player1, player1_elo)
    hd.update_elo(player2, player2_elo)


@sio.event
async def connect(sid, environ, auth):
    """
    called when the user trys to connect with a socket
    """
    environ = environ['aiohttp.request']
    if auth:
        if 'token' in auth:
            token = auth['token']
            if hd.does_exist(hd.COOKIE, token):
                username = hd.get_username_by_cookie(token)
                CLIENTS.append(Clients(username, sid))
                data_d = {'username': username,
                          'elo': str(round(hd.get_value(username, hd.ELO)))}
                await sio.emit('user_data', data_d, to=sid)
                return True
    return False


@sio.event
async def start_game(sid, data):
    """
    opens a new chess room for the given sids username,
    if the data stockfish key is True, the opponent will be stockfish.
    else the opponent will be the one in the waiting room
    then it will start the game.
    """
    username = get_username(sid)
    if is_in_room(username) or username in WAITING_ROOM or not data.get('game_mode'):
        return False
    match data['game_mode']:
        case 'online':
            if len(WAITING_ROOM) == 0:
                WAITING_ROOM.append(username)
                return
            player2 = WAITING_ROOM.pop(0)
            room = add_player_room(player1=username, player2=player2)
            await sio.emit('game_started', 'white', to=get_sid(room.players[0]))
            await sio.emit('game_started', 'black', to=get_sid(room.players[1]))
            room.start_clock()

        case 'engine':
            if not data.get('level'):
                return False
            room = add_engine_room(
                username, level=data.get('level'), time_limit=1)
            if room.is_players_turn(username):
                await sio.emit('game_started', 'white', to=sid)
                room.start_clock()
            else:
                await sio.emit('game_started', 'black', to=sid)
                await send_stockfish_move(username)
        case _:
            return False


@sio.event
async def send_stockfish_move(username: str):
    """
    send stockfish move to the given username.
    """
    room = get_room(username)
    move = room.make_stockfish_move()
    move_d = validate_move(move)
    if room in CHESS_ROOMS:
        await send_move_to_opponent(username, move_d)
        if room.is_game_over():
            await handle_game_over(username, move_d)


@sio.event
async def my_move(sid: str, data):
    """
    handle the given move from the given sid.
    """
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
    if room.is_game_over():
        await handle_game_over(username, move)
    elif is_engine_room(room):
        await send_stockfish_move(username)
    else:
        await send_move_to_opponent(opponent, move)
    await send_clock_update(username)


async def handle_game_over(username: str, move: dict[str, str]):
    """
    handle the game over event.
    """
    room = get_room(username)
    room.stop_clock()
    resaults = room.get_game_results()
    await sio.emit('game_over', resaults.get(username), to=get_sid(username))
    if not is_engine_room(room):
        update_elo(resaults)
        opponent = room.opponent()
        await sio.emit('opponent_move', move, to=get_sid(opponent))
        await sio.emit('game_over', resaults.get(opponent), to=get_sid(opponent))
        await send_elo(username)
        await send_elo(opponent)
    close_room(username)


async def send_move_to_opponent(username: str, move_d: dict[str, str]):
    """
    send the given move to the given username.
    """
    room = get_room(username)
    await sio.emit('opponent_move', move_d, to=get_sid(username))
    await send_clock_update(username)
    room.start_clock()


@sio.event
async def quit_game(sid):
    """
    handle the quit game event.
    """
    username = get_username(sid)
    if is_in_room(username):
        await handle_quit(username)
    elif username in WAITING_ROOM:
        WAITING_ROOM.remove(username)


@sio.event
async def ping(sid):
    """
    handle the ping event.
    """
    await sio.emit('pong', to=sid)


@sio.event
async def disconnect(sid):
    """
    handle the disconnect event.
    """
    username = get_username(sid)
    remove_client(username)
    if username in WAITING_ROOM:
        WAITING_ROOM.remove(username)
    if is_in_room(username):
        await handle_quit(username)


async def send_clock_update(username: str):
    """
    send the clock update to the given username.
    """
    room = get_room(username)
    white_player = room.players[0]
    clocks = {'white': round(room.get_time_left(white_player)),
              'black': round(room.get_time_left(room.opponent(white_player)))}
    await sio.emit('clock_update', clocks, to=get_sid(username))
    if not is_engine_room(room):
        await sio.emit('clock_update', clocks, to=get_sid(room.opponent(username)))


def remove_client(username: str):
    """
    remove the client from the list of clients.
    """
    CLIENTS.remove(
        [client for client in CLIENTS if client.username == username][0])


async def send_elo(username: str):
    """
    send the given username's elo to the client.
    """
    elo = str(round(hd.get_value(username, hd.ELO)))
    await sio.emit('update_elo', {'elo': elo}, to=get_sid(username))


async def handle_quit(username: str) -> None:
    """
    handle the quit game event.
    """
    room = get_room(username)
    opponent = room.opponent(username)
    close_room(username)
    if not is_engine_room(room):
        update_elo({username: 0, opponent: 1})
        await sio.emit('opponent_quit', to=get_sid(opponent))
        await send_elo(opponent)
        if is_connected(username):
            await send_elo(username)


async def handle_timeout(username: str, room: EngineRoom | PlayerRoom) -> None:
    """
    handle the timeout event.
    """
    if username == 'stockfish':
        await sio.emit('opponent_timeout', to=get_sid(room.opponent(username)))
        close_room(room.opponent(username))
        return
    await sio.emit('timeout', to=get_sid(username))
    if not is_engine_room(room):
        update_elo({username: 0, room.opponent(username): 1})
        await sio.emit('opponent_timeout', to=get_sid(room.opponent(username)))
    close_room(username)


def validate_move(move: str) -> dict[str, str] | None:
    """
    validate the given move and return a dict representation of it.
    """
    move = move.lower()
    regex = r'^[a-h][1-8][a-h][1-8][q,r,b,n]?$'
    if not re.fullmatch(regex, move):
        return None
    move_d: dict[str, str] = dict(move=move, src=move[:2], dst=move[2:4])
    if len(move) == 5:
        move_d.update(promotion=move[4])
    return move_d


def check_for_timeout(stop_event: threading.Event):
    """
    run endless loop to check for timeout.
    """
    while not stop_event():
        time.sleep(0.1)
        for room in CHESS_ROOMS:
            if room.is_timeout():
                asyncio.run(handle_timeout(room.timeout_player(), room))


async def login_validation(request: web.Request):
    """
    validate login.
    """
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data:
            username = data.get('username')
            password = data.get('password')
            if hd.does_exist(hd.USERNAME, username):
                if hd.check_password(username, password):
                    if not is_connected(username):
                        response = web.json_response({'status': 'ok'})
                        response.set_cookie(
                            COOKIE_NAME, hd.get_value(username, hd.COOKIE))
                        return response
    return web.json_response({'status': 'error'})


async def sign_up(request: web.Request):
    """
    sign up.
    """
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data and 'email' in data:
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            return web.json_response({'status': hd.create_new_user(username, password, email)})
    return web.json_response({'status': 400})


app.add_routes([web.get('/', game_page),
                web.get('/login', login),
                web.get('/register', register),
                web.post('/validate', login_validation),
                web.post('/sign_up', sign_up),
                web.static('/scripts', 'src/scripts'),
                web.static('/styles', 'src/styles'),
                web.static('/images', 'src/images')])


def main():
    """
    main function.
    """
    stop_thread = False
    thread = threading.Thread(target=check_for_timeout,
                              args=(lambda: stop_thread,))
    try:
        thread.start()
        web.run_app(app, port=5678)
    except KeyboardInterrupt:
        pass
    stop_thread = True
    thread.join()
    print('the server has been shut down')


if __name__ == '__main__':
    main()
