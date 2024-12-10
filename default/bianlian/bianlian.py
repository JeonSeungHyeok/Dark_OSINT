import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from default.basic_tor import osint_tor_render_js
from bs4 import BeautifulSoup
import json
import time

class osint_blackbasta(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)
        self.result = {}

    def using_bs4(self):
        html = self.response.text
        bsobj = BeautifulSoup(html, 'html.parser')

        # 모든 section.list-item 태그 찾기
        list_items = bsobj.find_all("section", class_="list-item")
        for item in list_items:
            # 데이터 추출
            title_tag = item.find("h1", class_="title")
            title = title_tag.text.strip() if title_tag else "No Title"

            url_tag = title_tag.find("a", href=True) if title_tag else None
            url = f"http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion{url_tag['href']}" if url_tag else "No URL"

            description_tag = item.find("div", class_="description")
            description = description_tag.text.strip() if description_tag else "No Description"

            # 결과 딕셔너리에 추가
            result = {
                "title": title,
                "url": url,
                "description": description
            }
            self.result[title] = result

    def next_page(self):
        while True:
            time.sleep(1)
            super().tor_playwright_crawl()
            self.using_bs4()
            try:
                next_button = self.page.locator("ul.pagination .page-next a")
                if not next_button or not next_button.is_visible() or next_button.is_disabled():
                    break
                next_button.click()
                self.page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Error while navigating pages: {e}")
                break
        # 결과를 JSON 파일로 저장
        with open("result.json", "w") as json_file:
            json.dump(self.result, json_file, indent=4)

    def remove_char(self,key):
        if '#' in key:
            key=key.replace('#','').lower()
        if ':' in key:
            key=key.replace(':','').lower()
        if '.' in key:
            key=key.replace('.','').lower()
        if key:
            return key.lower()
        else:
            return key

    def process(self):
        super().init_browser()
        self.next_page()
        super().close_browser()

def main():
    url = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/"
    blackbasta = osint_blackbasta(url)
    blackbasta.process()

if __name__ == "__main__":
    main()
