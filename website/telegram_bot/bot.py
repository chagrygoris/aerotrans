from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandObject
from aiogram import Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import os, logging, asyncio, sys, dotenv
from website.searching_tool.get_info import compile_message
from openai import OpenAI
dotenv.load_dotenv()

text_router = Router()

dp = Dispatcher()

def p():
    client = OpenAI()

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                'role': 'user', 'content': 'what model am i using?'
            }
        ]
    )
    print(completion)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("help"))
async def helper(message: Message):
    with open('help_message', 'r') as f:
        await message.answer(f.read())


route_router = Router()
dp.include_router(route_router)

@route_router.message(Command("route"))
async def routefinder(message: Message, command: CommandObject):
    commands = command.args
    departure, destination = commands.split()
    await message.answer(f"Finding routes {departure} ---> {destination}")
    await message.answer(str(await compile_message(departure, destination, '2024-11-30')))


async def bot_main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=os.getenv('TELEGRAM_API_KEY'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    p()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(bot_main())