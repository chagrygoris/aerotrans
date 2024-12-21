from src.models import session, City, select
from adapters import suggest


async def get_or_create_city(city_name: str):
    city_data = await suggest(city_name)
    yandex_code = city_data[0]
    city_name_from_api = city_data[1]
    city = session.execute(select(City).filter_by(yandex_code=yandex_code))
    city = city.scalar_one_or_none()
    if not city:
        city = City(city_name=city_name_from_api, yandex_code=yandex_code)
        session.add(city)
        session.commit()
    return city

async def get_yandex_code(city_name: str):
    city_id = await suggest(city_name)
    print(city_id[0], "city_id")
    return city_id[0]

async def get_city(city_name: str):
    yandex_code = await get_yandex_code(city_name)
    return yandex_code