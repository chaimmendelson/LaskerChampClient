"""
has all the functions that handle the users database.
"""
import hashlib
import secrets
from datetime import datetime
import re
import time
import requests
import execute_sql as db

# the name of the table.
TABLE_NAME = 'accounts'

# names of all columns.
USERNAME = 'username'
PASSWORD = 'password_hash'
EMAIL = 'email_address'
COOKIE = 'cookie'
ELO = 'elo'
GAMES_PLAYED = 'games_played'
LAST_ENTRY = 'last_entry'
CREATION_DATE = 'creation_date'
ROLL = 'roll'

# length settings.
MAX_USERNAME_L = 32
MAX_PASSWORD_L = 32
EMAIL_L = 320
COOKIE_L = 64

MIN_USERNAME_L = 3
MIN_PASSWORD_L = 8

HASH_LEN = 128

USER = 'user'
ADMIN = 'admin'
BLOCKED = 'blocked'
ROLLS = [USER, ADMIN, BLOCKED]
MAX_ROLL_L = max([len(roll) for roll in ROLLS])

# table structure.
STRUCTURE: list[str] = [
    f'{USERNAME} varchar({MAX_USERNAME_L}) unique not null primary key',
    f'{PASSWORD} varchar({HASH_LEN}) not null',
    f'{EMAIL} varchar({EMAIL_L}) unique not null',
    f'{COOKIE} varchar({COOKIE_L}) not null unique',
    f'{ELO} decimal not null',
    f'{GAMES_PLAYED} integer not null default 0',
    f'{ROLL} varchar({MAX_ROLL_L}) not null',
    f'{LAST_ENTRY} timestamp not null default now()',
    f'{CREATION_DATE} timestamp not null default now()',
]

SQL_CURRENT_TIME: str = 'now()'

# error codes.
INVALID_USERNAME: int = 471
INVALID_PASSWORD: int = 473
INVALID_EMAIL: int = 472

USERNAME_EXISTS: int = 481
EMAIL_EXISTS: int = 482


def var(string):
    """
    turn a string into a sql formatted variable.
    """
    return f"'{string}'"


def update_value(username: str, column: str, value) -> None:
    """
    change the value of the given column for the given username.
    """
    db.update_value(TABLE_NAME, column, value, USERNAME, username)


def get_value(username: str, column: str) -> str|int|float|datetime:
    """
    get the value of the given column for the given username.
    """
    return parse_values({column: db.select_values(TABLE_NAME, USERNAME, username, (column,))[0]})[column]


def does_exist(column: str, value: str) -> bool:
    """
    true if the given value exists in the given column.
    """
    return db.does_exist(TABLE_NAME, column, value)


def hash_pass(password: str) -> str:
    """
    use sha256 to hash the password to a length of 128.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def create_cookie(username: str):
    """
    create a new cookie with the given username by combining:
    1 - 32 random hex characters.
    2 - username hashed to 32 characters.
    """
    return f'{secrets.token_hex(16)}{hashlib.md5(username.encode()).hexdigest()}'


def is_username_valid(username: str) -> bool:
    """
    check if the username is valid by the rules specified:
    1 - username must be at least 3 characters and at most the length specified.
    2 - username must contain only letters and numbers.
    3 - the first character must be a letter.
    """
    if MIN_USERNAME_L <= len(username) <= MAX_USERNAME_L:
        if username.isalnum():
            return username[0].isalpha()
    return False


def is_password_valid(password: str) -> bool:
    """
    check if password is valid by the rules specified:
    1 - password must be at least 8 characters long and at most the length specified.
    2 - password must contain only letters and numbers.
    3 - password must containe at least one number and one lower case letter.
    """
    if MIN_PASSWORD_L <= len(password) <= MAX_PASSWORD_L:
        if password.isalnum():
            return any(char.isdigit() for char in password) and \
                any(char.islower() for char in password)
    return False


def is_email_valid(email: str) -> bool:
    """
    validate email via validation site,
    if it doesn't work the email will only be verfied via regex.
    """
    email_regex = r'^[\w.%+-]{1,64}@[A-Za-z\d.-]{1,253}\.[A-Z|a-z]{2,4}$'
    if not re.fullmatch(email_regex, email):
        return False
    return True
    # make a do while loop.
    while True:
        response = requests.get(
            url="https://isitarealemail.com/api/email/validate",
            params={'email': email},
            timeout=5,
        )
        if response.status_code == 429:
            time.sleep(1)
            continue
        if response.status_code == 403:
            return True
        return response.json().get('status') == "valid"


def is_cookie_valid(cookie: str) -> bool:
    """
    check if the given cookie is valid.
    """
    return len(cookie) == COOKIE_L and cookie.isalnum()
        

def validate_credentials(username: str, password: str, email: str) -> int:
    """
    validate the given credentials and return the appropriate error code.
    """
    if not is_username_valid(username):
        return INVALID_USERNAME
    if does_exist(USERNAME, username):
        return USERNAME_EXISTS
    if not is_password_valid(password):
        return INVALID_PASSWORD
    if not is_email_valid(email):
        return INVALID_EMAIL
    if does_exist(EMAIL, email):
        return EMAIL_EXISTS
    return 200

def create_new_user(username: str, password: str, email: str, elo: int=1200, roll: str=USER) -> None:
    """
    add a new user to the database after verifying the username and password
    (the email will be verfied later).
    """
    db.insert_row(TABLE_NAME, {
        USERNAME: username,
        PASSWORD: hash_pass(password),
        EMAIL: email,
        COOKIE: create_cookie(username),
        ELO: elo,
        ROLL: roll
    })


def get_user_data(column: str, value, columns) -> dict[str, str|int|float|datetime]:
    """
    get the data of the user with the given value in the given column.
    """
    return parse_values(dict(zip(columns, db.select_values(TABLE_NAME, column, value, columns))))


def delete_user(username: str) -> None:
    """
    calls delete_user to delete the user from the database
    """
    db.delete_row(TABLE_NAME, USERNAME, username)


def check_password(username: str, password: str) -> bool:
    """
    verfy the password by hashing it and comparing it against the acctual password.
    """
    return hash_pass(password) == get_value(username, PASSWORD)


def update_games_played(username: str) -> None:
    """
    add one to the games played value
    """
    update_value(username, GAMES_PLAYED, int(str(get_value(username, GAMES_PLAYED))) + 1)


def update_entry(username: str) -> None:
    """
    update entry value to current time, used upon user entry
    """
    update_value(username, LAST_ENTRY, SQL_CURRENT_TIME)


def get_username_by_cookie(cookie: str) -> str:
    """
    get the username from the database by his cookie
    """
    return db.select_values(TABLE_NAME, COOKIE, cookie, (USERNAME,))[0]


def reset_password(username: str) -> None:
    """
    reset the password to 'password'
    """
    update_value(username, PASSWORD, hash_pass('password'))


def reset_table():
    """
    reset the table and insert default users
    """
    db.reset_table(TABLE_NAME, STRUCTURE)
    create_new_user('chaim', 'test1234', 'chaimke2005@gmail.com', 1200, ADMIN)


def parse_values(data: dict) -> dict[str, str|int|float|datetime]:
    parsed_data = {}
    for key, value in data.items():
        if key == ELO:
            parsed_data[key] = float(value)
        elif key == GAMES_PLAYED:
            parsed_data[key] = int(value)
        elif key == LAST_ENTRY or key == CREATION_DATE:
            parsed_data[key] = datetime.fromisoformat(str(value))
        else:
            parsed_data[key] = str(value)
    return parsed_data
            

def get_user_count() -> int:
    """
    get the number of users in the database
    """
    return db.row_count(TABLE_NAME)


def test_validation():
    # test username validation
    assert is_username_valid('c' * (MAX_USERNAME_L + 1)) == False
    assert is_username_valid('c' * (MIN_USERNAME_L - 1)) == False
    assert is_username_valid('1' + 'c' * MIN_USERNAME_L) == False
    assert is_username_valid('c'  + '#' * MIN_USERNAME_L) == False
    assert is_username_valid('chaim') == True
    
    # test password validation
    assert is_password_valid('c' * (MAX_PASSWORD_L + 1) + '1') == False
    assert is_password_valid('c' * (MIN_PASSWORD_L - 2) + '1') == False
    assert is_password_valid('A' * MIN_PASSWORD_L + '1') == False
    assert is_password_valid('a' * MIN_PASSWORD_L) == False
    assert is_password_valid('a' * MIN_PASSWORD_L + '1 ') == False
    assert is_password_valid('a' * MIN_PASSWORD_L + '1') == True
    
    # test email validation
    assert is_email_valid('chaimke2005@gmail.com') == True
    
    print('validation tests passed')
     
    
def test():
    username, password, email = 'test', 'test1234', 'chaimm2005@gmail.com'
    delete_user(username)
    
    # test creation of new user
    assert validate_credentials(username, password, email) == 200
    create_new_user(username, password, email)
    
    # test getting values
    assert get_value(username, PASSWORD) == hash_pass(password)
    assert get_user_data(USERNAME, username, (GAMES_PLAYED,))[GAMES_PLAYED] == 0
    
    # test updating values
    update_value(username, ELO, 1500)
    assert get_value(username, ELO) == 1500
    
    # test update games played
    update_games_played(username)
    assert get_value(username, GAMES_PLAYED) == 1
    
    # test update entry
    update_entry(username)
    dates = get_user_data(USERNAME, username, (CREATION_DATE, LAST_ENTRY))
    reg, ent = dates[CREATION_DATE], dates[LAST_ENTRY]
    assert isinstance(reg, datetime) and isinstance(ent, datetime)
    assert reg < ent
    
    # test deleting user
    delete_user(username)
    assert does_exist(USERNAME, username) == False
    
    # if we got here, all tests passed
    print('all tests passed')

def main():
    reset_table()
    test()
    test_validation()

if __name__ == '__main__':
    main()