from sqlmodel import create_engine, SQLModel

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost/laskerchamp"

class PostgresClient:

    def __init__(self, conn_str: str):
        self.conn_str = conn_str
        self.engine = create_engine(conn_str, echo=True)

    def init_db(self):
        """
        Initialize the database by creating all tables.
        """
        SQLModel.metadata.create_all(self.engine)

    def drop_db(self):
        """
        Drop all tables in the database.
        """
        SQLModel.metadata.drop_all(self.engine)

    def reset_db(self):
        """
        Reset the database by dropping and re-creating all tables.
        """
        self.drop_db()
        self.init_db()
