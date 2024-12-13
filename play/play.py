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
                comment, description, title_link = self.details(full_url)

                result = {
                    "title": title,
                    "address": location,
                    "site": site,
                    "link": title_link,
                    "Description": description,
                    "all data": comment,
                }
                self.result[title] = result

    def details(self, url):
        self.make_tor_session()
        response = self.session.get(url, verify=False)
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
        title_link = new_soup.find('a')['href'] if new_soup.find('a') else 'none'

        return comment, description, title_link

    def next_page(self):
        while self.progress:
            time.sleep(1)
            super().tor_playwright_crawl()
            self.using_bs4()
            if hasattr(self, 'page'):
                try:
                    # 페이지 번호를 기준으로 정확한 다음 버튼을 선택
                    next_buttons = self.page.locator("span.Page[onclick*='goto_page(']")
                    visible_buttons = [btn for btn in next_buttons if btn.is_visible()]

                    if visible_buttons:
                        # 마지막 버튼을 클릭 (다음 페이지 버튼)
                        visible_buttons[-1].click()
                        self.page.wait_for_timeout(2000)
                    else:
                        break
                except Exception as e:
                    print(f"Error while navigating pages: {e}")
                    break
            else:
                print("Error: 'self.page' is not initialized.")
                break

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
