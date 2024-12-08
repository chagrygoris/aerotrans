from .models import User, session, TFlight, TCart
from sqlalchemy import select
from sqlalchemy import DateTime

def already_registered(name: str, email: str, telegram_id: int) -> bool:
    stmt = select(User).where(
        (User.name == name) &  # type: ignore
        (User.email == email) &
        (User.telegram_id == telegram_id)
    )
    return session.execute(stmt).first() is not None


def have_saved_routes(origin: str, destination: str, date: str) -> bool | TFlight:
    res = session.query(TFlight).filter(
        TFlight.origin.like(f"%{origin}%"),
        TFlight.destination == destination).first()
    if not res:
        return False
    return res



def cart_item_exists(user_id: int, flight_id: int) -> bool:
    stmt = select(TCart).where(
        (TCart.user_id == user_id) &  # type: ignore
        (TCart.flight_id == flight_id)
    )
    return session.execute(stmt).first() is not None


def add_user(name: str, email: str, password: bytes, telegram_id: int):
    if already_registered(name, email, telegram_id):
        return None
    new_user = User(name=name, email=email, password=password, telegram_id=telegram_id)
    session.add(new_user)
    session.commit()
    return new_user


def add_flight(origin: str, destination: str, departure_time: str, arrival_time: DateTime, price: float,
               company: str):
    if have_saved_routes(origin, destination, departure_time):
        return None

    new_flight = TFlight(
        origin=origin,
        destination=destination,
        departure_time=departure_time, #type:ignore
        arrival_time=arrival_time, #type:ignore
        price=price,
        company=company
    )
    session.add(new_flight)
    session.commit()
    return new_flight


def add_to_cart(user_id: int, flight_id: int):
    if cart_item_exists(user_id, flight_id):
        return None
    new_cart_item = TCart(user_id=user_id, flight_id=flight_id)
    session.add(new_cart_item)
    session.commit()
    return new_cart_item
