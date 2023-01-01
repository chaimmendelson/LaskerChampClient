import re

import psycopg2 as pg2

import os_values
import requests


TABLE_NAME = 'accounts'

USERNAME = 'username'
PASSWORD = 'password_hash'
EMAIL = 'email_address'
COOKIE = 'cookie'
ELO = 'elo'
GAMES_PLAYED = 'games_played'
PERMISSIONS = 'permissions'
LAST_ENTRY = 'last_entry'
CREATION_DATE = 'creation_date'

C_TYPE = 'type'
C_LEN = 'len'
C_CONSTRAINS = 'constrains'

COLUMNS = {
    USERNAME:       {C_TYPE: 'string',      C_LEN: 32,   C_CONSTRAINS: 'unique not null primary key'},
    PASSWORD:       {C_TYPE: 'string',      C_LEN: 128,  C_CONSTRAINS: 'not null'},
    EMAIL:          {C_TYPE: 'email',       C_LEN: None, C_CONSTRAINS: 'unique not null'},
    #COOKIE:         {C_TYPE: 'string',      C_LEN: 128,  C_CONSTRAINS: 'not null unique'},
    ELO:            {C_TYPE: 'decimal',     C_LEN: None, C_CONSTRAINS: 'not null'},
    GAMES_PLAYED:   {C_TYPE: 'number',      C_LEN: None, C_CONSTRAINS: 'not null'},
    PERMISSIONS:    {C_TYPE: 'string',      C_LEN: 10,   C_CONSTRAINS: 'not null'},
    LAST_ENTRY:     {C_TYPE: 'timestamp',   C_LEN: None, C_CONSTRAINS: 'not null'},
    CREATION_DATE:  {C_TYPE: 'timestamp',   C_LEN: None, C_CONSTRAINS: 'not null'}
}

MANUALLY_MUTABLE_COLUMNS = [USERNAME, PASSWORD, EMAIL, ELO, GAMES_PLAYED, PERMISSIONS]
OWNER = 'owner'
ADMIN = 'admin'
USER = 'user'
BLOCKED = 'blocked'
PERMISSIONS_LIST = [OWNER, ADMIN, USER, BLOCKED]
COLUMNS_L = list(COLUMNS)

ERROR = 0
COMPLETE = 1
VALID = 1
ARGUMENTS_ERROR = 2
INVALID_COLUMN_ERROR = 3
INVALID_VALUE_ERROR = 4
ALREADY_EXISTS_ERROR = 5


def get_len(column)->int:
    return COLUMNS[column][C_LEN]


def get_type(column)->str:
    return COLUMNS[column][C_TYPE]


def get_constrains(column)->str:
    return COLUMNS[column][C_CONSTRAINS]

def execute(code)->pg2.cursor:
    connection = os_values.DB_CONN
    cursor = connection.cursor()
    cursor.execute(code)
    return cursor


def create_table()->None:
    c_type_dict = {'number': 'integer', 'string': 'varchar', 'serial': 'serial',
                   'email': 'text', 'timestamp': 'timestamp', 'decimal': 'decimal'}
    columns = ""
    for column in COLUMNS:
        columns += f"{column} {c_type_dict[get_type(column)]} "
        if get_len(column):
            columns += f"({get_len(column)})"
        columns += f"{get_constrains(column)},\n"
    execute(f"create table if not exists {TABLE_NAME}({columns[:-2]});").close()


def drop_table()->None:
    execute(f"drop table if exists {TABLE_NAME};").close()


def reset_table()->None:
    drop_table()
    create_table()


def is_value_in_column(column, value)->bool:
    cursor = execute(f"select * from {TABLE_NAME} where {column} = '{value}';")
    data = cursor.fetchone()
    cursor.close()
    return data is not None


def delete_user(username)->int:
    if is_value_in_column(USERNAME, username):
        execute(f"delete from {TABLE_NAME} where {USERNAME} = '{username}';").close()
        return COMPLETE
    return INVALID_VALUE_ERROR


def check_value(column, value)->int:
    if type(value) != str:
        return INVALID_VALUE_ERROR
    if get_type(column) == 'number':
        if not value.isdecimal():
            return INVALID_VALUE_ERROR
    if get_type(column) == 'decimal':
        try:
            float(value)
        except ValueError:
            return INVALID_VALUE_ERROR
    if get_len(column):
        if len(value) > get_len(column):
            return INVALID_VALUE_ERROR
    if not value:
        if 'not null' in get_constrains(column):
            return INVALID_VALUE_ERROR
    if 'unique' in get_constrains(column):
        if is_value_in_column(column, value):
            return ALREADY_EXISTS_ERROR
    if column == ELO:
        if not 0 < int(value) < 3500:
            return INVALID_VALUE_ERROR
    if column == PERMISSIONS:
        if value not in PERMISSIONS_LIST:
            return INVALID_VALUE_ERROR
    if get_type(column) == 'email':
        if not is_email_valid(value):
            return INVALID_VALUE_ERROR
    return VALID


def insert_new_user(user_data):
    if len(user_data) > len(MANUALLY_MUTABLE_COLUMNS) or len(user_data) < len(MANUALLY_MUTABLE_COLUMNS):
        return ARGUMENTS_ERROR, None
    for column, value in dict(zip(MANUALLY_MUTABLE_COLUMNS, user_data)).items():
        status = check_value(column, value)
        if status != VALID:
            return status, column
    temp = []
    x = 0
    for column in COLUMNS_L:
        if get_type(column) == 'timestamp':
            temp.append('current_timestamp')
        else:
            temp.append(f"'{user_data[x]}'")
            x += 1
    execute(f"insert into {TABLE_NAME}({', '.join(list(COLUMNS))}) values({', '.join(temp)});").close()
    return COMPLETE, None


def get_all_users()->list:
    columns = COLUMNS_L.copy()
    columns.remove(PASSWORD)
    cursor = execute(f"select {', '.join(columns)} from {TABLE_NAME};")
    data = cursor.fetchall()
    cursor.close()
    return data


def printable_table(table, columns):
    table.insert(0, columns)
    for i in range(len(table)):
        table[i] = list(table[i])
        for j in range(len(table[0])):
            table[i][j] = str(table[i][j])
    for i in range(len(table[0])):
        longest = 0
        for row in table:
            if len(row[i]) > longest:
                longest = len(row[i])
        longest += 2
        for j in range(len(table)):
            table[j][i] += ' ' * (longest - len(table[j][i]))
    data = ""
    for line in table:
        data += ' | '.join(line) + '\n'
    return data[:-1]


def is_email_valid(email):
    email_regex = r'^[\w.%+-]{1,64}@[A-Za-z\d.-]{1,253}\.[A-Z|a-z]{2,4}$'
    if re.fullmatch(email_regex, email):
        try:
            response = requests.get("https://isitarealemail.com/api/email/validate", params={'email': email})
            status = response.json()['status']
            return status == "valid"
        except:
            return True
    return False


def get_value(username, column):
    if is_value_in_column(USERNAME, username) and column in COLUMNS:
        cursor = execute(f"select {column} from {TABLE_NAME} where {USERNAME} = '{username}';")
        data = cursor.fetchone()
        cursor.close()
        if data:
            return data[0]
    return None


def update_value(username, column, new_value):
    if column in MANUALLY_MUTABLE_COLUMNS:
        if is_value_in_column(USERNAME, username):
            if check_value(column, new_value):
                execute(f"update {TABLE_NAME} set {column} = '{new_value}'  where {USERNAME} = '{username}';").close()
                return COMPLETE
        return INVALID_VALUE_ERROR
    return INVALID_COLUMN_ERROR


def update_entry(username):
    if is_value_in_column(USERNAME, username):
        execute(f"update {TABLE_NAME} set {LAST_ENTRY} = current_timestamp  where {USERNAME} = '{username}';").close()
        return True
    return INVALID_VALUE_ERROR


def main():
    os_values.set_database_conn()
    columns = COLUMNS_L.copy()
    columns.remove(PASSWORD)
    print(printable_table(get_all_users(), columns))


if __name__ == '__main__':
    main()
