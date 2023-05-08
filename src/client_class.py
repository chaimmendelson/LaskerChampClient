from chess_rooms import *
import accounts_db as hd

class Client():
    """
    save the connection between the username and the sid.
    """

    def __init__(self, username: str, sid: str):
        self.username: str = username
        self.sid: str = sid
        # the room that the user is in.
        self.room: EngineRoom | PlayerRoom | None = None
        user_data = hd.get_user_data(hd.USERNAME, username, (hd.ELO, hd.GAMES_PLAYED, hd.ROLL))
        self.elo: float = user_data[hd.ELO] # type: ignore
        self.games_played: int = user_data[hd.GAMES_PLAYED] # type: ignore
        self.roll: str = user_data[hd.ROLL] # type: ignore

    def update_elo(self, opponent_elo: float, player_score: int):
        """
        calculate the new elo of the player.
        """
        k_val = (400 / self.games_played) + 16
        elo_gain = k_val * \
            (player_score - (1 / (1 + 10 ** ((opponent_elo - self.elo) / 400))))
        self.elo += elo_gain
        hd.update_value(self.username, hd.ELO, self.elo)

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
        hd.update_games_played(self.username)
    
    def elo_int(self):
        return round(self.elo)
    

CLIENTS: set[Client] = set()