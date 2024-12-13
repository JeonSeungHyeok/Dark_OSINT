from default.basic_tor import osint_tor_render_js
from bs4 import BeautifulSoup
import time
import re

class osint_play(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)
        self.base_url = url.rstrip("/")  # URL 마지막 슬래시 제거
        self.progress = True
        self.result = {}

    def using_bs4(self):
        html = self.response.text
        bsobj = BeautifulSoup(html, 'html.parser')
        object_table = bsobj.find_all("tr")


        for tr in object_table:
            # 제목
            title_element = tr.find('th', class_='News')
            title = title_element.contents[0].strip() if title_element else 'none'

            # 위치
            location_element = tr.find('i', class_='location')
            location = location_element.next_sibling.strip() if location_element else 'none'

            # 사이트
            site_element = tr.find('i', class_='link')
            site = site_element.next_sibling.strip() if site_element else 'none'

            # topic.php?id=<post_id> 추출
            post_id_element = tr.find('a', href=True)
            if post_id_element:
                post_id = post_id_element['href'].split('=')[-1]
                href = f'{self.base_url}/topic.php?id={post_id}'
                full_url = href

                # comment, description 가져오기
                comment, description = self.details(full_url)

            result = {
                "title": title,
                "address": location,
                "site": site,
                #"link": title_link,
                "Description": description,
                "all data": comment,
                }
            self.result[title] = result

    def details(self):
        self.make_tor_session()
        response = self.scraper.get(self.url)
        new_html = response.text
        new_soup = BeautifulSoup(new_html, 'html.parser')

        comment, description = None, None
        update_element = new_soup.find_all('th', class_='News')

        # 설명
        description_element = new_soup.find('div', string=lambda text: text and 'information:' in text.lower())
        description = description_element.text.strip() if description_element else 'none'

        # 유출 데이터
        comment_element = new_soup.find('div', string=lambda text: text and 'comment:' in text.lower())
        comment = comment_element.text.strip() if comment_element else 'none'

        # 링크
        #title_link = new_soup.find('a')['href'] if new_soup.find('a') else 'none'

        return comment, description

    def next_page(self):
        while self.progress: 
            time.sleep(1)  
            super().tor_playwright_crawl() 
            self.using_bs4()  
            for page in range(1,4):
                self.url = self.base_url + f'/index.php?page={page}'  # URL 업데이트
                print(self.url)  # 업데이트된 URL 출력

    def remove_char(self, key):
        if '#' in key:
            key = key.replace('#', '').lower()
        if ':' in key:
            key = key.replace(':', '').lower()
        if '.' in key:
            key = key.replace('.', '').lower()
        if key:
            return key.lower()
        else:
            return key

    def process(self):
        super().init_browser()
        self.next_page()
        super().close_browser()
        return self.result
