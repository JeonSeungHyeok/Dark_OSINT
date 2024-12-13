from default.basic_tor import *
from medusa.medusa import *
import json
import os

def process():
    url = "http://xfv4jzckytb4g3ckwemcny3ihv4i5p4lqzdpi624cxisu35my5fwi5qd.onion/"  # 여기에 실제 URL 입력
    medusa = osint_medusa(url)
    result = medusa.process()
    make_output_file("medusa", result)  # JSON 파일 저장
    print(result)

def make_output_file(name, result):
    current_path = os.getcwd()
    try:
        os.mkdir("OUT")
    except FileExistsError as e:
        pass
    with open(f"{current_path}/OUT/{name}_result.json", "w") as json_file:
        json.dump(result, json_file, indent=4)
