"""
This file contains the server code for the chess game.
"""
import os
import threading
import asyncio
from time import sleep
import socketio
import re
from aiohttp import web
from chess_rooms import EngineRoom, PlayerRoom
import accounts_db as hd
import handle_clients as hc
import app_routs as routs
import useful_func as uf
#os.chmod(STOCKFISH_L_PATH, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


chess_clocks = ['5|0', '3|2', '10|5', '15|10', '30|0']
    

async def handle_game_over(client: hc.Client):
    """
    handle the game over event.
    """
    room = client.room
    if room is None: return
    room.stop_clock()
    resaults = room.get_game_results()
    last_move = room.last_move()
    if not hc.is_engine_room(room):
        opponent = hc.get_oppoent(client)
        hc.update_elo({client: resaults[client.username], opponent: resaults[opponent.username]})
        await send_game_over_msg(opponent, last_move, resaults[opponent.username])
    await send_game_over_msg(client, last_move, resaults[client.username])
    hc.close_room(client)

async def send_game_over_msg(client: hc.Client, last_move: str, resault: str):
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
    await sio.emit('opponent_move', dict(move=room.last_move, clock=hc.clock_update(client)), to=client.sid)
    room.start_clock()


async def handle_quit(client: hc.Client) -> None:
    """
    handle the quit game event.
    """
    if client.room is not None and not hc.is_engine_room(client.room):
        opponent = hc.get_oppoent(client)
        hc.update_elo({client: '0', opponent: '1'})
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
        if not hc.is_engine_room(client.room):
            opponent = hc.get_oppoent(client)
            hc.update_elo({client: '0', opponent: '1'})
            await game_closed_msg(opponent, 'opponent_timeout')
        await game_closed_msg(client, 'timeout')
    hc.close_room(client)

async def game_closed_msg(client: hc.Client, msg: str):
    """
    send the game_closed message to the given client.
    """
    await sio.emit(msg, dict(elo=client.elo_int()), to=client.sid)
    
    
def check_for_timeout(stop_event: bool):
    """
    run endless loop to check for timeout.
    """
    while not stop_event:
        sleep(0.1) # type: ignore
        for room in hc.CHESS_ROOMS:
            if room.is_timeout():
                asyncio.run(handle_timeout(room))


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
                await sio.emit('connected', data_d, to=sid)
                hd.update_entry(username)
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
        if len(hc.WAITING_ROOM) != 0:
            for opponent in hc.WAITING_ROOM:
                if opponent.choosen_clock == clock:
                    hc.WAITING_ROOM.remove(opponent)
                    room = hc.add_player_room(client, opponent, clock)
                    await set_pvp_room(room)
                    return
        client.set_chosen_clock(clock)
        hc.WAITING_ROOM.append(client)
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
    white_data = dict(color='white', opponent=dict(username=black.username, elo=black.elo), clock=clock)
    black_data = dict(color='black', opponent=dict(username=white.username, elo=white.elo), clock=clock)
    await sio.emit('game_started', white_data, to=white.sid)
    await sio.emit('game_started', black_data, to=black.sid)
    room.start_clock()
    

async def set_engine_room(room: EngineRoom):
    client = hc.get_client(username=room.opponent('stockfish'))
    data = dict(color='black', opponent=dict(username='stockfish', elo=0), clock=hc.clock_update(client))
    if room.is_players_turn(client.username):
        data['color'] = 'white'
        await sio.emit('game_started', data, to=client.sid)
        room.start_clock()
    else:
        await sio.emit('game_started', data, to=client.sid)
        room.start_clock()
        await send_stockfish_move(client)
    
    
async def send_stockfish_move(client: hc.Client):
    """
    send stockfish move to the given username.
    """
    room = client.room
    if room is None or not isinstance(room, EngineRoom):
        return
    move = uf.validate_move(room.make_stockfish_move())
    if move is None:
        return
    if room in hc.CHESS_ROOMS:
        await send_move_to_opponent(client)
        if room.is_game_over():
            await handle_game_over(client)


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
        if hc.is_engine_room(client.room):
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
    elif client in hc.WAITING_ROOM:
        hc.WAITING_ROOM.remove(client)


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
    client = hc.get_client(sid=sid)
    hc.remove_client(sid)
    if client in hc.WAITING_ROOM:
        hc.WAITING_ROOM.remove(client)
    if client.is_in_room():
        await handle_quit(client)


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
    stop_thread = False
    thread = threading.Thread(target=check_for_timeout,
                              args=(lambda: stop_thread,))
    try:
        thread.start()
        web.run_app(app, port=os.getenv('PORT', '5678')) # type: ignore
    except KeyboardInterrupt:
        pass
    stop_thread = True
    thread.join()
    print('The server has been shut down')


if __name__ == '__main__':
    main()
    
