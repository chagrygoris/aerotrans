from y_rasp import fetch_data
import os


async def get_car_data():
    url = f'https://api.с.org/v2/directions/driving-car?api_key={os.getenv("OPENROUTE_API_KEY")}&start=8.681495,49.41461&end=8.687872,49.420318'
    data = dict(await fetch_data(url))
    print(data['features'][0]['properties'])