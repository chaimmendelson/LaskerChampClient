"""
handle the connected users.
"""
from .client_class import *
from .stats import *
import time
chess_clocks = ['1|0', '1|1', '2|1', '3|0', '3|2', '5|0', '10|5', '15|10', '30|0']


WAITING_ROOM: dict[str, list[Client]] = {chess_clocks[i]: [] for i in range(len(chess_clocks))}
WAITING_ENTRE_TIME: dict[Client, float] = {}


def add_client(username: str, sid: str) -> None:
    """
    add a new client to the CLIENTS list.
    """ 
    CLIENTS.add(Client(username, sid))

def remove_client(sid: str) -> None:
    """
    remove the client with the given sid from the CLIENTS list.
    """
    for client in CLIENTS:
        if client.sid == sid:
            CLIENTS.remove(client)
            break

def is_client_connected(username: str) -> bool:
    """
    return True if the given username is connected.
    """
    for client in CLIENTS:
        if client.username == username:
            return True
    return False


def get_client(sid: str|None = None, username: str|None = None) -> Client:
    """
    get the client object of the given username or sid.
    """
    if sid is not None:
        for client in CLIENTS:
            if client.sid == sid:
                return client
    if username is not None:
        for client in CLIENTS:
            if client.username == username:
                return client
    return Client('', '')  # return a dummy client


def get_oppoent(client: Client) -> Client:
    """
    get the opponent of the given client.
    """
    if client.room is None:
        return Client('', '')
    return get_client(username=client.room.opponent(client.username))


def close_room(client: Client) -> None:
    """
    this function removes the room of the given player from the CHESS_ROOMS list.
    """
    if client.room is not None:
        if not isinstance(client.room, EngineRoom):
            get_oppoent(client).exit_room()
        CHESS_ROOMS.remove(client.room)
        client.exit_room()
        

def add_to_waiting_room(client: Client, clock: str) -> None:
    WAITING_ROOM[clock].append(client)
    WAITING_ENTRE_TIME[client] = time.time()


def get_client_clock(client: Client) -> str:
    """
    return the clock of the given client.
    """
    for clock, clients in WAITING_ROOM.items():
        if client in clients:
            return clock
    return ''

def is_in_waiting_room(client: Client) -> bool:
    """
    return True if the given client is in the waiting room.
    """
    return get_client_clock(client) != ''


def remove_from_waiting_room(client: Client, clock: str|None=None) -> None:
    """
    remove the given client from the waiting room.
    """
    if is_in_waiting_room(client):
        clock = clock if clock is not None else get_client_clock(client)
        WAITING_ROOM[clock].remove(client)
        WAITING_ENTRE_TIME.pop(client)


def add_engine_room(player: Client, level: int = 10) -> EngineRoom:
    """
    add a new engine room to the CHESS_ROOMS list.
    """
    room = EngineRoom(player.username, level)
    CHESS_ROOMS.add(room)
    player.enter_room(room)
    update_stat(ENGINE_PLAYED)
    return room


def add_player_room(player1: Client, player2: Client, clock: str = DEAFULT_CLOCK) -> PlayerRoom:
    """
    add a player room to the CHESS_ROOMS list.
    """
    remove_from_waiting_room(player1, clock)
    remove_from_waiting_room(player2, clock)
    room = PlayerRoom(player1.username, player2.username, clock)
    CHESS_ROOMS.add(room)
    player1.update_games_played()
    player2.update_games_played()
    player1.enter_room(room)
    player2.enter_room(room)
    update_stat(PVP_PLAYED)
    return room


def update_elo(score_dict: dict[Client, int]):
    """
    RatA + K * (score - (1 / (1 + 10**((RatB - RatA)/400))))
    K = 400 / games_played + 16
    """
    player1, player2 = tuple(score_dict.keys())
    player1_score, player2_score = score_dict[player1], score_dict[player2]
    
    if player1_score == DRAW: return
    player1_score = 1 if player1_score == WON else 0
    player2_score = 1 - player1_score
    
    player1_elo, player2_elo = player1.elo, player2.elo
    player1.update_elo(player2_elo, player1_score)
    player2.update_elo(player1_elo, player2_score)

def clock_update(client: Client) -> dict[str, int]:
    """
    send the clock update to the given username.
    """
    room = client.room
    if room is None or isinstance(room, EngineRoom):
        return dict(w = 0, b = 0)
    return dict(
            w = round(room.get_time_left(room.players[0])),
            b = round(room.get_time_left(room.players[1]))
            )