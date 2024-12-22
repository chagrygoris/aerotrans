from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime, select
from sqlalchemy.types import LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, '../src/users.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL)

Base = declarative_base()




class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(LargeBinary)
    telegram_id = Column(Integer)
    def __repr__(self):
        return f"<User(name='{self.name}'>"


class TRequest(Base):
    __tablename__ = "t_request"
    request_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    from_city = Column(String)
    to_city = Column(String)
    date = Column(String)

class City(Base):
    __tablename__ = "t_cities"
    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, nullable=False)
    yandex_code = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<City(name='{self.city_name}', yandex_code='{self.yandex_code}')>"


class TFlight(Base):
    __tablename__ = "t_flights"
    flight_id = Column(Integer, primary_key=True, index=True)
    origin_city_code = Column(String, ForeignKey("t_cities.yandex_code"))
    destination_city_code = Column(String, ForeignKey("t_cities.yandex_code"))
    origin_city_name = Column(String)
    destination_city_name = Column(String)
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    transport_type = Column(String)
    price = Column(Float)
    company = Column(String)

    def __repr__(self):
        return f"<TFlight(flight_id='{self.flight_id}', origin='{self.origin_city_name}', destination='{self.destination_city_name}')>"


class TCart(Base):
    __tablename__ = "t_cart"
    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    flight_id = Column(Integer, ForeignKey("t_flights.flight_id"))

# Base.metadata.drop_all(bind= engine)
Base.metadata.create_all(bind= engine)

Session = sessionmaker(bind=engine)
session = Session()




