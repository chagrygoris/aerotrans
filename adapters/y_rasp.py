import asyncio
import json
import os
import aiohttp
import certifi
from yarl import URL
import yaml
from dotenv import load_dotenv
from datetime import datetime, timedelta
from src import TFlight, session
from src import have_saved_routes
from aiogram import html
from config import Config

load_dotenv()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()
apikey = '28e3cb6e-cc7b-4d8a-b64c-8a52a70365fc'
#apikey = Config.YANDEX_RASP_KEY

async def get_flight_data(departure: str, destination: str, date: str):
    from src import get_or_create_city
    departure_city = await get_or_create_city(departure)
    destination_city = await get_or_create_city(destination)
    url = str(URL(f'''
        https://api.rasp.yandex.net/v3.0/search/?apikey={apikey}&from={departure_city.yandex_code}&to={destination_city.yandex_code}&format=json&lang=ru_RU&date={date}
    '''))
    data = await fetch_data(url)
    flights = []
    res_origin, res_arrival = '', ''
    for segment in data['segments']:
        origin = segment['from']['title']
        destination = segment['to']['title']
        if not res_origin or not res_arrival:
            res_origin, res_arrival = origin, destination
        departure_time = datetime.fromisoformat(segment['departure'])
        arrival_time = datetime.fromisoformat(segment['arrival'])
        try:
            price = segment['tickets_info']['places'][0]['price']['whole']
        except:
            price = None
        try:
            company = segment['thread']['carrier']['title']
        except:
            company = None
        try:
            transport_type = segment['thread']['transport_type']
        except:
            transport_type = None
        # print(origin, destination, "nothing found")
        flights.append(TFlight(
            origin_city_code=departure_city.yandex_code,
            destination_city_code=destination_city.yandex_code,
            origin_city_name=origin,
            destination_city_name=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            price=price,
            company=company,
            transport_type=transport_type
        ))
    session.add_all(flights)
    session.commit()
    return res_origin, res_arrival


async def get_suggestion(city:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://suggests.rasp.yandex.net/all_suggests?format=old&part=<{city}>') as resp:
            res = await resp.json()
    return res

async def fetch_data(url:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async def suggest(city:str):
    res = await get_suggestion(city)
    # print(res[1][0])
    return res[1][0]


def get_icon(transport:str) -> str:
    if transport == 'plane':
        return '✈️'
    if transport == 'train':
        return '🚆'
    if transport == 'suburban':
        return '🚇'
    if transport == 'bus':
        return '🚌'
    if transport == 'helicopter':
        return '🚁'
    if transport == 'water':
        return '🛳️'


async def compile_message(origin: str, destination: str, date: str) -> str:
    from src import get_city
    from adapters import format_datetime
    results = have_saved_routes(origin, destination, date)
    if not results:
        await get_flight_data(origin, destination, date)
        dep_code = await get_city(origin)
        dest_code = await get_city(destination)
        results = session.query(TFlight).filter_by(origin_city_code=dep_code, destination_city_code=dest_code).all()
    message = ''''''
    for i in range(min(5, len(results))):
        res = results[i]
        message += (html.bold(f"{i+1})") + get_icon(res.transport_type) + f''' {res.origin_city_name} -> {res.destination_city_name} \nОтправление {format_datetime(str(res.departure_time))}\nПрибытие {format_datetime(str(res.arrival_time))}\n''')
        if res.price:
            message += f'Цена: от {res.price} рублей\n\n'
    return message


if __name__ == '__main__':
    # asyncio.run(get_flight_data2('Москва', 'Санкт-Петербург', '2024-11-30'))
    # asyncio.run(get_segments(json.load(open('mow-spb.json', 'r'))))
    asyncio.run(get_flight_data('Москва', 'Сочи', '2024-12-25'))

