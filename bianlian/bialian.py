from default.basic_tor import osint_tor_render_js
from bs4 import BeautifulSoup
import time

class osint_bianlian(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)
        self.base_url = url.rstrip("/")  # URL 마지막 슬래시 제거
        self.progress = True

    def using_bs4(self):
        html = self.response.text
        bsobj = BeautifulSoup(html, 'html.parser')
        object_table = bsobj.find_all("section", class_="list-item")

        for section in object_table:
            # 제목
            title_tag = section.find("h1", class_="title")
            title_link = title_tag.find("a") if title_tag else None
            title = title_link.text.strip() if title_link else "No Title"

            # 링크
            link = f"{self.base_url}{title_link['href']}" if title_link else "No URL"

            # 설명
            description_tag = section.find("div", class_="description")
            description = description_tag.text.strip() if description_tag else "No Description"

            # 회사 데이터 상세 내용
            company_details_tag = section.find("div", class_="company-details")
            company_details = company_details_tag.text.strip() if company_details_tag else "No Company Details"

            # 결과 저장
            result = {
                "title": title,
                "link": link,
                "Description": description,
            }
            self.result[title] = result

    def next_page(self):
        while self.progress:
            time.sleep(1)
            super().tor_playwright_crawl()
            self.using_bs4()
            try:
                next_button = self.page.locator("span.page-item.page-next > a.page-link")
                if not next_button or not next_button.is_visible():
                    break
                next_button.click()
                self.page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Error while navigating pages: {e}")
                break
                  
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
        return self.result