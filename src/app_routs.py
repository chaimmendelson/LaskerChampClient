"""
function to handle the routes of the app
"""
import sys

from src.accounts_db import is_cookie_valid, does_exist, COOKIE, get_username_by_cookie, get_value, ROLL, ADMIN, \
    is_username_valid, is_password_valid, USERNAME, check_password, validate_credentials, create_new_user
from src.handle_clients import is_client_connected

sys.path.append('./')
from datetime import datetime, timedelta
from aiohttp import web
from .stats import *
COOKIE_NAME: str = 'chess-cookie'

USER_lOGGED_IN: int = 490
INVALID_CREDENTIALS: int = 491

async def get_stats(request: web.Request) -> web.Response:
    return web.json_response(dict(stats=get_overall_stats()))


async def admin(request: web.Request) -> web.Response:
    # print the cookie
    cookie = request.cookies.get(COOKIE_NAME)
    if cookie is None:
        return web.Response(status=302, headers={'Location': '/'})
    roll = get_value(get_username_by_cookie(cookie), ROLL)
    if roll != ADMIN:
        return web.Response(status=302, headers={'Location': '/'})
    with open('src/pages/admin.html', encoding='utf-8') as admin_page:
        return web.Response(text=admin_page.read(), content_type='text/html')


async def game_page(request: web.Request):
    """
    Serve the client-side application.
    """
    cookies = request.cookies
    if COOKIE_NAME in cookies:
        cookie = cookies[COOKIE_NAME]
        if is_cookie_valid(cookie) and does_exist(COOKIE, cookie):
            if not is_client_connected(username=get_username_by_cookie(cookie)):
                with open('src/pages/client.html', encoding='utf-8') as main_page:
                    return web.Response(text=main_page.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})


async def login(request: web.Request):
    """
    Serve the client-side application.
    """
    with open('src/pages/login.html', encoding='utf-8') as login_page:
        return web.Response(text=login_page.read(), content_type='text/html')


async def register(request: web.Request):
    """
    Serve the client-side application.
    """
    with open('src/pages/register.html', encoding='utf-8') as register_page:
        return web.Response(text=register_page.read(), content_type='text/html')
    

    
async def login_validation(request: web.Request):
    """
    validate login.
    """
    if not request.body_exists:
        return web.json_response({'status': 400})
    data = await request.json()
    if not ('username' in data and 'password' in data):
        return web.json_response({'status': 400})
    username, password = data.get('username'), data.get('password')
    if not (is_username_valid(username) and is_password_valid(password)):
        return web.json_response({'status': 400})
    if does_exist(USERNAME, username):
        if check_password(username, password):
            if not is_client_connected(username):
                response = web.json_response({'status': 200})
                expires = datetime.now() + timedelta(days=365*10)
                expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
                response.set_cookie(
                    COOKIE_NAME, str(get_value(username, COOKIE)), expires=expires, httponly=False, secure=False)
                return response
            return web.json_response({'status': USER_lOGGED_IN})
    return web.json_response({'status': INVALID_CREDENTIALS})


async def sign_up(request: web.Request):
    """
    sign up.
    """
    code = 400
    if request.body_exists:
        data = await request.json()
        username, password, email = data.get('username'), data.get('password'), data.get('email')
        if username is not None and password is not None and email is not None:
            code = validate_credentials(username, password, email)
            if code == 200:
                create_new_user(username, password, email)
                update_stat(NEW_ACCOUNTS)
    return web.json_response({'status': code})



async def pong(request: web.Request):
    """
    Serve the client-side application.
    """
    return web.json_response(text='pong')
