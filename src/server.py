"""
This file contains the server code for the chess game.
"""
import os
import threading
import asyncio
from time import sleep, time
import socketio
import re
from aiohttp import web
from chess_rooms import EngineRoom, PlayerRoom, WON, LOST, DRAW
import accounts_db as hd
import handle_clients as hc
import app_routs as routs
import useful_func as uf
import stats
#os.chmod(STOCKFISH_L_PATH, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


chess_clocks = ['5|0', '3|2', '10|5', '15|10', '30|0']
OPPONENT_ELO_RANGE = 100
    

async def handle_game_over(client: hc.Client):
    """
    handle the game over event.
    """
    room = client.room
    if room is None: return
    room.stop_clock()
    resaults = room.get_game_results()
    last_move = room.last_move()
    if not isinstance(room, EngineRoom):
        opponent = hc.get_oppoent(client)
        hc.update_elo({client: resaults[client.username], opponent: resaults[opponent.username]})
        await send_game_over_msg(opponent, last_move, resaults[opponent.username])
    await send_game_over_msg(client, last_move, resaults[client.username])
    hc.close_room(client)

async def send_game_over_msg(client: hc.Client, last_move: str, resault: int):
    data = dict(move=last_move,
                clock=hc.clock_update(client),
                resault=resault,
                elo=client.elo_int())
    await sio.emit('game_over', data, to=client.sid)
    

async def send_move_to_opponent(client: hc.Client):
    """
    send the given move to the given username.
    """
    room = client.room
    if room is None: return
    await sio.emit('opponent_move', dict(move=room.last_move(), clock=hc.clock_update(client)), to=client.sid)
    room.start_clock()


async def handle_quit(client: hc.Client) -> None:
    """
    handle the quit game event.
    """
    if client.room is not None and not isinstance(client.room, EngineRoom):
        opponent = hc.get_oppoent(client)
        hc.update_elo({client: -1, opponent: 1})
        await sio.emit('opponent_quit', dict(elo=opponent.elo_int()), to=opponent.sid)
    hc.close_room(client)


async def handle_timeout(room: EngineRoom | PlayerRoom) -> None:
    """
    handle the timeout event.
    """
    username = room.timeout_player()
    if username == 'stockfish':
        client = hc.get_client(username=room.opponent(username))
        if client is None: return
        await game_closed_msg(client, 'opponent_timeout')
    else:
        client = hc.get_client(username=username)
        if client is None or client.room is None: return
        if not isinstance(client.room, EngineRoom):
            opponent = hc.get_oppoent(client)
            hc.update_elo({client: LOST, opponent: WON})
            await game_closed_msg(opponent, 'opponent_timeout')
        await game_closed_msg(client, 'timeout')
    hc.close_room(client)

async def game_closed_msg(client: hc.Client, msg: str):
    """
    send the game_closed message to the given client.
    """
    await sio.emit(msg, dict(elo=client.elo_int()), to=client.sid)
    
            
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
                hc.add_client(username, sid)
                data_d = {'username': username,
                          'elo': hc.get_client(username=username).elo_int()}
                hd.update_entry(username)
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
    client = hc.get_client(sid=sid)
    if client.is_in_room() or client in hc.WAITING_ROOM or not data.get('game_mode'):
        return False
    clock: str|None = data.get('clock')
    if clock is None or not clock in chess_clocks:
        clock = chess_clocks[0]
    if data.get('game_mode') == 'online':
        if len(hc.WAITING_ROOM[clock]) != 0:
            for opponent in hc.WAITING_ROOM[clock]:
                if hc.get_client_clock(opponent) == clock and\
                    opponent.elo_int() in range(client.elo_int() - OPPONENT_ELO_RANGE,
                                                client.elo_int() + OPPONENT_ELO_RANGE):
                    room = hc.add_player_room(client, opponent, clock)
                    await set_pvp_room(room)
                    return
        hc.add_to_waiting_room(client, clock)
        await sio.emit('searching', to=sid)
        return
    elif data.get('game_mode') == 'engine':
        if data.get('level') is None:
            data['level'] = 10
        room = hc.add_engine_room(client, data['level'], clock)
        await set_engine_room(room)
    else:
        return False


async def set_pvp_room(room: PlayerRoom):
    white, black = [hc.get_client(username=username) for username in room.players]
    clock = hc.clock_update(white)
    white_data = dict(color='w', opponent=dict(username=black.username, elo=black.elo_int()), clock=clock)
    black_data = dict(color='b', opponent=dict(username=white.username, elo=white.elo_int()), clock=clock)
    await sio.emit('game_started', white_data, to=white.sid)
    await sio.emit('game_started', black_data, to=black.sid)
    room.start_clock()
    

async def set_engine_room(room: EngineRoom):
    client = hc.get_client(username=room.opponent('stockfish'))
    data: dict[str, dict|str] = dict(opponent=dict(username='stockfish', elo=0), clock=hc.clock_update(client))
    data['color'] = 'w' if room.is_players_turn(client.username) else 'b'
    await sio.emit('game_started', data, to=client.sid)
    room.start_clock()
    if not room.is_players_turn(client.username):
        await send_stockfish_move(client)
    
    
async def send_stockfish_move(client: hc.Client):
    """
    send stockfish move to the given username.
    """
    room = client.room
    if room is None or not isinstance(room, EngineRoom):
        return
    room.make_stockfish_move()
    if room in hc.CHESS_ROOMS:
        if room.is_game_over():
            await handle_game_over(client)
        else:
            await send_move_to_opponent(client)


@sio.event
async def my_move(sid: str, data: dict[str, str]):
    """
    handle the given move from the given sid.
    """
    client = hc.get_client(sid=sid)
    if (client.room is None) or (not client.room.is_players_turn(client.username)):
        return False
    move = uf.validate_move(data.get('move'))
    if move is None: return False
    client.room.commit_move(move)
    if client.room.is_game_over():
        await handle_game_over(client)
    else:
        if isinstance(client.room, EngineRoom):
            await send_stockfish_move(client)
        else:
            await send_move_to_opponent(hc.get_oppoent(client))
        await sio.emit('move_received', dict(move=move, clock=hc.clock_update(client)), to=sid)


@sio.event
async def quit_game(sid):
    """
    handle the quit game event.
    """
    client = hc.get_client(sid=sid)
    if client.is_in_room():
        await handle_quit(client)
    return dict(elo=client.elo_int())


@sio.event
async def ping(sid) -> str:
    """
    handle the ping event.
    """
    return 'pong'


@sio.event
async def quit_waiting(sid):
    """
    handle the quit waiting event.
    """
    client = hc.get_client(sid=sid)
    if hc.is_in_waiting_room(client):
        hc.remove_from_waiting_room(client)
        return dict(success=True)
    if client.is_in_room():
        return dict(success=False)
    return dict(success=True)


@sio.event
async def disconnect(sid):
    """
    handle the disconnect event.
    """
    client = hc.get_client(sid=sid)
    if hc.is_in_waiting_room(client):
        hc.remove_from_waiting_room(client)
    if client.is_in_room():
        await handle_quit(client)
    hc.remove_client(sid)
    

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
    for room in hc.CHESS_ROOMS:
        if room.is_timeout():
            asyncio.run(handle_timeout(room))
            break


def check_waiting_room():
    """
    run endless loop to check for waiting room.
    """
    for client, entry in hc.WAITING_ENTRE_TIME.items():
        if time() - entry > 10:
            clock = hc.get_client_clock(client)
            if len(hc.WAITING_ROOM[clock]) == 1:
                continue
            # find the player with the closest elo to the client
            client_elo = client.elo_int()
            # find the closest elo to the client
            opponent = min(hc.WAITING_ROOM[clock], key=lambda x: abs(x.elo_int() - client_elo) if x != client else 100000)
            room = hc.add_player_room(client, opponent, clock)
            asyncio.run(set_pvp_room(room))
            break
            
            
app.add_routes([
    web.get('/', routs.game_page),
    web.get('/login', routs.login),
    web.get('/register', routs.register),
    web.get('/admin', routs.admin),
    web.get('/ping', routs.pong),
    web.post('/validate', routs.login_validation),
    web.post('/sign_up', routs.sign_up),
    web.post('/stats', routs.get_stats),
    web.static('/scripts', 'src/scripts'),
    web.static('/styles', 'src/styles'),
    web.static('/images', 'src/images'),
])


def main():
    """
    main function.
    """
    # import stat
    # from chess_rooms import STOCKFISH_L_PATH
    # os.chmod(STOCKFISH_L_PATH, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    stats.reset_counter(stats.ONLINE_PLAYERS)
    threads: list[KillableThread] = []
    threads.append(KillableThread(check_for_timeout, 0.1))
    threads.append(KillableThread(check_waiting_room, 0.1))
    try:
        for thread in threads:
            thread.start()
        web.run_app(app, port=os.getenv('PORT', '5678')) # type: ignore
    except KeyboardInterrupt:
        pass
    for thread in threads:
        thread.kill()
    print('The server has been shut down')


if __name__ == '__main__':
    main()
    
