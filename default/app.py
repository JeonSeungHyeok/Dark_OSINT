from default.basic_tor import *
from blackbasta.blackbasta import *
from rhysida.rhysida import *
from collections import OrderedDict
import json
import os

def reorder_dict(data):
    desired_order = ["title", "Description", "site", "address", "country", "region", "all data", "tel", "link", "images", "timer", "price"]
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
    return json.dumps(reorder_dict(result), indent=4)

def process():
    urls = {
        #"blackbasta":"http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion/",
        "rhysida":"http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion",
    }
    classes = {
        #"blackbasta":osint_blackbasta,
        "rhysida":osint_rhysida,
    }
    result = []
    for key,value in classes.items():
        osint_class = value(urls[key])
        make_output_file(key,osint_class.process())
        result.append(make_output_file(key,value(urls[key]).process()))
    return result