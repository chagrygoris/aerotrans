from g4f import Client
from faker import Faker
import concurrent.futures

randomizer = Faker('ru_RU')

client = Client()
def contains_only_letters_and_spaces(s:str) -> bool:
    return all(c.isalpha() or c.isspace() for c in s)


def random_city() -> str:
    city = ' '.join(randomizer.city().split()[1:])
    while not contains_only_letters_and_spaces(city):
        city = ' '.join(randomizer.city().split()[1:])
    return city



def try_to_advertise():
    city = random_city()
    message = f'Напиши красивый рассказ про город {city} в двух предложениях. Укажи, в каком субъекте он находится'
    # message = ''
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message}],
        # Add any other necessary parameters
        language='Russian'
    )
    return response.choices[0].message.content



def advertise() -> str:
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(try_to_advertise)
            message = future.result(timeout=17)
    except concurrent.futures.TimeoutError:
        message = "Анлаки. Пока никуда не летим"
    return message





if __name__ == '__main__':
    print(advertise())