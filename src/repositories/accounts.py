from sqlmodel import Session, select
from ..db.execute_sql import PostgresClient
from ..models.user import User
from typing import Optional


class UserRepository:

    def __init__(self, db: PostgresClient):
        self.db = db
        self.db.init_db()

    def create_user(self, user: User) -> User:
        with Session(self.db.engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with Session(self.db.engine) as session:
            statement = select(User).where(User.id == user_id)
            return session.exec(statement).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        with Session(self.db.engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        with Session(self.db.engine) as session:
            statement = select(User).where(User.email_address == email)
            return session.exec(statement).first()

    def get_user_by_cookie(self, cookie: str) -> Optional[User]:
        with Session(self.db.engine) as session:
            statement = select(User).where(User.cookie == cookie)
            return session.exec(statement).first()

    def email_exists(self, email: str) -> bool:
        with Session(self.db.engine) as session:
            statement = select(User).where(User.email_address == email)
            return session.exec(statement).first() is not None

    def username_exists(self, username: str) -> bool:
        with Session(self.db.engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first() is not None

    def update_user(self, user: User) -> None:
        with Session(self.db.engine) as session:
            session.add(user)
            session.commit()

    def delete_user(self, user_id: int) -> None:
        with Session(self.db.engine) as session:
            user = self.get_user_by_id(user_id)
            if user:
                session.delete(user)
                session.commit()