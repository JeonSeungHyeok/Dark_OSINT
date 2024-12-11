from default.basic_tor import *
from blackbasta.blackbasta import *
import json
import os

def make_output_file(name,result):
    current_path = os.getcwd()
    try:
         os.mkdir("OUT")
    except FileExistsError as e:
         pass
    with open(f"{current_path}/OUT/{name}_result.json", "w") as json_file:
            json.dump(result, json_file, indent=4)

def process():
    urls = {
        "blackbasta":"http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion/"
    }
    classes = {
        "blackbasta":osint_blackbasta,
    }

    for key,value in classes.items():
        make_output_file(key,value(urls[key]).process())