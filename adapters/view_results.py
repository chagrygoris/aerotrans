from datetime import datetime
from src.models import TFlight
from sqlalchemy.orm import Session
from typing import List
from adapters.y_rasp import suggest
import locale

def format_datetime(iso_datetime: str) -> str:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    dt = datetime.fromisoformat(iso_datetime)
    return dt.strftime("%d %B %Y, %H:%M")

async def create_rectangles(from_city: str, to_city: str, db: Session, limit: int) -> List[dict]:
    flight_rectangles = []
    departure_id = await suggest(from_city)
    destination_id = await suggest(to_city)
    departure_id, destination_id = departure_id[0], destination_id[0]

    flights_query = db.query(TFlight).filter(
        TFlight.origin_city_code == departure_id,
        TFlight.destination_city_code == destination_id, #type: ignore
        TFlight.destination_city_code == destination_id,  # type: ignore
    ).limit(limit).all()

    for flight in flights_query:
        departure_time_str = flight.departure_time.isoformat() if flight.departure_time else None
        departure_time_str = format_datetime(flight.departure_time.isoformat()) if flight.departure_time else None
        arrival_time_str = format_datetime(flight.arrival_time.isoformat()) if flight.arrival_time else None

        print(flight.departure_time, flight.arrival_time)
        print(departure_time_str, arrival_time_str, "1234")

        flight_rectangles.append({
            "id": flight.flight_id,
            "origin": flight.origin_city_name,
            "destination": flight.destination_city_name,
            "departure_time": departure_time_str,
            "arrival_time": arrival_time_str,
            "price": flight.price
        })
    return flight_rectangles

