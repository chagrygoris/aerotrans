from .databaza import User, session, TFlight
from sqlalchemy import select




def already_registered(name: str, email: str, telegram_id: int) -> bool:
    stmt = select(User).where(
        (User.name == name) &  # type: ignore
        (User.email == email) &
        (User.telegram_id == telegram_id)
    )
    return session.execute(stmt).first() is not None


def have_saved_routes(origin:str, destination:str, date:str) -> bool | TFlight:
    res = session.query(TFlight).filter_by(origin=origin, destination=destination).first()
    if not res:
        return False
    return res