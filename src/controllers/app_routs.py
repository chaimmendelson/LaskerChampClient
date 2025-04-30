import os

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from datetime import datetime, timedelta

from starlette import status

from src.handle_clients import is_client_connected
from ..middlewears import auth
from ..models.user import User
from ..stats import stats

app = FastAPI()
COOKIE_NAME = "chess-cookie"

templates = os.path.join(os.path.dirname(__file__), "../../client/templates")

@app.get("/admin")
async def render_admin_page(user: User = Depends(auth.get_admin)) -> HTMLResponse:
    path = os.path.join(templates, "admin.html")

    with open(path, encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/game")
async def serve_game_page(user: User = Depends(auth.get_user)) -> HTMLResponse|RedirectResponse:
    path = os.path.join(templates, "client.html")

    if not is_client_connected(username=user.username):
        with open(path, encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    return RedirectResponse(url="/login")



@app.get("/login")
async def serve_login_page() -> HTMLResponse:
    path = os.path.join(templates, "login.html")

    with open(path, encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/register")
async def serve_register_page():
    path = os.path.join(templates, "register.html")

    with open(path, encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/login")
async def handle_login_validation(request: Request):

    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if not (username and password):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)
    if not (is_username_valid(username) and is_password_valid(password)):
        return JSONResponse(content={"status": 400})

    if does_exist(USERNAME, username) and check_password(username, password):
        if not is_client_connected(username=username):
            cookie_value = get_value(username, COOKIE)
            expires = (datetime.utcnow() + timedelta(days=365 * 10)).strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
            response = JSONResponse(content={"status": 200})
            response.set_cookie(key=COOKIE_NAME, value=cookie_value, expires=expires)
            return response
        return JSONResponse(content={"status": USER_ALREADY_LOGGED_IN})

    return JSONResponse(content={"status": BAD_CREDENTIALS})


@app.post("/api/signup")
async def handle_user_signup(request: Request):
    if not request.headers.get("content-type") == "application/json":
        return JSONResponse(content={"status": 400})

    data = await request.json()
    username, password, email = data.get("username"), data.get("password"), data.get("email")

    if not (username and password and email):
        return JSONResponse(content={"status": 400})

    status = validate_credentials(username, password, email)
    if status == 200:
        create_new_user(username, password, email)
        update_stat(NEW_ACCOUNTS)

    return JSONResponse(content={"status": status})


@app.get("/api/stats")
async def fetch_game_statistics():
    return {"stats": stats.get_overall_stats()}

@app.get("/ping")
async def ping_pong():
    return JSONResponse(content={"text": "pong"})
