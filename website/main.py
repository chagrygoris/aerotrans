import logging
from fastapi import FastAPI, Form, Request, Query, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session, sessionmaker

from databaza import session, User, already_registered, TRequest, TFlight, TCart

from searching_tool.get_info import get_flight_data
from searching_tool.view_results import create_rectangles

logging.basicConfig(filename='logs', filemode='w')
logging.getLogger().setLevel(logging.INFO)
from telegram_bot import registration



app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key="your-secret-key") # pycharm глупенький!!!
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


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
    request.session["from_city"] = fr
    request.session["to_city"] = to
    user = session.query(User).filter_by(name=request.session.get("name"), email=request.session.get("email")).first()
    new_request = TRequest(user_id = user.id, from_city=fr, to_city=to, date=date)
    session.add(new_request)
    session.commit()
    logging.info(f"User {request.session.get('name')} made a new request: {fr} : {to} : {date}")
    last_request = session.query(TRequest).filter_by(user_id=user.id).order_by(TRequest.request_id.desc()).first()
    registration.send_request(user.telegram_id, last_request.from_city, last_request.to_city, last_request.date)
    if not session.query(TFlight).filter_by(origin=fr, destination=to).first():
        get_flight_data()
    flight_rectangles = create_rectangles(request.session.get("from_city"), request.session.get("to_city"), session)
    request.session["flight_rectangles"] = flight_rectangles
    return RedirectResponse(url="/search/results")

@app.post("/search/results", response_class=HTMLResponse)
async def search_results(request: Request):
    flight_rectangles = request.session.get("flight_rectangles")
    return templates.TemplateResponse("search_results.html", {
        "request": request,
        "flight_rectangles": flight_rectangles
    })


@app.post("/add_to_cart", response_class=HTMLResponse)
async def add_to_cart(request: Request, flight_id: int = Form(...)):
    user = session.query(User).filter_by(name=request.session.get("name"), email=request.session.get("email")).first()
    selected_flight = session.query(TFlight).filter(TFlight.flight_id == flight_id).first()
    entry = session.query(TCart).filter(TCart.user_id == user.id, TCart.flight_id == flight_id).first()
    if not entry:
        new_item = TCart(user_id=user.id, flight_id=selected_flight.flight_id)
        session.add(new_item)
        session.commit()
        request.session["cart_length"] = session.query(TCart).count()
    return RedirectResponse(url="/search/results")
@app.get("/search/cart", response_class=HTMLResponse)
async def cart(request: Request):
    user = session.query(User).filter_by(name=request.session.get("name"), email=request.session.get("email")).first()
    cart_items = session.query(TCart).filter_by(user_id=user.id).all()
    flights = []
    for cart_item in cart_items:
        flight = session.query(TFlight).filter_by(flight_id=cart_item.flight_id).first()
        if flight:
            flights.append(flight)
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "cart": flights
    })