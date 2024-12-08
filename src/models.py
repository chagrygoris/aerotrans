from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime, select
from sqlalchemy.types import LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///../users.db"
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

class TFlight(Base):
    __tablename__ = "t_flights"
    flight_id = Column(Integer, primary_key=True, index=True)
    origin = Column(String)
    destination = Column(String)
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    price = Column(Float)
    company = Column(String)
    class Config:
        orm_mode = True

class TCart(Base):
    __tablename__ = "t_cart"
    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    flight_id = Column(Integer, ForeignKey("t_flights.flight_id"))

Base.metadata.drop_all(bind= engine)
Base.metadata.create_all(bind= engine)

Session = sessionmaker(bind=engine)
session = Session()




