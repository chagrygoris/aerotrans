from src.models import TFlight
from sqlalchemy.orm import Session
from typing import List
from adapters.y_rasp import suggest

async def create_rectangles(from_city: str, to_city: str, db: Session) -> List[dict]:
    flight_rectangles = []
    departure_id = await suggest(from_city)
    destination_id = await suggest(to_city)
    departure_id, destination_id = departure_id[0], destination_id[0]
    flights_query = db.query(TFlight).filter(
        TFlight.origin_city_code == departure_id,
        TFlight.destination_city_code == destination_id, #type: ignore
    ).all()
    for flight in flights_query:
        departure_time_str = flight.departure_time.isoformat() if flight.departure_time else None
        flight_rectangles.append({
            "id": flight.flight_id,
            "origin": flight.origin_city_name,
            "destination": flight.destination_city_name,
            "departure_time": departure_time_str,
            "price": flight.price
        })
    print(flight_rectangles, "test")
    return flight_rectangles