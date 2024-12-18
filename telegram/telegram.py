import requests


BOT_TOKEN = '7612275874:AAHkZ3F1-xNyDdV8jJYhS9MXbN3xqSnI3l8'
CHAT_ID = '-1002438870737'
url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def send_message(name, message):
    payload = {
    'chat_id': CHAT_ID,
    'text': '#'+name+'\n'+message
    }
    requests.post(url, data=payload)


