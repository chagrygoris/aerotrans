import logging
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from databaza import session, User, already_registered
from fastapi import Request, Query
logging.basicConfig(filename='logs', filemode='w')
logging.getLogger().setLevel(logging.INFO)
from telegram_bot import registration
app = FastAPI()
templates = Jinja2Templates(directory="templates")

class UserRequest(BaseModel):
    name: str
    age: int
    telegram_id: int


@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/sign_up", response_class=HTMLResponse)
async def sign_up(request: Request):
    return templates.TemplateResponse("telegram_widget.html", {
        "request": request
    })

# server with the app to get info from TelegramAPI: https://5370-185-200-105-117.ngrok-free.app/


@app.get("/sign_up/telegram", response_class=HTMLResponse)
async def telegram_auth(request: Request, id: int = Query(...)):
    global global_telegram_id # may be changed with request.session ???
    global_telegram_id = id
    return RedirectResponse(url="/sign_up/form")


@app.get("/sign_up/form", response_class=HTMLResponse)
async def sign_up_form(request: Request):
    return templates.TemplateResponse("form.html", {
        "request": request
    })


@app.post("/success/", response_class=HTMLResponse)
async def create_user(request: Request, name: str = Form(), email: str = Form()):
    if already_registered(name, email, global_telegram_id): # optional as it duplicates unique=True in telegram_id Column
        return HTMLResponse(status_code=404, content="Bad Request")
    user = User(name=name, email=email, telegram_id=global_telegram_id)
    session.add(user)
    session.commit()
    logging.info(f"User {name} with email {email} and Telegram ID {global_telegram_id} has signed up")
    registration.send_welcome_message(user.telegram_id, user.name)
    return templates.TemplateResponse("result.html", {
        "request": request
    })
