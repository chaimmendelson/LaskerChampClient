from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum


class Roll(str, Enum):
    USER = "user"
    ADMIN = "admin"
    BLOCKED = "blocked"


MAX_USERNAME_L = 32
MAX_PASSWORD_L = 32
EMAIL_L = 320
COOKIE_L = 64
HASH_LEN = 128
MAX_ROLL_L = max(len(r.value) for r in Roll)


class User(SQLModel, table=True):
    __tablename__ = "accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, max_length=MAX_USERNAME_L, unique=True)
    password_hash: str = Field(max_length=HASH_LEN)
    email_address: str = Field(max_length=EMAIL_L, unique=True)
    cookie: str = Field(max_length=COOKIE_L, unique=True)
    elo: float = Field(default=1200)
    games_played: int = Field(default=0)
    roll: Roll = Field(default=Roll.USER, max_length=MAX_ROLL_L)
    last_entry: datetime = Field(default_factory=datetime.utcnow)
    creation_date: datetime = Field(default_factory=datetime.utcnow)

