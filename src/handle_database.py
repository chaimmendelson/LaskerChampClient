import hashlib
import timeit
import accounts_database as db
from datetime import datetime

import os_values


def hash(password)->str:
    return hashlib.sha512(password.encode()).hexdigest()


def return_username_error(username) -> str|int:
    if type(username) == str:
        if 3 <= len(username) <= db.get_len(db.USERNAME):
            if username.isalnum():
                if username[0].isalpha():
                    return db.VALID
                return 'username must start with a letter'
            return 'username must contain only numbers and letters'
        return 'username must be at least 3 digits and no more then 32 digits'
    return 'username must be a string'


def is_username_valid(username):
    return return_username_error(username) == db.VALID


def return_password_error(password):
    if type(password) == str:
        if 8 <= len(password) <= db.get_len(db.USERNAME):
            if password.isalnum():
                if any(char.isdigit() for char in password) and any(char.islower() for char in password):
                    return db.VALID
                return 'password must contain at least one number and one letter'
            return 'password must contain only numbers and letters'
        return 'password must be at least 8 digits and no more then 32 digits'
    return 'password must be a string'


def is_password_valid(password):
    return return_password_error(password) == db.VALID


def is_email_valid(email):
    if db.is_email_valid(email):
        return db.VALID
    return 'invalid email'


def create_new_user(username, password, email):
    if is_username_valid(username) == db.VALID:
        if is_password_valid(password) == db.VALID:
            status, column = db.insert_new_user([username, hash(password), email, '1200', '0', db.USER])
            if status == db.VALID:
                return "account created"
            if status == db.INVALID_VALUE_ERROR:
                return f"invalid email"
            if status == db.ALREADY_EXISTS_ERROR:
                return f"{column} already exists"
        return return_password_error(password)
    return return_username_error(username)


def delete_user(username):
    if does_username_exist(username):
        db.delete_user(username)
        return True
    return False


def check_password(username, password):
    return hash(password) == db.get_value(username, db.PASSWORD)


def does_username_exist(username):
    return db.is_value_in_column(db.USERNAME, username)


def update_username(username, password, new_username):
    if check_password(username, password):
        if is_username_valid(username):
            db.update_value(username, db.USERNAME, new_username)
            return True
    return False


def update_password(username, old_password, new_password):
    if check_password(username, old_password):
        db.update_value(username, db.PASSWORD, hash(new_password))
        return True
    return False


def update_email(username, password, new_email):
    if check_password(username, password):
        db.update_value(username, db.EMAIL, new_email)
        return True
    return False


def get_email(username):
    return db.get_value(username, db.EMAIL)


def update_elo(username, new_elo):
    return db.update_value(username, db.ELO, new_elo)


def get_elo(username):
    return db.get_value(username, db.ELO)


def update_games_played(username, add):
    return db.update_value(username, db.GAMES_PLAYED, get_games_played(username) + add)


def get_games_played(username):
    return db.get_value(username, db.GAMES_PLAYED)


def update_entry(username):
    return db.update_entry(username)


def get_entry(username):
    entry = db.get_value(username, db.LAST_ENTRY)
    if entry:
        entry = datetime.fromisoformat(str(entry))
        return entry.strftime("(%d/%m/%y, %H:%M:%S)")
    return None


def get_creation_date(username):
    creation = db.get_value(username, db.LAST_ENTRY)
    if creation:
        creation = datetime.fromisoformat(str(creation))
        return creation.strftime("(%d/%m/%y, %H:%M:%S)")
    return None


def reset_password(username):
    if does_username_exist(username):
        db.update_value(username, db.PASSWORD, hash('default'))
        return True
    return False


def get_permission(username):
    return db.get_value(username, db.PERMISSIONS)


def is_owner(username):
    if does_username_exist(username):
        if get_permission(username) == db.OWNER:
            return True
    return False


def is_admin(username):
    if does_username_exist(username):
        if get_permission(username) in [db.ADMIN, db.OWNER]:
            return True
    return False


def get_owner_password():
    text = hashlib.sha384('the python'.encode()).hexdigest()
    password = ''
    for i in range(0, len(text), 4):
        password += text[i]
    return password


def create_owner():
    name = 'python'
    create_new_user(name, get_owner_password(), 'chaimke2005@gmail.com')
    db.update_value(name, db.PERMISSIONS, db.OWNER)


def reset_table():
    db.reset_table()
    create_owner()
    create_new_user('aviad', 'aviad12344', 'aviad.bagno@gmail.com')
    create_new_user('test', 'test12345', 'chaimm2005@gmail.com')


def test():
    """delete_user('test')
    create_new_user('test', 'test', 'chaimm2005@gmail.com')
    start = timeit.default_timer()
    update_email('test', 'test', 'chaimke2005@gmail.com')
    stop = timeit.default_timer()
    print('Time: ', stop - start)
    print(db.printable_table(db.get_all_users()))"""
    os_values.set_database_conn()
    c = db.COLUMNS_L.copy()
    c.remove(db.PASSWORD)
    print(db.printable_table(db.get_all_users(), c))
    os_values.DB_CONN.close()
if __name__ == '__main__':
    test()
