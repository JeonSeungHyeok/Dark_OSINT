from default.basic_tor import osint_tor_render_js
from bs4 import BeautifulSoup
import time
import re
import requests

class osint_play(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)
        self.base_url = url.rstrip("/")  # URL 마지막 슬래시 제거
        self.progress = True
        self.scraper = requests.Session()
        self.result = {}

    def using_bs4(self):
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
                full_url = self.base_url + href # 링크 추출
                print('onclick_value:', onclick_value)
                print()
                print('full_url:', full_url)  # 생성된 URL 출력

            description, comment = self.details(full_url)
            
            result = {
                        "title": title,
                        "address": location,
                        "site": site,
                        "Description": description,
                        "all data": comment,
                        "link": full_url
            }
            print()
            print(result)
            self.result[title]=result

    def details(self, full_url):
        self.tor_playwright_crawl()
        new_html = self.response.text
        new_soup = BeautifulSoup(new_html, 'html.parser')

        comment, description = None, None
        # update_element = new_soup.find_all('th', class_='News')

        # 정보(information) 추출
        information_element = new_soup.find('div', string=lambda t: t and 'information:' in t.lower())
        if information_element:
            description = information_element.text.strip().replace('information:', '').strip()

        # 댓글(comment) 추출
        comment_element = new_soup.find('div', string=lambda t: t and 'comment:' in t.lower())
        if comment_element:
            comment = comment_element.text.strip().replace('comment:', '').strip()

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

