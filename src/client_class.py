from .chess_rooms import *
from .accounts_db import *

class Client():
    """
    save the connection between the username and the sid.
    """

    def __init__(self, username: str, sid: str):
        self.username: str = username
        self.sid: str = sid
        # the room that the user is in.
        self.room: EngineRoom | PlayerRoom | None = None
        user_data = get_user_data(USERNAME, username, (ELO, GAMES_PLAYED, ROLL))
        self.elo: float = user_data[ELO] # type: ignore
        self.games_played: int = user_data[GAMES_PLAYED] # type: ignore
        self.roll: str = user_data[ROLL] # type: ignore

    def update_elo(self, opponent_elo: float, player_score: int):
        """
        calculate the new elo of the player.
        """
        k_val = (400 / self.games_played) + 16
        elo_gain = k_val * \
            (player_score - (1 / (1 + 10 ** ((opponent_elo - self.elo) / 400))))
        self.elo += elo_gain
        update_value(self.username, ELO, self.elo)

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
            self.update_games_played()
        
    def update_games_played(self):
        self.games_played += 1
        update_games_played(self.username)
    
    def elo_int(self):
        return round(self.elo)
    

CLIENTS: set[Client] = set()