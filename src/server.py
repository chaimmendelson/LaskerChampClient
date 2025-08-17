"""
This file contains the server code for the chess game.
"""
import os
import threading
import asyncio
from time import time
import socketio

from .chess_rooms import EngineRoom, PlayerRoom, WON, LOST, CHESS_ROOMS
from .accounts_db import does_exist, COOKIE, get_username_by_cookie, update_entry, reset_table
from .handle_clients import Client, add_client, get_client, WAITING_ROOM, is_in_waiting_room, get_client_clock, \
    add_player_room, add_to_waiting_room, add_engine_room, clock_update, get_oppoent, update_elo, close_room, \
    remove_from_waiting_room, remove_client, WAITING_ENTRE_TIME, chess_clocks
from .app_routs import *
from .useful_func import validate_move
#os.chmod(STOCKFISH_L_PATH, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

OPPONENT_ELO_RANGE = 100
    

async def handle_game_over(client: Client):
    """
    handle the game over event.
    """
    room = client.room
    if room is None: return
    results = room.get_game_results()
    last_move = room.last_move()
    if isinstance(room, PlayerRoom):
        room.stop_clock()
        opponent = get_oppoent(client)
        update_elo({client: results[client.username], opponent: results[opponent.username]})
        await send_game_over_msg(opponent, last_move, results[opponent.username])
    await send_game_over_msg(client, last_move, results[client.username])
    close_room(client)

async def send_game_over_msg(client: Client, last_move: str, result: int):
    data = dict(move=last_move,
                clock=clock_update(client),
                resault=result,
                elo=client.elo_int())
    await sio.emit('game_over', data, to=client.sid)
    

async def send_move_to_opponent(client: Client):
    """
    send the given move to the given username.
    """
    room = client.room
    if room is None: return
    await sio.emit('opponent_move', dict(move=room.last_move(), clock=clock_update(client)), to=client.sid)
    if isinstance(room, PlayerRoom):
        room.start_clock()
    


async def handle_quit(client: Client) -> None:
    """
    handle the quit game event.
    """
    if client.room is not None and not isinstance(client.room, EngineRoom):
        opponent = get_oppoent(client)
        update_elo({client: -1, opponent: 1})
        await sio.emit('opponent_quit', dict(elo=opponent.elo_int(), clock=clock_update(opponent)), to=opponent.sid)
    close_room(client)


async def handle_timeout(room: PlayerRoom) -> None:
    """
    handle the timeout event.
    """
    username = room.timeout_player()
    client = get_client(username=username)
    if client is None or client.room is None: return
    opponent = get_oppoent(client)
    update_elo({client: LOST, opponent: WON})
    await game_closed_msg(opponent, 'opponent_timeout')
    await game_closed_msg(client, 'timeout')
    close_room(client)

async def game_closed_msg(client: Client, msg: str):
    """
    send the game_closed message to the given client.
    """
    await sio.emit(msg, dict(elo=client.elo_int(), clock=clock_update(client)), to=client.sid)
    
            
@sio.event
async def connect(sid, _, auth):
    """
    called when the user trys to connect with a socket
    """
    if auth:
        if 'token' in auth:
            token = auth['token']
            if does_exist(COOKIE, token):
                username = get_username_by_cookie(token)
                add_client(username, sid)
                data_d = {'username': username,
                          'elo': get_client(username=username).elo_int()}
                update_entry(username)
                await sio.emit('user', data_d, to=sid)
                return True
    return False

@sio.event
async def start_game(sid, data: dict):
    """
    opens a new chess room for the given sids username,
    if the data stockfish key is True, the opponent will be stockfish.
    else the opponent will be the one in the waiting room
    then it will start the game.
    """
    client = get_client(sid=sid)
    if client.is_in_room() or client in WAITING_ROOM or not data.get('game_mode'):
        return False
    clock: str|None = data.get('clock')
    if data.get('game_mode') == 'online':
        if clock is None or not clock in chess_clocks:
            clock = chess_clocks[0]
        if is_in_waiting_room(client):
            return {'status': 0}
        if len(WAITING_ROOM[clock]) != 0:
            for opponent in WAITING_ROOM[clock]:
                if get_client_clock(opponent) == clock and\
                    opponent.elo_int() in range(client.elo_int() - OPPONENT_ELO_RANGE,
                                                client.elo_int() + OPPONENT_ELO_RANGE):
                    room = add_player_room(client, opponent, clock)
                    await set_pvp_room(room)
                    return {'status': 1}
        add_to_waiting_room(client, clock)
        return {'status': 2}
    elif data.get('game_mode') == 'engine':
        if data.get('level') is None:
            data['level'] = 10
        room = add_engine_room(client, data['level'])
        await set_engine_room(room)
        return {'status': 1}
    else:
        return {'status': 0}


async def set_pvp_room(room: PlayerRoom):
    white, black = [get_client(username=username) for username in room.players]
    clock = clock_update(white)
    white_data = dict(color='w', opponent=dict(username=black.username, elo=black.elo_int()), clock=clock)
    black_data = dict(color='b', opponent=dict(username=white.username, elo=white.elo_int()), clock=clock)
    await sio.emit('game_started', white_data, to=white.sid)
    await sio.emit('game_started', black_data, to=black.sid)
    room.start_clock()
    

async def set_engine_room(room: EngineRoom):
    client = get_client(username=room.opponent('stockfish'))
    data: dict[str, dict|str] = dict(opponent=dict(username='stockfish', elo=0), clock=clock_update(client))
    data['color'] = 'w' if room.is_players_turn(client.username) else 'b'
    await sio.emit('game_started', data, to=client.sid)
    if not room.is_players_turn(client.username):
        await send_stockfish_move(client)
    
    
async def send_stockfish_move(client: Client):
    """
    send stockfish move to the given username.
    """
    room = client.room
    if room is None or not isinstance(room, EngineRoom):
        return
    room.make_stockfish_move()
    if room in CHESS_ROOMS:
        if room.is_game_over():
            await handle_game_over(client)
        else:
            await send_move_to_opponent(client)


@sio.event
async def message(sid: str, message: str):
    """
    handle the message event.
    """
    client = get_client(sid=sid)
    if client.room is None: return

    print("message from", client.username, ":", message)
    await sio.emit(
        'message',
        message,
        to=get_client(username=client.room.opponent(client.username)).sid
    )

@sio.event
async def my_move(sid: str, data: dict[str, str]):
    """
    handle the given move from the given sid.
    """
    client = get_client(sid=sid)
    if (client.room is None) or (not client.room.is_players_turn(client.username)):
        return False
    move = validate_move(data.get('move'))
    if move is None: return False
    client.room.commit_move(move)
    if client.room.is_game_over():
        await handle_game_over(client)
    else:
        if isinstance(client.room, EngineRoom):
            await send_stockfish_move(client)
        else:
            await send_move_to_opponent(get_oppoent(client))
        await sio.emit('move_received', dict(move=move, clock=clock_update(client)), to=sid)


@sio.event
async def quit_game(sid):
    """
    handle the quit game event.
    """
    client = get_client(sid=sid)
    if client.is_in_room():
        await handle_quit(client)
    return dict(elo=client.elo_int())


@sio.event
async def ping(_) -> str:
    """
    handle the ping event.
    """
    return 'pong'


@sio.event
async def quit_waiting(sid):
    """
    handle the quit waiting event.
    """
    client = get_client(sid=sid)
    if is_in_waiting_room(client):
        remove_from_waiting_room(client)
        return dict(success=True)
    if client.is_in_room():
        return dict(success=False)
    return dict(success=True)


@sio.event
async def disconnect(sid):
    """
    handle the disconnect event.
    """
    client = get_client(sid=sid)
    if is_in_waiting_room(client):
        remove_from_waiting_room(client)
    if client.is_in_room():
        await handle_quit(client)
    remove_client(sid)
    

class KillableThread(threading.Thread):
    def __init__(self, function, sleep_interval: int|float=1):
        super().__init__()
        self._kill = threading.Event()
        self._interval = sleep_interval
        self._function = function

    def run(self):
        while True:
            self._function()
            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            #  wake up and handle
            is_killed = self._kill.wait(self._interval)
            if is_killed:
                break

        print("Killing Thread")

    def kill(self):
        self._kill.set()
        
        
def check_for_timeout():
    """
    run endless loop to check for timeout.
    """
    rooms = [room for room in CHESS_ROOMS if isinstance(room, PlayerRoom)]
    for room in rooms:
        if room.is_timeout():
            asyncio.run(handle_timeout(room))


def check_waiting_room():
    """
    run endless loop to check for waiting room.
    """
    for client, entry in WAITING_ENTRE_TIME.items():
        if time() - entry > 10:
            clock = get_client_clock(client)
            if len(WAITING_ROOM[clock]) == 1:
                continue
            # find the player with the closest elo to the client
            client_elo = client.elo_int()
            # find the closest elo to the client
            opponent = min(WAITING_ROOM[clock], key=lambda x: abs(x.elo_int() - client_elo) if x != client else 100000)
            room = add_player_room(client, opponent, clock)
            asyncio.run(set_pvp_room(room))
            break
            
            
app.add_routes([
    web.get('/', game_page),
    web.get('/login', login),
    web.get('/register', register),
    web.get('/admin', admin),
    web.get('/ping', pong),
    web.post('/validate', login_validation),
    web.post('/sign_up', sign_up),
    web.post('/stats', get_stats),
    web.static('/scripts', 'src/scripts'),
    web.static('/styles', 'src/styles'),
    web.static('/images', 'src/images'),
    web.static('/packages', 'src/packages'),
])


def main():
    """
    main function.
    """
    # import stat
    # from chess_rooms import STOCKFISH_L_PATH
    # os.chmod(STOCKFISH_L_PATH, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    if input("Do you want to reset the table? (y/n): ") == 'y':
        reset_table()

    threads: list[KillableThread] = [KillableThread(check_for_timeout, 0.1), KillableThread(check_waiting_room, 0.1)]
    try:
        for thread in threads:
            thread.daemon = True
            thread.start()
        web.run_app(app, port=int(os.getenv('PORT', '5678')))
    except KeyboardInterrupt:
        pass
    print('The server has been shut down')


if __name__ == '__main__':
    main()
    
