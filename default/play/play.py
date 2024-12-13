from default.basic_tor import osint_tor_render_js
from bs4 import BeautifulSoup
import time
import re
from requests import *

class osint_play(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)
        self.base_url = url.rstrip("/")  # URL 마지막 슬래시 제거
        self.progress = True
        self.result = {}

    def tor_playwright_crawl(self):
        try:
            self.page.goto(self.url, timeout=60000) 
            self.page.wait_for_timeout(5000)
            html = self.page.content()
            response = Response()
            response._content = html.encode('utf-8') 
            response.status_code = 200 
            response.url = self.url 
            response.headers = {"Content-Type": "text/html; charset=utf-8"} 
            self.response = response
        except Exception as e:
            print(f"Error: {e}")

    def using_bs4(self):
        print(self.response)
        print()
        print()
        html = self.response.text
        bsobj = BeautifulSoup(html, 'html.parser')
        object_table = bsobj.find_all("th", class_='News')

        for tr in object_table:
            # 제목
            title = tr.contents[0].strip() if tr.contents[0] else 'none'

            # 위치
            location_element = tr.find('i', class_='location')
            location = location_element.next_sibling.strip() if location_element else 'none'

            # 사이트
            site_element = tr.find('i', class_='link')
            site = site_element.next_sibling.strip() if site_element else 'none'

            # topic ip
            onclick_value = tr['onclick'] if 'onclick' in tr.attrs else 'none'  # onclick 속성이 있는 <th> 태그 찾기
  
            if onclick_value:
                # "viewtopic('<post_id>')"에서 <post_id> 추출
                post_id = onclick_value.split("'")[1]  # 작은 따옴표로 분리하여 post_id 추출
                href = f'/topic.php?id={post_id}'  # 완전한 URL 생성
                full_url = self.base_url + href
                self.url=full_url
                comment, description = self.details()

            
            result = {
                        "title": title,
                        "address": location,
                        "site": site,
                        "Description": description,
                        "all data": comment
            }
            self.result[title]=result

    def details(self):
        self.tor_playwright_crawl()
        new_html = self.response.text
        new_soup = BeautifulSoup(new_html, 'html.parser')
        print(self.url)
        print(new_html)
        input()
        description = None
        for elem in new_soup.find_all(string=re.compile(r'information\s*:?', re.IGNORECASE)):
            if 'information' in elem.lower():
                description = elem.split('information:')[-1].strip()
                break

        # comment 추출 (comment: 뒤의 내용)
        comment = None
        for elem in new_soup.find_all(string=re.compile(r'comment\s*:?', re.IGNORECASE)):
            if 'comment' in elem.lower():
                comment = elem.split('comment:')[-1].strip()
                break

        # 링크
        #title_link = new_soup.find('a')['href'] if new_soup.find('a') else 'none'
        print(comment,description)
        return comment, description

    def next_page(self):
        for page in range(1):  # 페이지 1~2까지만 크롤링
            self.url = self.base_url + f'/index.php?page={page}'  # URL 업데이트
            print(self.url)  # 업데이트된 URL 출력
            time.sleep(1)  # 1초 대기
            super().tor_playwright_crawl()  # Tor 브라우저로 크롤링
            self.using_bs4()  # BeautifulSoup으로 데이터 처리

    def remove_char(self, key):
        for char in ['#', ':', '.']:
            key = key.replace(char, '').lower()
        return key.lower()

    def process(self):
        super().init_browser()
        try:
            self.next_page()
        finally:
            self.progress = False  # 종료 조건 설정
            super().close_browser()
        return self.result