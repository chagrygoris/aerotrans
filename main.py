import logging
from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import bcrypt
import base64
import os
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import sessionmaker

from src import session, User, TRequest, TFlight, TCart
from src import already_registered, have_saved_routes

from adapters import get_flight_data
from adapters import create_rectangles

logging.basicConfig(filename='logs', filemode='w')
logging.getLogger().setLevel(logging.INFO)

from bot import send_welcome_message, send_request

from src import get_city

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")  # type: ignore
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

app.mount("/static", StaticFiles(directory="static"), name="static")


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
async def sign_up_form(request: Request, from_city: str = Query(None), to_city: str = Query(None),
                       date: str = Query(None), telegram_id: int = Query(None)):
    return templates.TemplateResponse("form.html", {
        "request": request,
        "from_city": from_city,
        "to_city": to_city,
        "date": date,
        "telegram_id": telegram_id
    })

@app.post("/sign_up", response_class=HTMLResponse)
async def register_user(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...),
                        from_city: str = Form(None), to_city: str = Form(None), date: str = Form(None),
                        telegram_id = Form(None)):
    print(telegram_id, from_city, to_city)
    if session.query(User).filter_by(email=email).first():
        return templates.TemplateResponse("form.html", {
            "request": request,
            "error": "Пользователь с таким email уже существует. Пожалуйста, войдите."
        }, status_code=400)

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(name=name, email=email, password=hashed_password)

    if telegram_id:
        user.telegram_id = telegram_id
    session.add(user)
    session.commit()
    request.session["name"] = user.name
    request.session["email"] = user.email

    if from_city != "None" and to_city != "None" and date != "None":
        request.session["telegram_id"] = user.telegram_id
        request.session["from_city"] = from_city
        request.session["to_city"] = to_city
        request.session["date"] = date
        return RedirectResponse(url="/search/results", status_code=303)

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
async def user_request(request: Request, fr: str = Form(), to: str = Form(), date: str = Form(), limit: int = Form(10) ):
    name = request.session.get("name")
    email = request.session.get("email")

    if not name or not email:
        return RedirectResponse(url="/", status_code=303)

    user = session.query(User).filter_by(name=name, email=email).first()
    if not user:
        return HTMLResponse("User not found. Please log in again.", status_code=401)

    request.session["from_city"] = fr
    request.session["to_city"] = to
    request.session["date"] = date
    request.session["limit"] = limit

    new_request = TRequest(user_id=user.id, from_city=fr, to_city=to, date=date)
    session.add(new_request)
    session.commit()
    logging.info(f"User {name} made a new request: {fr} : {to} : {date}")
    last_request = session.query(TRequest).filter_by(user_id=user.id).order_by(TRequest.request_id.desc()).first()
    send_request(user.telegram_id, last_request.from_city, last_request.to_city, last_request.date)
    return RedirectResponse(url="/search/results")


@app.api_route("/search/results", methods=["GET", "POST"], response_class=HTMLResponse)
async def search_results(request: Request):
    if request.method == "GET" and not request.session.get("telegram_id"):
        from_city = request.query_params.get("from_city")
        to_city = request.query_params.get("to_city")
        date = request.query_params.get("date")
        telegram_id = request.query_params.get("telegram_id")
        print(telegram_id, "what do we see?")
        request.session["from_city"] = from_city
        request.session["to_city"] = to_city
        request.session["date"] = date
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        request.session["name"] = user.name
        request.session["email"] = user.email
    else:
        from_city = request.session.get("from_city")
        to_city = request.session.get("to_city")
        date = request.session.get("date")

    limit = request.session.get("limit", 10)
    from_city_db = await get_city(from_city)
    to_city_db = await get_city(to_city)
    if not have_saved_routes(from_city_db, to_city_db, date):
        await get_flight_data(from_city, to_city, date)
    flight_rectangles = await create_rectangles(from_city, to_city, session, limit)
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