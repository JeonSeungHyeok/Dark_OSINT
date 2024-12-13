from default.basic_tor import *
from blackbasta.blackbasta import *
from cactus.cactus import *
from play.play import *
from collections import OrderedDict
import json
import os

def reorder_dict(data):
    desired_order = ["title",       # 
                     "Description", #
                     "site",        #
                     "address",     #
                     "country",     #
                     "region",      #
                     "all data",    # 
                     "tel",         #
                     "link",        #
                     "images",      #
                     ]
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
        #"cactus":"https://cactusbloguuodvqjmnzlwetjlpj6aggc6iocwhuupb47laukux7ckid.onion/",
        "play": "http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/",
    }
    classes = {
        #"blackbasta":osint_blackbasta,
        #"cactus":osint_cactus,
        "play":osint_play,
    }

    for key,value in classes.items():
        print(f'Detecting : {key}')
        osint_class = value(urls[key])
        make_output_file(key,osint_class.process())