import hashlib
import secrets
import accounts_database as db
from datetime import datetime
import re
import requests


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

# length settings.
MAX_USERNAME_L = 32
MAX_PASSWORD_L = 32
EMAIL_L = 320
COOKIE_L = 64

MIN_USERNAME_L = 3
MIN_PASSWORD_L = 8

HASH_LEN = 128

# table structure.
STRUCTURE = [
    f'{USERNAME} varchar({MAX_USERNAME_L}) unique not null primary key',
    f'{PASSWORD} varchar({HASH_LEN}) not null',
    f'{EMAIL} varchar({EMAIL_L}) unique not null',
    f'{COOKIE} varchar({COOKIE_L}) not null unique',
    f'{ELO} decimal not null',
    f'{GAMES_PLAYED} integer not null default 0',
    f'{LAST_ENTRY} timestamp not null default now()',
    f'{CREATION_DATE} timestamp not null default now()'
]

SQL_CURRENT_TIME = 'current_timestamp'

def var(string): return f"'{string}'"


def update_value(username, column, value) -> None:
    db.update_value(TABLE_NAME, column, value, f"{USERNAME} = '{username}'")


def get_value(username, column) -> str:
    return db.select_value(TABLE_NAME, column, f"{USERNAME} = '{username}'")


def does_exist(column, value) -> bool:
    return db.select_value(TABLE_NAME, '*', f"{column} = '{value}'") != None


def hash(password)->str:
    """
    use sha512 to hash the password to a length of 128.
    """
    return hashlib.sha512(password.encode()).hexdigest()


def create_cookie(username):
    """
    create a new cookie with the given username by combining:
    1 - 32 random hex characters.
    2 - username hashed to 32 characters.
    """
    return f'{secrets.token_hex(16)}{hashlib.md5(username.encode()).hexdigest()}'


def is_username_valid(username) -> bool:
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


def is_password_valid(password) -> bool:
    """
    check if password is valid by the rules specified:
    1 - password must be at least 8 characters long and at most the length specified.
    2 - password must contain only letters and numbers.
    3 - password must containe at least one number and one lower case letter.
    """
    if MIN_PASSWORD_L <= len(password) <= MAX_PASSWORD_L:
        if password.isalnum():
            return any(char.isdigit() for char in password) and any(char.islower() for char in password)
    return False


def is_email_valid(email) -> bool:
    """
    validate email via validation site, when it doesn't work the email will only be verfied via regex.
    """
    email_regex = r'^[\w.%+-]{1,64}@[A-Za-z\d.-]{1,253}\.[A-Z|a-z]{2,4}$'
    if re.fullmatch(email_regex, email):
        try:
            response = requests.get("https://isitarealemail.com/api/email/validate", params={'email': email})
            status = response.json()['status']
            return status == "valid"
        except:
            return True
    return False


def create_new_user(username, password, email) -> bool:
    """
    add a new user to the database after verifying the username and password
    (the email will be verfied later).
    """
    if not is_username_valid(username):
        return "invalid username"
    if does_exist(USERNAME, username):
        return "username already exists"
    if not is_password_valid(password):
        return "invalid password"
    if not is_email_valid(email):
        return "invalid email"
    if does_exist(EMAIL, email):
        return "email already exists"
    db.insert_row(TABLE_NAME, {
        USERNAME: username,
        PASSWORD: hash(password),
        EMAIL: email,
        COOKIE: create_cookie(username),
        ELO: '1200'
    })
    return "created successfully"


def delete_user(username) -> None:
    """
    calls delete_user to delete the user from the database
    """
    db.delete_row(TABLE_NAME, f"{USERNAME} = {var(username)}")


def check_password(username, password) -> bool:
    """
    verfy the password by hashing it and comparing it against the acctual password.
    """
    return hash(password) == get_value(username, PASSWORD)


"""
update functions, all require the password.
"""


def update_username(username, new_username) -> bool:
    """
    if the new username is valid, it will be updated
    """
    if is_username_valid(username):
        update_value(username, USERNAME, var(new_username))
        return True
    return False


def update_password(username, old_password, new_password) -> bool:
    """
    if the new password is valid, it will be updated
    """
    if check_password(username, old_password) and is_password_valid(new_password):
        update_value(username, PASSWORD, var(hash(new_password)))
        return True
    return False


def update_email(username, password, new_email) -> bool:
    """
    if the new email is valid, it will be updated
    """
    if check_password(username, password):
        update_value(username, EMAIL, var(new_email))
        return True
    return False


def update_elo(username, new_elo) -> None:
    """
    if the new elo is valid, it will be updated
    """
    update_value(username, ELO, new_elo)


def update_games_played(username) -> None:
    """
    add one to the games played value
    """
    update_value(username, GAMES_PLAYED, int(get_value(username, GAMES_PLAYED)) + 1)


def update_entry(username) -> None:
    """
    update entry value to current time, used upon user entry
    """
    update_value(username, LAST_ENTRY, SQL_CURRENT_TIME)


"""
get functions
"""
def get_username_by_cookie(cookie):
    return db.select_value(TABLE_NAME, USERNAME, f'{COOKIE} = {var(cookie)}')


def get_entry(username) -> datetime.strftime:
    """
    get the last entry time from the database and convert it from sql format to datetime format
    """
    entry = datetime.fromisoformat(str(get_value(username, LAST_ENTRY)))
    return entry.strftime("(%d/%m/%y, %H:%M:%S)")


def get_creation_date(username) -> datetime.strftime:
    """
    get the user creation time from the database and convert it from sql format to datetime format
    """
    creation = datetime.fromisoformat(str(get_value(username, LAST_ENTRY)))
    return creation.strftime("(%d/%m/%y, %H:%M:%S)")


"""
reset functions
"""
def reset_password(username) -> bool:
    """
    reset the password to 'default'
    """
    return update_value(username, PASSWORD, hash('default'))


def reset_table():
    """
    reset the table and insert default users
    """
    db.reset_table(TABLE_NAME, STRUCTURE)


def test():
    username = 'test1'
    password = 'test12345'
    delete_user(username)
    create_new_user(username, password, 'chaimm2005@gmail.com')

    update_elo(username, 1300)
    assert get_value(username, ELO) == 1300

    update_password(username, password, 'test123456')
    assert get_value(username, PASSWORD) == hash('test123456')

    password = 'test123456'
    pass


def main():
    reset_table()
    create_new_user('test', 'test1234', 'chaimm2005@gmail.com')
    create_new_user('test1', 'test1234', 'chaimke2005@gmail.com')

if __name__ == '__main__':
    main()
