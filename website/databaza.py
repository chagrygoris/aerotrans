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
    def __repr__(self):
        return f"<User(name='{self.name}'>"

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def already_registered(name:str, email:str):
    stmt = select(User).where(User.name == name and User.email == email)
    result = session.execute(stmt)
    if len([i for i in result.scalars()]) > 0:
        return True
    return False

