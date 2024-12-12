from default.basic_tor import osint_tor_render_js
from bs4 import BeautifulSoup
import time

class osint_rhysida(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)
        self.progress=True

    def using_bs4(self):
        html = self.response.text
        bsobj = BeautifulSoup(html,'html.parser')
        object_table = bsobj.find("div",class_="carousel-inner")
        object_table = object_table.find_all("div",class_="carousel-item")
        for item in object_table:
            mass = item.find('div',class_="col-8")
            title = mass.find("a",class_="").string
            link = mass.find('a',class_="").get("href")
            description = mass.find(lambda tag: tag.name == 'div' and tag.has_attr('class') and tag['class'] == ['m-2']).string
            images = item.find_all('img', alt="image")

            result = {}
            result.update({"title":title})
            result.update({"Description":description})
            result.update({"site":link})
            for image in images:
                img = self.url + image.get('src')
                result.update({"image":img})
            self.result.update({result["title"]:result})

    def process(self):
        super().init_browser()
        super().tor_playwright_crawl()
        self.using_bs4()
        super().close_browser()
        return self.result
