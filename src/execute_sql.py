"""
send and receive data from the database.
"""
import psycopg
from psycopg import sql
import platform

def execute_query(query: sql.Composed, *args: str|tuple) -> psycopg.Cursor:
    """
    Execute a SQL query on the database and return the cursor object.
    """
    conn_str = "dbname=laskerchamp user=postgres password=postgres"
    conn: psycopg.Connection = psycopg.connect(conn_str, autocommit=True)
    args = args[0] if len(args) == 1 and isinstance(args[0], tuple) else args
    cursor = conn.execute(query, args)
    conn.close()
    return cursor


def create_table(table_name: str, columns: list[str]) -> None:
    """
    Create a new table with the given name and columns.
    """
    query = sql.SQL("CREATE TABLE IF NOT EXISTS {table_name} ({columns_l})").format(
        table_name=sql.Identifier(table_name),
        columns_l=sql.SQL(', ').join([sql.SQL(column) for column in columns])) # type: ignore
    execute_query(query)


def drop_table(table_name: str) -> None:
    """
    Drop the table with the given name if it exists.
    """
    execute_query(sql.SQL("DROP TABLE IF EXISTS {table_name};").format(
        table_name=sql.Identifier(table_name)))


def reset_table(table_name: str, columns: list) -> None:
    """
    Reset the table with the given name and columns.
    """
    drop_table(table_name)
    create_table(table_name, columns)


def insert_row(table_name: str, columns: dict) -> None:
    """
    Insert a new row into the table with the given name and columns.
    """
    names = list(columns.keys())
    query = sql.SQL("INSERT INTO {table} ({keys}) VALUES ({values})").format(
        table=sql.Identifier(table_name),
        keys=sql.SQL(', ').join(map(sql.Identifier, names)),
        values=sql.SQL(', ').join(sql.Placeholder() * len(names)))
    execute_query(query, tuple(columns.values()))


def select_values(table_name: str, column: str, value, columns: tuple) -> tuple:
    query = sql.SQL("SELECT {columns} FROM {table} WHERE {c} = {v};").format(
        columns=sql.SQL(', ').join(map(sql.Identifier, columns)),
        table=sql.Identifier(table_name),
        c=sql.Identifier(column),
        v=sql.Placeholder())
    cursor = execute_query(query, value)
    data = cursor.fetchone()
    cursor.close()
    return data # type: ignore
   
   
def does_exist(table_name: str, column: str, value) -> bool:
    """
    Check if a row exists in the table with the given name where the where clause is true.
    """
    query = sql.SQL("SELECT EXISTS(SELECT 1 FROM {table} WHERE {c} = {v});").format(
        table=sql.Identifier(table_name),
        c=sql.Identifier(column),
        v=sql.Placeholder())
    cursor = execute_query(query, value)
    data = cursor.fetchone()
    cursor.close()
    return False if data is None else data[0]

def update_value(table_name: str, s_column: str, s_value: str|None, column: str, value) -> None:
    """
    Update a row in the table with the given name and updates where the where clause is true.
    """
    if s_value is None:
        # set the value to current timestamp
        s_value = 'current_timestamp'
    query = sql.SQL("UPDATE {table} SET {s_c} = {s_v} WHERE {c} = {v};").format(
        table=sql.Identifier(table_name),
        s_c=sql.Identifier(s_column),
        s_v=sql.Placeholder(),
        c=sql.Identifier(column),
        v=sql.Placeholder())
    execute_query(query, s_value, value)


def delete_row(table_name: str, column:str, value) -> None:
    """
    Delete a row from the table with the given name where the where clause is true.
    """
    query = sql.SQL("DELETE FROM {table} WHERE {c} = {v};").format(
        table=sql.Identifier(table_name),
        c=sql.Identifier(column),
        v=sql.Placeholder())
    execute_query(query, value)


def row_count(table_name: str) -> int:
    """
    Get the number of users in the table with the given name.
    """
    query = sql.SQL("SELECT COUNT(*) FROM {table};").format(
        table=sql.Identifier(table_name))
    cursor = execute_query(query)
    data = cursor.fetchone()
    cursor.close()
    return 0 if data is None else data[0]