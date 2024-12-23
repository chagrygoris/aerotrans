# to do
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from adapters import get_flight_data
import aiohttp
from src import TFlight  # Предполагается, что TFlight определён в models

async def fetch_data(url:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

@pytest.mark.asyncio
@patch("src.get_or_create_city")
@patch("adapters.fetch_data")
@patch("src.session")
async def test_get_flight_data(mock_session, mock_fetch_data, mock_get_or_create_city):
    # Настройка моков
    mock_get_or_create_city.side_effect = lambda name: AsyncMock(yandex_code=f"code_{name}")

    mock_fetch_data.return_value = {
        'segments': [
            {
                'from': {'title': 'CityA'},
                'to': {'title': 'CityB'},
                'departure': '2024-12-23T10:00:00',
                'arrival': '2024-12-23T12:00:00',
                'tickets_info': {'places': [{'price': {'whole': 100}}]},
                'thread': {
                    'carrier': {'title': 'AirlineX'},
                    'transport_type': 'plane'
                }
            },
            {
                'from': {'title': 'CityA'},
                'to': {'title': 'CityB'},
                'departure': '2024-12-23T15:00:00',
                'arrival': '2024-12-23T17:00:00',
                'tickets_info': {'places': []},  # Нет данных о цене
                'thread': {}  # Нет данных о перевозчике
            }
        ]
    }

    mock_session.add_all = MagicMock()
    mock_session.commit = MagicMock()

    # Вызов тестируемой функции
    departure = "CityA"
    destination = "CityB"
    date = "2024-12-23"
    res_origin, res_arrival = await get_flight_data(departure, destination, date)

    # Проверка результата
    assert res_origin == "CityA"
    assert res_arrival == "CityB"

    mock_get_or_create_city.assert_any_call("CityA")
    mock_get_or_create_city.assert_any_call("CityB")
    mock_fetch_data.assert_called_once()



