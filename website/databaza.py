from sqlalchemy import create_engine, Column, Integer, String, select, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
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


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def already_registered(name: str, email: str, telegram_id: int):
    stmt = select(User).where(
        (User.name == name) & #type: ignore
        (User.email == email) &
        (User.telegram_id == telegram_id)
    )
    result = session.execute(stmt).scalars().all()
    return len(result) > 0

