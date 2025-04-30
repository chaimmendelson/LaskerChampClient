from .execute_sql import PostgresClient

postgres = PostgresClient("postgresql+psycopg2://postgres:postgres@localhost/laskerchamp")