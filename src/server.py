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
async def send_elo(client: hc.Client):
    """
    send the given username's elo to the client.
    """
    await sio.emit('update_elo', {'elo': round(client.elo)}, to=client.sid)


async def send_clock_update(client: hc.Client):
    """
    send the clock update to the given username.
    """
    room = client.room
    if room is None:
        return
    clocks = {'white': round(room.get_time_left(room.players[0])),
              'black': round(room.get_time_left(room.players[1]))}
    await sio.emit('clock_update', clocks, to=client.sid)
    if not hc.is_engine_room(room):
        await sio.emit('clock_update', clocks, to=hc.get_oppoent(client).sid)


async def handle_game_over(client: hc.Client, move: dict[str, str]):
    """
    handle the game over event.
    """
    room = client.room
    if room is None:
        return
    room.stop_clock()
    resaults = room.get_game_results()
    await sio.emit('game_over', resaults.get(client.username), to=client.sid)
    if not hc.is_engine_room(room):
        move['game_over'] = 'true'
        opponent = hc.get_oppoent(client)
        hc.update_elo({client: resaults[client.username], opponent: resaults[opponent.username]})
        await sio.emit('opponent_move', move, to=opponent.sid)
        await sio.emit('game_over', resaults.get(opponent.username), to=opponent.sid)
        await send_elo(client)
        await send_elo(opponent)
    hc.close_room(client)


async def send_move_to_opponent(client: hc.Client, move_d: dict[str, str]):
    """
    send the given move to the given username.
    """
    await sio.emit('opponent_move', move_d, to=client.sid)
    room = client.room
    if room is not None:
        room.start_clock()
        await send_clock_update(client)


async def handle_quit(client: hc.Client) -> None:
    """
    handle the quit game event.
    """
    
    if client.room is not None and not hc.is_engine_room(client.room):
        opponent = hc.get_oppoent(client)
        hc.update_elo({client: '0', opponent: '1'})
        await sio.emit('opponent_quit', to=opponent.sid)
        await send_elo(opponent)
    hc.close_room(client)


async def handle_timeout(room: EngineRoom | PlayerRoom) -> None:
    """
    handle the timeout event.
    """
    username = room.timeout_player()
    if username == 'stockfish':
        client = hc.get_client(username=room.opponent(username))
        if client is None: return
        await sio.emit('opponent_timeout', to=client.sid)
    else:
        client = hc.get_client(username=username)
        if client is None or client.room is None: return
        await sio.emit('timeout', to=client.sid)
        if not hc.is_engine_room(client.room):
            opponent = hc.get_oppoent(client)
            hc.update_elo({client: '0', opponent: '1'})
            await sio.emit('opponent_timeout', to=opponent.sid)
    hc.close_room(client)


def check_for_timeout(stop_event: bool):
    """
    run endless loop to check for timeout.
    """
    while not stop_event:
        sleep(0.1)
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
                          'elo': round(hc.get_client(username=username).elo)}
                await sio.emit('user_data', data_d, to=sid)
                hd.update_entry(username)
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
    client = hc.get_client(sid=sid)
    if client.is_in_room() or client in hc.WAITING_ROOM or not data.get('game_mode'):
        return False
    clock: str|None = data.get('clock')
    if clock is None or not clock in chess_clocks:
        clock = chess_clocks[0]
    limit, bonus = [int(x) for x in clock.split('|')]
    if data.get('game_mode') == 'online':
        if len(hc.WAITING_ROOM) != 0:
            for opponent in hc.WAITING_ROOM:
                if opponent.choosen_clock == clock:
                    hc.WAITING_ROOM.remove(opponent)
                    room = hc.add_player_room(client, opponent, limit, bonus)
                    await set_pvp_room(room)
                    return
        client.set_chosen_clock(clock)
        hc.WAITING_ROOM.append(client)
        await sio.emit('searching', to=sid)
        return
    elif data.get('game_mode') == 'engine':
        if data.get('level') is None:
            data['level'] = 10
        room = hc.add_engine_room(client, data['level'], limit, bonus)
        await set_engine_room(room)
    else:
        return False


async def set_pvp_room(room: PlayerRoom):
    white, black = [hc.get_client(username=username) for username in room.players]
    white_data = dict(color='white', username=black.username, elo=black.elo)
    black_data = dict(color='black', username=white.username, elo=white.elo)
    await sio.emit('game_started', white_data, to=white.sid)
    await sio.emit('game_started', black_data, to=black.sid)
    room.start_clock()
    await send_clock_update(white)
    

async def set_engine_room(room: EngineRoom):
    client = hc.get_client(username=room.opponent('stockfish'))
    data = dict(color='black', username='stockfish', elo=0)
    if room.is_players_turn(client.username):
        data['color'] = 'white'
        await sio.emit('game_started', data, to=client.sid)
        room.start_clock()
    else:
        await sio.emit('game_started', data, to=client.sid)
        room.start_clock()
        await send_clock_update(client)
        await send_stockfish_move(client)
    await send_clock_update(client)
    
@sio.event
async def send_stockfish_move(client: hc.Client):
    """
    send stockfish move to the given username.
    """
    room = client.room
    if room is None or not isinstance(room, EngineRoom):
        return
    move = room.make_stockfish_move()
    move_d = uf.validate_move(move)
    if not move_d:
        return
    if room in hc.CHESS_ROOMS:
        await send_move_to_opponent(client, move_d)
        if room.is_game_over():
            await handle_game_over(client, move_d)


@sio.event
async def my_move(sid: str, data):
    """
    handle the given move from the given sid.
    """
    client = hc.get_client(sid=sid)
    if (client.room is None) or (not client.room.is_players_turn(client.username)):
        return False
    move = uf.validate_move(data.get('move'))
    if move is None:
        return False
    client.room.commit_move(move['move'])
    if client.room.is_game_over():
        await handle_game_over(client, move)
    else:
        if hc.is_engine_room(client.room):
            await send_stockfish_move(client)
        else:
            await send_move_to_opponent(hc.get_oppoent(client), move)
        await send_clock_update(client)


@sio.event
async def quit_game(sid):
    """
    handle the quit game event.
    """
    client = hc.get_client(sid=sid)
    if client.is_in_room():
        await handle_quit(client)
        await send_elo(client)
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
    hc.CLIENTS.remove(client)
    if client in hc.WAITING_ROOM:
        hc.WAITING_ROOM.remove(client)
    if client.is_in_room():
        await handle_quit(client)


app.add_routes([
    web.get('/', routs.game_page),
    web.get('/login', routs.login),
    web.get('/register', routs.register),
    web.get('/dungeon', routs.dungeon),
    web.get('/ping', routs.pong),
    web.post('/validate', routs.login_validation),
    web.post('/sign_up', routs.sign_up),
    web.post('/items', routs.items),
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
