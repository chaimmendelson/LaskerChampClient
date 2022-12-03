import socketio
from aiohttp import web
import secrets
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
CLIENTS = []
COOKIE_NAME = 'chess-cookie'
class Clients():
    def __init__(self, username, cookie, sid=None):
        self.username = username
        self.cookie = cookie
        self.sid = sid
    
    def set_sid(self, sid):
        self.sid = sid

def does_cookie_exist(cookie):
    for client in CLIENTS:
        if client.cookie == cookie:
            return True
    return False

def create_cookie():
    cookie = secrets.token_hex(16)
    while does_cookie_exist(cookie):
        cookie = secrets.token_hex(16)
    return cookie


async def task(sid):
    await sio.sleep(5)
    resault = await sio.call('mult', {'numbers': [2, 3]}, to=sid)
    print(resault)

async def login_page(request):
    """Serve the client-side application."""
    print(request)
    with open('src/login.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

async def game_page(request):
    """Serve the client-side application."""
    print(request)
    with open('src/client.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.event
async def connect(sid, environ, auth):
    if auth:
        if 'token' in auth:
            token = auth['token']
            print(token)
            if does_cookie_exist(token):
                for client in CLIENTS:
                    if client.cookie == token:
                        client.set_sid(sid)
                        print("connect ", sid)
                        return True
    return False
    # sio.start_background_task(task, sid)

@sio.event
async def disconnect(sid):
    global CLIENTS   
    print('disconnect ', sid)
    if sid in CLIENTS:
        CLIENTS.remove(sid)


async def login_validation(request: web.Request):
    headers = request.headers
    if request.method == 'POST':
        if request.body_exists:
            data = await request.json()
            if 'username' in data and 'password' in data:
                if data['username'] == 'test' and data['password'] == 'test':
                    cookie = create_cookie()
                    CLIENTS.append(Clients(data['username'], cookie))
                    cookie = f'{COOKIE_NAME}={cookie}'
                    return web.json_response({'status': 'ok', 'set-cookie': cookie, 'redirect': '/'})
        return web.json_response({'status': 'error'})
    cookie = headers.get(COOKIE_NAME)
    if cookie:
        if does_cookie_exist(cookie):
            return web.Response()
    return(web.Response(status=401))

app.add_routes([web.get('/', game_page),
                web.get('/login', login_page),
                web.post('/validate', login_validation),
                web.get('/validate', login_validation),
                web.static('/scripts', 'src/scripts'),
                web.static('/styles', 'src/styles'),
                web.static('/images', 'src/images')])

if __name__ == '__main__':
    web.run_app(app, port=8000)