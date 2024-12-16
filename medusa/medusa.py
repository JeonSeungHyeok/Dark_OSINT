from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from default.basic_tor import osint_tor_render_js
from captcha import CaptchaHandler

class osint_medusa(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)
        self.progress = True

    def using_bs4(self, html):
        bsobj = BeautifulSoup(html, 'html.parser')
        companies = bsobj.find_all("div", class_="card")
        
        for company in companies:
            try:
                title = company.find("h3", class_="card-title").get_text(strip=True)
                description = company.find("div", class_="card-body").find("p").get_text(strip=True)
                price_tag = company.find("div", class_="product__price-tag price-tag-warning")
                price = price_tag.find("p", class_="product__price-tag-price").get_text(strip=True) if price_tag else "No Price"
                countdown = company.find("ul", id="counter-list")
                if countdown:
                    time_elements = countdown.find_all("span")
                    time_units = ["D", "H", "M", "S"]
                    timer = " ".join(f"{elem.get_text(strip=True)}{unit}" for elem, unit in zip(time_elements, time_units))
                else:
                    timer = "No Time"
                updated_tag = company.find("div", class_="date-updated")
                update_date = updated_tag.find("span", class_="text-muted").get_text(strip=True) if updated_tag else "No Update Date"
                views_tag = company.find("div", class_="number-view")
                views = views_tag.find("span", class_="text-muted").get_text(strip=True) if views_tag else "No Views"
                
                result = {
                    "title": title,
                    "description": description,
                    "price": price,
                    "timer": timer,
                    "update_date": update_date,
                    "views": views
                }
                self.result[title] = result
            except Exception as e:
                print(f"Error extracting data: {e}")
    
    def crawl(self):
        captcha_handler = CaptchaHandler(self.url)  # CaptchaHandler 인스턴스를 생성
        captcha_handler.crawl_with_captcha(self.using_bs4)  # 크롤링 및 BS4 처리 호출
  
    def process(self):
        self.crawl()
        if self.browser:  # 크롤링 작업이 끝난 후 브라우저 종료
            self.browser.close()
        return self.result
