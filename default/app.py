from collections import OrderedDict
from default.basic_tor import *
from bianlian.bianlian import *
import json
import os

def reorder_dict(data):
    desired_order = ["title", "Description", "site", "address", "country", "region", "data_info", "tel", "link", "images", "times", "timer", "price"]
    reordered = {}
    for key, value in data.items():
        if isinstance(value, dict):
            reordered[key] = {k: value.get(k,"N/A") for k in desired_order}
        else:
            reordered[key] = value

    if len(reordered)==0:
        tmp = {}
        for desired_key in desired_order:
            tmp[desired_key] = "N/A"
        reordered["N/A"]=tmp
                   
    return reordered

def make_output_file(name, result):
    current_path = os.getcwd()
    try:
        os.mkdir("OUT")
    except FileExistsError:
        pass
    with open(f"{current_path}/OUT/{name}_result.json", "w") as json_file:
        json.dump(reorder_dict(result), json_file, indent=4,ensure_ascii=False)

def process():
    urls = {
        "bianlian": "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/"
    }
    classes = {
        "bianlian": osint_bianlian,
    }

    for key, value in classes.items():
        make_output_file(key, value(urls[key]).process())