from default.basic_tor import *
from blackbasta.blackbasta import *
from bianlian.bialian import *
from play.play import *
from raworld.ra_world import *
from collections import OrderedDict
import json
import os

def reorder_dict(data):
    desired_order = ["title", "Description", "site", "address", "country", "region", "all data", "tel", "link", "images", "times"]
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
        #"blackbasta":"http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion/",
        #"bianlian": "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/"
        #"play": "http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/",
        "raworld" : "http://raworldw32b2qxevn3gp63pvibgixr4v75z62etlptg3u3pmajwra4ad.onion/"
    }
    classes = {
        #"blackbasta":osint_blackbasta,
        #"bianlian":osint_bianlian,
        #"play":osint_play,
        "raworld": osint_rawolrd
    }

    for key,value in classes.items():
        osint_class = value(urls[key])
        make_output_file(key,osint_class.process())