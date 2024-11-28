import logging
from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from databaza import session, User, already_registered, TRequest

from searching_tool.get_info import get_flight_data
from searching_tool.view_results import create_rectangles

logging.basicConfig(filename='logs', filemode='w')
logging.getLogger().setLevel(logging.INFO)
from telegram_bot import registration



app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key="your-secret-key") # pycharm глупенький!!!

class UserRequest(BaseModel):
    name: str
    age: int
    telegram_id: int


@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/sign_up", response_class=HTMLResponse)
async def sign_up(request: Request):
    return templates.TemplateResponse("form.html", {
        "request": request
    })


@app.post("/sign_up", response_class=HTMLResponse)
async def register_user(request: Request, name: str = Form(), email: str = Form()):
    request.session["name"] = name
    request.session["email"] = email
    return RedirectResponse(url="/sign_up/tg", status_code=303)

@app.get("/sign_up/tg", response_class=HTMLResponse)
async def telegram_widget(request: Request):
    name = request.session.get("name")
    email = request.session.get("email")
    if not name or not email:
        return RedirectResponse(url="/sign_up")

    return templates.TemplateResponse("telegram_widget.html", {
        "request": request
    })

@app.get("/sign_up/telegram", response_class=HTMLResponse)
async def telegram_auth(request: Request, id: int = Query(...)):
    telegram_id = id
    request.session["telegram_id"] = telegram_id
    name = request.session.get("name")
    email = request.session.get("email")
    if already_registered(name, email, telegram_id): # optional as it duplicates unique=True in telegram_id Column
        return HTMLResponse(status_code=404, content="Bad Request")
    user = User(name=name, email=email, telegram_id=telegram_id)
    session.add(user)
    session.commit()
    logging.info(f"User {name} with email {email} and Telegram ID {telegram_id} has signed up")
    registration.send_welcome_message(user.telegram_id, user.name)
    return RedirectResponse(url="/search")
@app.get("/search", response_class=HTMLResponse)
async def search_form(request: Request):
    return templates.TemplateResponse("search_form.html", {
        "request": request
    })

@app.post("/search", response_class=HTMLResponse)
async def user_request(request: Request, fr: str = Form(), to: str = Form(), date: str = Form()):
    user = session.query(User).filter_by(name=request.session.get("name"), email=request.session.get("email")).first()
    new_request = TRequest(user_id = user.id, from_city=fr, to_city=to, date=date)
    session.add(new_request)
    session.commit()
    logging.info(f"User {request.session.get('name')} made a new request: {fr} : {to} : {date}")
    last_request = session.query(TRequest).filter_by(user_id=user.id).order_by(TRequest.request_id.desc()).first()
    registration.send_request(user.telegram_id, last_request.from_city, last_request.to_city, last_request.date)
    return RedirectResponse(url="/search/results")

@app.post("/search/results", response_class=HTMLResponse)
async def search_results(request: Request):
    flight_data = get_flight_data()
    flight_rectangles = create_rectangles(flight_data)
    return templates.TemplateResponse("search_results.html", {
        "request": request,
        "flight_rectangles": flight_rectangles
    })

