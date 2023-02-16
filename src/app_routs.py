"""
function to handle the routes of the app
"""
from aiohttp import web
import handle_database as hd
import connected as con

COOKIE_NAME: str = 'chess-cookie'

async def game_page(request: web.Request):
    """
    Serve the client-side application.
    """
    print(request)
    cookies = request.cookies
    if COOKIE_NAME in cookies:
        cookie = cookies[COOKIE_NAME]
        if hd.does_exist(hd.COOKIE, cookie):
            if not con.get_client(username=hd.get_username_by_cookie(cookie)):
                with open('src/pages/client.html', encoding='utf-8') as main_page:
                    return web.Response(text=main_page.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})


async def login(request: web.Request):
    """
    Serve the client-side application.
    """
    print(request)
    with open('src/pages/login.html', encoding='utf-8') as login_page:
        return web.Response(text=login_page.read(), content_type='text/html')


async def register(request: web.Request):
    """
    Serve the client-side application.
    """
    print(request)
    with open('src/pages/register.html', encoding='utf-8') as register_page:
        return web.Response(text=register_page.read(), content_type='text/html')


async def login_validation(request: web.Request):
    """
    validate login.
    """
    print(request)
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data:
            username = data.get('username')
            password = data.get('password')
            if hd.does_exist(hd.USERNAME, username):
                if hd.check_password(username, password):
                    if not con.get_client(username=username):
                        response = web.json_response({'status': 'ok'})
                        response.set_cookie(
                            COOKIE_NAME, hd.get_value(username, hd.COOKIE))
                        return response
    return web.json_response({'status': 'error'})


async def sign_up(request: web.Request):
    """
    sign up.
    """
    print(request)
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data and 'email' in data:
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            return web.json_response({'status': hd.create_new_user(username, password, email)})
    return web.json_response({'status': 400})


async def pong(request: web.Request):
    """
    Serve the client-side application.
    """
    print(request)
    return web.json_response({'status': 'ok'}, text='pong')
