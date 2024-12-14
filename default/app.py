from default.basic_tor import *
from bianlian.bianlian import *
from collections import OrderedDict
import json
import os

def reorder_dict(data):
    # 기존 필드에 추가된 필드를 포함한 순서 정의
    desired_order = [
        "title", "description", "link", "site", "contact_info", "data_description", "external_links"
    ]
    reordered = []
    for item in data:
        reordered.append({k: item.get(k, "N/A") for k in desired_order})
    return reordered

def make_output_file(name, result):
    current_path = os.getcwd()
    try:
        os.mkdir("OUT")
    except FileExistsError:
        pass
    with open(f"{current_path}/OUT/{name}_result.json", "w") as json_file:
        json.dump(reorder_dict(result), json_file, indent=4)

def process():
    urls = {
        "bianlian": "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/"
    }
    classes = {
        "bianlian": osint_bianlian,
    }

    for key, value in classes.items():
        print(f"[DEBUG] Processing URL for class {key}")
        make_output_file(key, value(urls[key]).process())
