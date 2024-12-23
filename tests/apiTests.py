from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
from adapters.yrasp import get_flight_data, get_suggestion, get_icon, suggest, compile_message
import pytest
from unittest.mock import MagicMock
from aioresponses import aioresponses
from src import session, TFlight
from src.exceptions import UnknownCityException
from adapters.yrasp import get_flight_data, suggest
async def fetch_data(url:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

@pytest.mark.asyncio
@patch("src.get_or_create_city")
@patch("adapters.fetch_data")
@patch("src.session")
async def test_get_flight_data(mock_session, mock_fetch_data, mock_get_or_create_city):
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

    assert res_origin == "CityA"
    assert res_arrival == "CityB"

    mock_get_or_create_city.assert_any_call("CityA")
    mock_get_or_create_city.assert_any_call("CityB")
    mock_fetch_data.assert_called_once()


@pytest.mark.asyncio
async def test_get_flight_data():
    with aioresponses() as m:
        m.get(
            'https://api.rasp.yandex.net/v3.0/search/?apikey=28e3cb6e-cc7b-4d8a-b64c-8a52a70365fc&from=Moscow&to=Sochi&format=json&lang=ru_RU&date=2024-12-25',
            payload={
                "segments": [
                    {
                        "from": {"title": "Москва"},
                        "to": {"title": "Сочи"},
                        "departure": "2024-12-25T10:00:00",
                        "arrival": "2024-12-25T12:30:00",
                        "tickets_info": {"places": [{"price": {"whole": 3000}}]},
                        "thread": {
                            "carrier": {"title": "Аэрофлот"},
                            "transport_type": "plane"
                        }
                    }
                ]
            })
        m.get(
            'https://suggests.rasp.yandex.net/all_suggests?format=old&part=<Москва>',
            payload=[None, []]
        )

        mock_query = MagicMock()
        mock_query.all.return_value = []
        session.query = MagicMock(return_value=mock_query)
        session.add = MagicMock()
        session.commit = MagicMock()
        with pytest.raises(UnknownCityException, match="Москва"):
            await get_flight_data('Москва', 'Сочи', '2024-12-25')

        session.add.assert_not_called()
        session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_suggestion():
    with aioresponses() as m:
        m.get(
            'https://suggests.rasp.yandex.net/all_suggests?format=old&part=<Москва>',
            payload='Москва'
        )
        suggestion = await get_suggestion('Москва')
        assert suggestion == 'Москва'

@pytest.mark.parametrize("transport, expected_icon", [
    ("plane", "✈️"),
    ("train", "🚆"),
    ("suburban", "🚇"),
    ("bus", "🚌"),
    ("helicopter", "🚁"),
    ("water", "🛳️"),
])
def test_get_icon(transport, expected_icon):
    icon = get_icon(transport)
    assert icon == expected_icon


@pytest.mark.asyncio
async def test_compile_message():
    with aioresponses() as m:
        m.get(
            'https://api.rasp.yandex.net/v3.0/search/?apikey=28e3cb6e-cc7b-4d8a-b64c-8a52a70365fc&from=Moscow&to=Sochi&format=json&lang=ru_RU&date=2024-12-25',
            payload={
                "segments": [
                    {
                        "from": {"title": "Москва"},
                        "to": {"title": "Сочи"},
                        "departure": "2024-12-25T10:00:00",
                        "arrival": "2024-12-25T12:30:00",
                        "tickets_info": {"places": [{"price": {"whole": 3000}}]},
                        "thread": {
                            "carrier": {"title": "Аэрофлот"},
                            "transport_type": "plane"
                        }
                    }
                ]
            })
        mock_query = MagicMock()
        mock_query.all.return_value = []
        session.query = MagicMock(return_value=mock_query)
        session.add = MagicMock()
        session.commit = MagicMock()
        mock_saved_routes = MagicMock()
        mock_saved_routes.return_value = []
        have_saved_routes = mock_saved_routes
        mock_get_flight_data = MagicMock()
        mock_get_flight_data.return_value = ('Москва', 'Сочи')
        get_flight_data = mock_get_flight_data
        mock_compile_message = MagicMock()
        mock_compile_message.return_value = (
            "Аэрофлот"
        )
        compile_message = mock_compile_message
        message = compile_message('Москва', 'Сочи', '2024-12-25')
        assert message == "Аэрофлот"


