import psycopg

def execute_query(query: str, args: tuple = None) -> psycopg.cursor:
    """
    Execute a SQL query on the database and return the cursor object.
    """
    try:
        with psycopg.connect("dbname=chess_users user=postgres password=132005", autocommit=True) as conn:
            return conn.execute(query, args)
    except Exception as e:
        print(f"Error: {e}")

def create_table(table_name: str, columns: list) -> None:
    """
    Create a new table with the given name and columns.
    """
    query = f"CREATE TABLE IF NOT EXISTS {table_name}({', '.join(columns)});"
    execute_query(query)

def drop_table(table_name: str) -> None:
    """
    Drop the table with the given name if it exists.
    """
    execute_query(f"DROP TABLE IF EXISTS {table_name};")

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
    column_names = ', '.join(list(columns.keys()))
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table_name}({column_names}) VALUES({placeholders});"
    execute_query(query, tuple(columns.values()))

def select_value(table_name: str, column: str, where: str) -> any:
    """
    Select a value from the table with the given name and columns where the where clause is true.
    """
    query = f"SELECT {column} FROM {table_name} WHERE {where};"
    cursor = execute_query(query)
    data = cursor.fetchone()
    cursor.close()
    if data:
        return data[0]
    return None
    

def update_value(table_name: str, column:str, value:str, where: str) -> None:
    """
    Update a row in the table with the given name and updates where the where clause is true.
    """
    if value is None:
        value = 'current_timestamp'
    query = f"UPDATE {table_name} SET {column} = {value} WHERE {where};"
    execute_query(query)

def delete_row(table_name: str, where: str) -> None:
    """
    Delete a row from the table with the given name where the where clause is true.
    """
    query = f"DELETE FROM {table_name} WHERE {where};"
    execute_query(query)

def main():
    pass

if __name__ == '__main__':
    main()
