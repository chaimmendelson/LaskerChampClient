from src.repositories.accounts import UserRepository
from ..schemas.user import UserRequest, LoginRequest
from ..models.user import User

class userService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, user: UserRequest) -> User:
        """
        Create a new user in the database.
        """
        new_user = User(
            username=user.username,
            email_address=user.email_address,
            password=user.password,
            cookie=user.cookie,
            elo=user.elo,
            games_played=user.games_played
        )