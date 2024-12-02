from databaza import TFlight
from sqlalchemy.orm import Session
from typing import List


def create_rectangles(from_city: str, to_city: str, db: Session) -> List[dict]:
    flight_rectangles = []
    flights_query = db.query(TFlight).filter(
        TFlight.origin == from_city,
        TFlight.destination == to_city,
    ).all()
    for flight in flights_query:
        departure_time_str = flight.departure_time.isoformat() if flight.departure_time else None
        flight_rectangles.append({
            "id": flight.flight_id,
            "origin": flight.origin,
            "destination": flight.destination,
            "departure_time": departure_time_str,
            "price": flight.price
        })
    return flight_rectangles