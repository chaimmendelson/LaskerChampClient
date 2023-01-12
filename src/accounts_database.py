import psycopg

def executeQuery(query: str, args: tuple = None) -> psycopg.cursor:
    """
    Execute a SQL query on the database and return the cursor object.
    """
    try:
        with psycopg.connect("dbname=chess_users user=postgres password=132005", autocommit=True) as conn:
            return conn.execute(query, args)
    except Exception as e:
        print(f"Error: {e}")

def createTable(table_name: str, columns: list) -> None:
    """
    Create a new table with the given name and columns.
    """
    query = f"CREATE TABLE IF NOT EXISTS {table_name}({', '.join(columns)});"
    executeQuery(query)

def dropTable(table_name: str) -> None:
    """
    Drop the table with the given name if it exists.
    """
    executeQuery(f"DROP TABLE IF EXISTS {table_name};")

def resetTable(table_name: str, columns: list) -> None:
    """
    Reset the table with the given name and columns.
    """
    dropTable(table_name)
    createTable(table_name, columns)

def insertRow(table_name: str, columns: dict) -> None:
    """
    Insert a new row into the table with the given name and columns.
    """
    column_names = ', '.join(list(columns.keys()))
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table_name}({column_names}) VALUES({placeholders});"
    executeQuery(query, tuple(columns.values()))

def selectValue(table_name: str, column: str, where: str) -> any:
    """
    Select a value from the table with the given name and columns where the where clause is true.
    """
    query = f"SELECT {column} FROM {table_name} WHERE {where};"
    cursor = executeQuery(query)
    data = cursor.fetchone()
    cursor.close()
    if data:
        return data[0]
    return None
    

def updateValue(table_name: str, column:str, value:str, where: str) -> None:
    """
    Update a row in the table with the given name and updates where the where clause is true.
    """
    if value is None:
        value = 'current_timestamp'
    query = f"UPDATE {table_name} SET {column} = {value} WHERE {where};"
    executeQuery(query)

def deleteRow(table_name: str, where: str) -> None:
    """
    Delete a row from the table with the given name where the where clause is true.
    """
    query = f"DELETE FROM {table_name} WHERE {where};"
    executeQuery(query)

def main():
    pass

if __name__ == '__main__':
    main()



# import psycopg

# C_TYPE = 'type'
# C_LEN = 'len'
# C_CONSTRAINS = 'constrains'
# C_NAME = 'name'


# def execute(code, args=None)->psycopg.Cursor:
#     """
#     execute a sql code on the database.
#     """
#     with psycopg.connect("dbname=chess_users user=postgres password=132005", autocommit=True) as conn:
#         return conn.execute(code, args)



# def create_table(table, table_structer:list[dict])->None:
#     """
#     build a sql line of code to create a table from the column settings.
#     """
#     columns = ""
#     for column in table_structer:
#         columns += f"{column[C_NAME]} {column[C_TYPE]} "
#         if column.get(C_LEN):
#             columns += f"({column[C_LEN]}) "
#         columns += f"{column[C_CONSTRAINS]},\n"
#     execute(f"create table if not exists {table}({columns[:-2]});").close()


# def drop_table(table)->None:
#     """
#     send a sql line of code to drop the table
#     """
#     execute(f"drop table if exists {table};").close()


# def reset_table(table, table_structer)->None:
#     """
#     reset the table.
#     """
#     drop_table(table)
#     create_table(table, table_structer)


# def is_value_in_column(table, column, value)->bool:
#     """
#     try to get a value from the database, the database will return the value if it exists
#     and None if it does not.
#     """
#     cursor = execute(f"select * from {table} where {column} = '{value}';")
#     data = cursor.fetchone()
#     cursor.close()
#     return data is not None


# def delete_row(table, column, value)->None:
#     """
#     run a sql line of code to delete a user by username.
#     """
#     execute(f"delete from {table} where {column} = '{value}';").close()


# def insert_new_row(table, columns: dict) -> bool:
#     """
#     insert a new user to the database, the args will contain all the values that are not inserted 
#     with a specified value by default (for now only date values).
#     """
#     value_string = '%s, ' * (len(columns) - 1) + '%s'
#     execute(f"insert into {table}({', '.join(list(columns.keys()))})\
#               values({value_string});", tuple(columns.values())).close()


# def get_value(table, unique_column, unique_value, column) -> any:
#     """
#     get a value from the database for a username from a specified column.
#     """
#     cursor = execute(f"select {column} from {table} where {unique_column} = '{unique_value}';")
#     data = cursor.fetchone()
#     cursor.close()
#     if data:
#         return data[0]
#     return None


# def update_value(table, unique_column, unique_value, column, new_value='current_timestamp') -> None:
#     """
#     update a value for a specified username and column
#     """
#     execute(f"update {table} set {column} = '{new_value}'  where {unique_column} = '{unique_value}';").close()


# def main():
#     pass


# if __name__ == '__main__':
#     main()
