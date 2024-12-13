import requests

BOT_TOKEN = '8079638698:AAFzIsI5C1ikXLXbSpbCZYHlYOtQId-v0Os'
CHAT_ID = '-1002178735706' # channel chat_id # '7730634302' (bot chat_id)
url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def send_message(message):
    payload = {
    'chat_id': CHAT_ID,
    'text': message
    }
    requests.post(url, data=payload)