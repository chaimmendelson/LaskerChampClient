from .user import User
from .chess_room import EngineRoom, PlayerRoom


class Client:
    """
    save the connection between the username and the sid.
    """

    def __init__(self, user: User, sid: str):
        self.user = user
        self.sid: str = sid
        self.room: EngineRoom | PlayerRoom | None = None

    def update_elo(self, opponent_elo: float, player_score: int):
        """
        calculate the new elo of the player.
        """
        k_val = (400 / self.user.games_played) + 16
        elo_gain = k_val * \
            (player_score - (1 / (1 + 10 ** ((opponent_elo - self.user.elo) / 400))))
        self.user.elo += elo_gain

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
        if isinstance(room, PlayerRoom):
            self.user.games_played += 1

    def elo_int(self):
        return round(self.user.elo)

CLIENTS: set[Client] = set()