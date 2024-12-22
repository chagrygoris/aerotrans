from aiogram import Router, html
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultDocument
from src.models import session, TCart, TFlight, User
from src.constants import ending, empty_cart_message
from adapters import get_icon, format_datetime, compile_message, advertise
from datetime import datetime


def is_date(dt:str):
    try:
        datetime.strptime(dt, '%Y-%m-%d')
        return True

    except:
        return False

inline_router = Router()



def describe_cart(user_id: int):
    try:
        user_id = session.query(User.id).filter(User.telegram_id == user_id).first()[0]
        cart_items = session.query(TCart, TFlight).join(TFlight, TCart.flight_id == TFlight.flight_id).filter(
            TCart.user_id == user_id).all()
        if not cart_items:
            return empty_cart_message
        message = ''''''
        for i in range(len(cart_items)):
            item = cart_items[i][1]
            print(item.transport_type)
            message += html.bold(f"{i + 1}) ") + get_icon(
                item.transport_type) + f''' {item.origin_city_name} -> {item.destination_city_name} \nОтправление {format_datetime(str(item.departure_time))}\nПрибытие {format_datetime(str(item.arrival_time))}\n'''
            i += 1
        return message
    except:
        return "Ваша корзина пуста"


@inline_router.inline_query()
async def inline_find_routes(inline_query: InlineQuery):
    if inline_query.query:
        try:
            origin, destination, date = inline_query.query.split()
            assert is_date(date)
        except:
            article = InlineQueryResultArticle(
                id='1',
                title='Введите ваше сообщение в формате',
                input_message_content=InputTextMessageContent(
                    message_text='Пожалуйста, введите корректный запрос'
                ),
                description='откуда куда YYYY-MM-DD'
            )
            await inline_query.answer([article])
            return
        article = InlineQueryResultArticle(
            id='1',
            title='Найти рейсы',
            input_message_content=InputTextMessageContent(
                message_text=await compile_message(origin, destination, date)
            ),
            description='нажмите, чтобы начать поиск'
        )
        await inline_query.answer([article])
        return
    print(inline_query.from_user.id)
    results = []
    results.append(InlineQueryResultArticle(
        id='1',
        title='cart',
        description='Корзина',
        input_message_content=InputTextMessageContent(message_text=describe_cart(inline_query.from_user.id)),
        thumbnail_url='https://img.lovepik.com/photo/20211125/small/lovepik-daughters-parents-shopping-cart-shopping-picture_501056049.jpg'
    ))

    results.append(InlineQueryResultArticle(
        id='2',
        title="I'm feeling lucky...",
        thumbnail_url='https://avatars.dzeninfra.ru/get-zen_doc/271828/pub_656aad81c205fb172b747405_656aad86d352075c620f80c4/scale_1200',
        input_message_content=InputTextMessageContent(
            message_text=advertise() + ending
        ),
        description='улететь за тридевять земель'
    ))

    results.append(InlineQueryResultArticle(
        id='3',
        title='Введите ваше сообщение в формате',
        input_message_content=InputTextMessageContent(
            message_text='Пожалуйста, введите корректный запрос'
        ),
        description='откуда куда YYYY-MM-DD'
    ))

    await inline_query.answer(results, cache_time=0)


if __name__ == '__main__':
    # print(is_date('2024-11-21'))
    from faker import Faker
    f = Faker('ru_RU')
    print(' '.join(f.city().split()[1:]))