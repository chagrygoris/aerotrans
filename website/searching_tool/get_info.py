import asyncio
import json
import os
import aiohttp
import certifi
from yarl import URL
import yaml
from dotenv import load_dotenv
from datetime import datetime, timedelta
from databaza import TFlight, session

load_dotenv()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()
# apikey = '28e3cb6e-cc7b-4d8a-b64c-8a52a70365fc'
apikey = os.getenv('YANDEX_RASP_API_KEY')
mock_res = dict()

def get_flight_data():
    flights = [
        TFlight(
            origin="Москва",
            destination="Минск",
            departure_time=datetime(2024, 12, 15, 14, 30),
            price=200.50
        ),
        TFlight(
            origin="Минск",
            destination="Санкт-Пeтербург",
            departure_time=datetime(2024, 12, 16, 9, 0),
            price=150.00
        ),
        TFlight(
            origin="Москва",
            destination="Москва",
            departure_time=datetime(2024, 12, 17, 16, 45),
            price=180.75
        ),
        TFlight(
            origin="Miami",
            destination="New York",
            departure_time=datetime(2024, 12, 18, 11, 30),
            price=220.00
        ),
        TFlight(
            origin="San Francisco",
            destination="New York",
            departure_time=datetime(2024, 12, 19, 20, 0),
            price=250.00
        )
    ]
    session.add_all(flights)
    session.commit()

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
    print(res[1][0])
    return res[1][0]
async def get_flight_data2(departure:str, destination:str, date:str):
    departure_id = await suggest(departure)
    destination_id = await suggest(destination)
    departure_id, destination_id = departure_id[0], destination_id[0]
    date = '2024-11-30'
    url = str(URL(f'''
        https://api.rasp.yandex.net/v3.0/search/?apikey={apikey}&from={departure_id}&to={destination_id}&format=json&lang=ru_RU&date={date}
    '''))
    res = await fetch_data(url)
    json.dump(res, open('mow-spb.json', 'w'))

async def get_segments(data:dict):
    for segment in data['segments']:
        # if not segment['tickets_info']['places']:
        #     continue

        print(segment['thread']['carrier']['url'])
        print(segment['tickets_info'])

async def get_car_data():
    url = f'https://api.openrouteservice.org/v2/directions/driving-car?api_key={os.getenv("OPENROUTE_API_KEY")}&start=8.681495,49.41461&end=8.687872,49.420318'
    data = dict(await fetch_data(url))
    print(data['features'][0]['properties'])



if __name__ == '__main__':
    # asyncio.run(get_flight_data2('Москва', 'Санкт-Петербург', '2024-11-30'))
    # asyncio.run(get_segments(json.load(open('mow-spb.json', 'r'))))
    asyncio.run(get_car_data())