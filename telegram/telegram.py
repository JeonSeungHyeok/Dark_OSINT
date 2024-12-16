import time
import requests
import json
import os

BOT_TOKEN = '7612275874:AAHkZ3F1-xNyDdV8jJYhS9MXbN3xqSnI3l8'
CHAT_ID = '-1002438870737'
url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def send_message(message):
    response = requests.post(url, data={'chat_id': CHAT_ID, 'text': message})
    print("Message sent!" if response.status_code == 200 else f"Failed: {response.status_code}")

def send_json_content_to_telegram(json_file_path):
    with open(json_file_path) as json_file:
        data = json.load(json_file)

    message = "\n".join(
        [f"**{title}**\n"
         f"description: {details.get('description', 'N/A')}\n"
         f"price: {details.get('price', 'N/A')}\n"
         f"timer: {details.get('timer', 'N/A')}\n"
         f"update_date: {details.get('update_date', 'N/A')}\n"
         f"views: {details.get('views', 'N/A')}\n{'-'*40}"
         for title, details in data.items()]
    )

    if message:
        # 메시지가 너무 길면 분할해서 보내기
        [send_message(chunk) for chunk in [message[i:i+4096] for i in range(0, len(message), 4096)]] if len(message) > 4096 else send_message(message)

def monitor_and_notify():
    json_file_path = '/tmp/darkweb/OUT/medusa_result.json'
    
    # 10초마다 파일이 생성되었는지 확인
    while not os.path.exists(json_file_path):
        time.sleep(10)  # 10초마다 확인

    # 파일이 생성되면 텔레그램으로 전송
    send_json_content_to_telegram(json_file_path)