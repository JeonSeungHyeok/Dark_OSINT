from default.basic_tor import *
from blackbasta.blackbasta import *
from play.play import *
from rhysida.rhysida import *
from cactus.cactus import *
from elastic import ELK
import json
import os

def reorder_dict(data):
    desired_order = ["title", "Description", "site", "address", "country", "region", "all data", "tel", "link", "images", "times", "timer", "price"]
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
        #"play": "http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/",
        #"rhysida":"http://rhysidafohrhyy2aszi7bm32tnjat5xri65fopcxkdfxhi4tidsg7cad.onion",
        "cactus":"https://cactusbloguuodvqjmnzlwetjlpj6aggc6iocwhuupb47laukux7ckid.onion/",
    }
    classes = {
        #"blackbasta":osint_blackbasta,
        #"play":osint_play,
        #"rhysida":osint_rhysida,
        "cactus":osint_cactus,
    }
    js = ['blackbasta','play','rhysida']
    tmp = osint_tor_render_js()
    tmp.init_browser()
    for key,value in classes.items():
        osint_class = value(urls[key])
        if key in js:
            osint_class.browser = tmp.browser
            osint_class.page = tmp.page
            result, tmp.browser, tmp.page = osint_class.process()
        else:
             result = osint_class.process()
        make_output_file(key,result)
    tmp.close_browser()
    
    ELK().process()