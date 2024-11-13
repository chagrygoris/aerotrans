from sqlalchemy import create_engine, Column, Integer, String, select
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
    telegram_id = Column(Integer, unique=True)
    def __repr__(self):
        return f"<User(name='{self.name}'>"

Base.metadata.drop_all(engine) # just for now to avoid problems with unique id's after reloads. than instead of the UniqueException redirection to the /login endpoint may be implemented
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
