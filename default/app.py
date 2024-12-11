from default.basic_tor import *
from blackbasta.bianlian import *
from collections import OrderedDict
import json
import os

def reorder_dict(data):
    desired_order = ["title", "Description", "site", "address", "all data", "tel", "link", "images"]
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
    except FileExistsError as e:
         pass
    with open(f"{current_path}/OUT/{name}_result.json", "w") as json_file:
            json.dump(reorder_dict(result), json_file, indent=4)

def process():
    urls = {
        "bianlian":"http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/"
    }
    classes = {
        "bianlian":osint_bianlian,
    }

    for key,value in classes.items():
        make_output_file(key,value(urls[key]).process())