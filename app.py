from default.basic_tor import *
from medusa.medusa import *
from collections import OrderedDict
from captcha import *
import json
import os

def reorder_dict(data):
    desired_order = ["title", "description", "timer", "price", "views", "update_date", "site", "address", "country", "region", "link"]
    reordered = {}
    for key, value in data.items():
        if isinstance(value, dict):
            reordered[key] = {k: value.get(k,"N/A") for k in desired_order}
        else:
            reordered[key] = value
    return reordered

def make_output_file(name,result):
    current_path = os.getcwd()
    try:
         os.mkdir("OUT")
    except FileExistsError:
         pass
    file_path = f"{current_path}/OUT/{name}_result.json"  # file_path 정의
    with open(file_path, "w") as json_file:
            json.dump(reorder_dict(result), json_file, indent=4)
    return file_path

def process():
    urls = {
        "medusa": "http://xfv4jzckytb4g3ckwemcny3ihv4i5p4lqzdpi624cxisu35my5fwi5qd.onion/",
        #"rhysida":"http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion",
    }
    classes = {
        "medusa":osint_medusa,
        #"rhysida":osint_rhysida,
    }
    result = []
    for key,value in classes.items():
        osint_class = value(urls[key])
        file_path = make_output_file(key, osint_class.process())
        result.append(file_path)
    return result