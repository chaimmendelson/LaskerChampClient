"""
handle the connected users.
"""
from chess_rooms import PlayerRoom, EngineRoom
import handle_database as hd
CHESS_ROOMS: list[PlayerRoom | EngineRoom] = []


class Client():
    """
    save the connection between the username and the sid.
    """

    def __init__(self, username: str, sid: str):
        self.username: str = username
        self.sid: str = sid
        # the room that the user is in.
        self.room: EngineRoom | PlayerRoom | None = None
        self.elo: float = float(hd.get_value(self.username, hd.ELO))

    def update_elo(self, opponent_elo, player_score):
        """
        calculate the new elo of the player.
        """
        k_val = (400 / (int(hd.get_value(self.username, hd.GAMES_PLAYED)))) + 16
        elo_gain = k_val * \
            (player_score - (1 / (1 + 10 ** ((opponent_elo - self.elo) / 400))))
        self.elo += elo_gain
        hd.update_elo(self.username, self.elo)

    def is_in_room(self) -> bool:
        """
        return True if the user is in a room.
        """
        return self.room is not None

    def exit_room(self):
        """
        this function is called when the game ends.
        """
        self.room = None

    def enter_room(self, room):
        """
        set the room of the user.
        """
        self.room = room


WAITING_ROOM: list[Client] = []
CLIENTS: list[Client] = []


def add_client(username: str, sid: str) -> None:
    """
    add a new client to the CLIENTS list.
    """
    CLIENTS.append(Client(username, sid))


def get_client(sid: str = None, username: str = None) -> Client | None:
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
    return None


def get_oppoent(client: Client) -> Client:
    """
    get the opponent of the given client.
    """
    return get_client(username=client.room.opponent(client.username))


def close_room(client: Client) -> None:
    """
    this function removes the room of the given player from the CHESS_ROOMS list.
    """
    if not is_engine_room(client.room):
        get_oppoent(client).exit_room()
    CHESS_ROOMS.remove(client.room)
    client.exit_room()


def is_engine_room(room: EngineRoom | PlayerRoom) -> bool:
    """
    return True if room is a engine room.
    """
    return isinstance(room, EngineRoom)


def add_engine_room(player: Client, level: int = 10, limit: int = 10, bonus: int = 0) -> EngineRoom:
    """
    add a new engine room to the CHESS_ROOMS list.
    """
    room = EngineRoom(player.username, level, limit, bonus)
    CHESS_ROOMS.append(room)
    player.enter_room(room)
    return room


def add_player_room(player1: Client, player2: Client, limit: int = 10, bonus:int = 0) -> PlayerRoom:
    """
    add a player room to the CHESS_ROOMS list.
    """
    room = PlayerRoom(player1.username, player2.username,
                      limit, bonus)
    CHESS_ROOMS.append(room)
    hd.update_games_played(player1.username)
    hd.update_games_played(player2.username)
    player1.enter_room(room)
    player2.enter_room(room)
    return room


def update_elo(score_dict: dict[Client, str]):
    """
    RatA + K * (score - (1 / (1 + 10**((RatB - RatA)/400))))
    K = 400 / games_played + 16
    """
    player1, player2 = tuple(score_dict.keys())
    player1_elo, player2_elo = player1.elo, player2.elo
    player1_score, player2_score = score_dict[player1], score_dict[player2]
    player1.update_elo(player2_elo, player1_score)
    player2.update_elo(player1_elo, player2_score)
