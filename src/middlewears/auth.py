from fastapi import HTTPException, status
from ..models.user import Roll, User

from ..repositories.accounts import UserRepository

repo = UserRepository()

def get_user(chess_cookie: str) -> User:

    user = repo.get_user_by_cookie(chess_cookie)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


def get_admin(chess_cookie: str) -> User:
    user = repo.get_user_by_cookie(chess_cookie)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if user.role != Roll.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user
