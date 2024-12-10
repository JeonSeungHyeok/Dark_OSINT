import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from default.basic_tor import osint_tor_render_js
from bs4 import BeautifulSoup

class osint_blackbasta(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)

    def using_bs4(self):
        #example code
        html = self.response.text
        #print(html)
        bsobj = BeautifulSoup(html,'html.parser')
        object_table = bsobj.find_all("div",class_="card")
        for card in object_table:
            title_link = card.find("div",class_="title")
            title = title_link.find('a',class_="blog_name_link").string
            link = title_link.find('a',class_="blog_name_link").get("href")
            data_v_md_lines = card.find_all('p',attrs={"data-v-md-lines":True})
            
            for p in data_v_md_lines:
                print(f"Tag content: {p.text}, data-v-md-line: {p['data-v-md-line']}")

    def process(self):
        super().process()
        self.using_bs4()

def main():
    url = "http://stniiomyjliimcgkvdszvgen3eaaoz55hreqqx6o77yvmpwt7gklffqd.onion/"
    blackbasta = osint_blackbasta(url)
    blackbasta.process()

if __name__=="__main__":
    main()
