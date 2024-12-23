from .viewResults import create_rectangles, format_datetime
from .yrasp import get_flight_data, suggest, compile_message, get_icon
from .assistant import advertise
import aiohttp

async def fetch_data(url:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
