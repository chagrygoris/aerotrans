import logging
from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import bcrypt
import base64
import os
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import sessionmaker

from src import session, User, TRequest, TFlight, TCart
from src import already_registered, have_saved_routes

from adapters import get_flight_data, get_flight_data_test
from adapters import create_rectangles

logging.basicConfig(filename='logs', filemode='w')
logging.getLogger().setLevel(logging.INFO)

from bot import send_welcome_message, send_request



app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

app.add_middleware(SessionMiddleware, secret_key="your-secret-key") #type: ignore
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


class UserRequest(BaseModel):
    name: str
    age: int
    telegram_id: int

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user_name = request.session.get("name")
    if user_name:
        return templates.TemplateResponse("home.html", {
            "request": request,
            "user_name": user_name
        })
    else:
        return templates.TemplateResponse("home.html", {
            "request": request,
            "user_name": None
        })
    
@app.get("/sign_up", response_class=HTMLResponse)
async def sign_up(request: Request):
    if request.session.get("name") and request.session.get("email"):
        return RedirectResponse(url="/search")
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/sign_up", response_class=HTMLResponse)
async def register_user(request: Request, name: str = Form(), email: str = Form(), password: str = Form()):
    if session.query(User).filter_by(email=email).first():
        return templates.TemplateResponse("form.html", {
            "request": request,
            "error": "Пользователь с таким email уже существует. Пожалуйста, войдите."
        }, status_code=400)

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(name=name, email=email, password=hashed_password)
    session.add(user)
    session.commit()
    request.session["name"] = user.name
    request.session["email"] = user.email

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
    name = request.session.get("name")
    email = request.session.get("email")
    if not name or not email:
        return RedirectResponse(url="/sign_up")
    user = session.query(User).filter_by(name=name, email=email).first()
    if not user:
        return HTMLResponse("User not found", status_code=404)
    user.telegram_id = telegram_id
    session.commit()
    send_welcome_message(user.telegram_id, user.name)
    return RedirectResponse(url="/search")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("name") and request.session.get("email"):
        return RedirectResponse(url="/search")
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    user = session.query(User).filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный email или пароль"
        }, status_code=401)
        
    request.session["name"] = user.name
    request.session["email"] = email
    return RedirectResponse(url="/search", status_code=303)


@app.get("/search", response_class=HTMLResponse)
async def search_form(request: Request):
    if not request.session.get("name") or not request.session.get("email"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("search_form.html", {"request": request})


@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")


@app.post("/search", response_class=HTMLResponse)
async def user_request(request: Request, fr: str = Form(), to: str = Form(), date: str = Form()):
    name = request.session.get("name")
    email = request.session.get("email")

    if not name or not email:
        return RedirectResponse(url="/", status_code=303)

    user = session.query(User).filter_by(name=name, email=email).first()
    if not user:
        return HTMLResponse("User not found. Please log in again.", status_code=401)

    request.session["from_city"] = fr
    request.session["to_city"] = to

    new_request = TRequest(user_id=user.id, from_city=fr, to_city=to, date=date)
    session.add(new_request)
    session.commit()
    logging.info(f"User {name} made a new request: {fr} : {to} : {date}")
    last_request = session.query(TRequest).filter_by(user_id=user.id).order_by(TRequest.request_id.desc()).first()
    send_request(user.telegram_id, last_request.from_city, last_request.to_city, last_request.date)


    if not have_saved_routes(fr, to, date):
        get_flight_data_test()
    flight_rectangles = create_rectangles(request.session.get("from_city"), request.session.get("to_city"), session)
    request.session["flight_rectangles"] = flight_rectangles
    return RedirectResponse(url="/search/results")


@app.post("/search/results", response_class=HTMLResponse)
async def search_results(request: Request):
    flight_rectangles = request.session.get("flight_rectangles")
    print(flight_rectangles)
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