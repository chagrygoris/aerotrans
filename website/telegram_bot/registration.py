import requests
TELEGRAM_API_TOKEN = "7819255078:AAEyKSPcylO0GrgTra9aHube2AT3kJtYomc"
def send_welcome_message(user_id, name):
    message = f"smile widely 🎉, {name}"
    url = f'https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage'
    payload = {
        'chat_id': user_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"Message sent to {user_id}")
    else:
        print(f"Failed to send message to {user_id}, status code {response.status_code}")
def send_request(user_id, fr: str, to: str, date: str):
    message = f"Ваш запрос: {fr} {to} {date}"
    url = f'https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage'
    payload = {
        'chat_id': user_id,
        'text': message
    }
    requests.post(url, data=payload)
