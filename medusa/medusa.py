from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class osint_medusa:
    def __init__(self, url):
        self.url = url
        self.result = {}

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
                    time_remaining = " ".join(f"{elem.get_text(strip=True)}{unit}" for elem, unit in zip(time_elements, time_units))
                else:
                    time_remaining = "No Time"
                updated_tag = company.find("div", class_="date-updated")
                updated_date = updated_tag.find("span", class_="text-muted").get_text(strip=True) if updated_tag else "No Update Date"
                views_tag = company.find("div", class_="number-view")
                views = views_tag.find("span", class_="text-muted").get_text(strip=True) if views_tag else "No Views"
                
                result = {
                    "title": title,
                    "description": description,
                    "price": price,
                    "time_remaining": time_remaining,
                    "updated_date": updated_date,
                    "views": views
                }
                self.result[title] = result
            except Exception as e:
                print(f"Error extracting data: {e}")

    def handle_captcha(self, page):
        try:
            print("CAPTCHA를 해결한 후, 엔터 키를 누르세요...")
            input()  
            print("CAPTCHA 해결 완료!")
        except Exception as e:
            print(f"Error handling CAPTCHA: {e}")

    def crawl(self):
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False, proxy={"server": "socks5://127.0.0.1:9050"})
            page = browser.new_page()
            page.goto(self.url, timeout=60000)
            self.handle_captcha(page)
            html = page.content()
            self.using_bs4(html)
            while True:
                try:
                    next_button = page.locator("div.next-page-btn")
                    if next_button.is_visible() and not next_button.is_disabled():
                        next_button.click()
                        page.wait_for_timeout(2000)
                        html = page.content()
                        self.using_bs4(html)
                    else:
                        break
                except Exception as e:
                    print(f"Error while navigating pages: {e}")
                    break
            browser.close()

    def process(self):
        self.crawl()
        return self.result
