import asyncio
import json
import os
import aiohttp
import certifi
from yarl import URL
import yaml
from dotenv import load_dotenv

load_dotenv()

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()
# apikey = '28e3cb6e-cc7b-4d8a-b64c-8a52a70365fc'
apikey = os.getenv('YANDEX_RASP_API_KEY')
mock_res = dict()

def get_flight_data():
    return [
        {"from_city": "New York", "to_city": "London", "date": "2024-12-25", "price": "$500",
         "airline": "Delta Airlines", "flight_time": "7h 45m"},
        {"from_city": "Paris", "to_city": "Tokyo", "date": "2024-12-26", "price": "$800", "airline": "Air France",
         "flight_time": "11h 30m"},
        {"from_city": "Los Angeles", "to_city": "Sydney", "date": "2024-12-30", "price": "$1200",
         "airline": "Qantas Airways", "flight_time": "15h 10m"},
        {"from_city": "Berlin", "to_city": "Tokyo", "date": "2024-12-27", "price": "$600", "airline": "Lufthansa",
         "flight_time": "9h 50m"},
        {"from_city": "San Francisco", "to_city": "London", "date": "2024-12-28", "price": "$550",
         "airline": "British Airways", "flight_time": "10h 30m"},
        {"from_city": "Toronto", "to_city": "Paris", "date": "2024-12-29", "price": "$650", "airline": "Air Canada",
         "flight_time": "7h 20m"},
        {"from_city": "Madrid", "to_city": "Dubai", "date": "2024-12-31", "price": "$750", "airline": "Emirates",
         "flight_time": "6h 50m"},
        {"from_city": "Los Angeles", "to_city": "New York", "date": "2024-12-26", "price": "$300",
         "airline": "American Airlines", "flight_time": "5h 30m"},
        {"from_city": "Chicago", "to_city": "Tokyo", "date": "2024-12-25", "price": "$950",
         "airline": "United Airlines", "flight_time": "13h 45m"},
        {"from_city": "Houston", "to_city": "Sydney", "date": "2024-12-24", "price": "$1100",
         "airline": "Qantas Airways", "flight_time": "14h 10m"}
    ]

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