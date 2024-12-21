import datetime

from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandObject
from aiogram import Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import os, logging, asyncio, sys, dotenv
from src.constants import help_message
from config import Config
dotenv.load_dotenv()

text_router = Router()

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("help"))
async def helper(message: Message):
    await message.answer(help_message)


route_router = Router()
dp.include_router(route_router)

@route_router.message(Command("route"))
async def routefinder(message: Message, command: CommandObject):
    from adapters import compile_message
    commands = command.args.split()
    departure, destination, date = '', '', ''
    if len(commands) == 3:
        departure, destination, date = commands
    elif len(commands) == 2:
        departure, destination = commands
        date = datetime.datetime.today()
    await message.answer(f"Finding routes {departure} ---> {destination}")
    await message.answer(str(await compile_message(departure, destination, date)))





async def bot_main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=Config.TELEGRAM_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(bot_main())