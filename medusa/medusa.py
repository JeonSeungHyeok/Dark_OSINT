from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json  # JSON 파일 저장을 위한 import

class osint_medusa:
    def __init__(self, url):
        self.url = url
        self.result = {}

    def using_bs4(self, html):
        bsobj = BeautifulSoup(html, 'html.parser')

        # 데이터 추출
        companies = bsobj.find_all("div", class_="card")
        for company in companies:
            try:
                title = company.find("h3", class_="card-title").get_text(strip=True)
                description = company.find("div", class_="card-body").find("p").get_text(strip=True)
                
                # 협박 금액 추출
                price_tag = company.find("div", class_="product__price-tag price-tag-warning")
                price = price_tag.find("p", class_="product__price-tag-price").get_text(strip=True) if price_tag else "No Price"
                
                # 마감 시간 추출 (4D 22H 57M 20S 형식으로)
                countdown = company.find("ul", id="counter-list")
                if countdown:
                    time_elements = countdown.find_all("span")
                    time_units = ["D", "H", "M", "S"]
                    time_remaining = " ".join(f"{elem.get_text(strip=True)}{unit}" for elem, unit in zip(time_elements, time_units))
                else:
                    time_remaining = "No Time"

                # 피해기업 링크 추출
                link_tag = company.find("a", href=True)
                link = link_tag["href"] if link_tag else "No Link"

                # 결과 저장
                result = {
                    "title": title,
                    "description": description,
                    "price": price,
                    "time_remaining": time_remaining,
                    "link": link
                }
                self.result[title] = result

            except Exception as e:
                print(f"Error extracting data: {e}")

    def handle_captcha(self, page):
        try:
            # CAPTCHA 해결을 위한 로직
            print("CAPTCHA를 해결한 후, 엔터 키를 누르세요...")
            input()  # 사용자가 CAPTCHA를 해결하고 엔터 키를 누를 때까지 대기
            print("CAPTCHA 해결 완료!")

        except Exception as e:
            print(f"Error handling CAPTCHA: {e}")

    def crawl(self):
        with sync_playwright() as p:
            # Firefox 실행
            browser = p.firefox.launch(headless=False, proxy={"server": "socks5://127.0.0.1:9050"})
            page = browser.new_page()

            # URL 접속
            page.goto(self.url, timeout=60000)

            # CAPTCHA 해결
            self.handle_captcha(page)

            # 페이지 내용 처리
            html = page.content()
            self.using_bs4(html)

            # 다음 페이지로 넘어가기
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

    def save_to_json(self):
        # 추출된 데이터를 JSON 파일로 저장
        with open('medusa_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(self.result, json_file, ensure_ascii=False, indent=4)

    def process(self):
        self.crawl()
        self.save_to_json()  # JSON 파일로 저장
        return self.result

def main():
    url = "http://xfv4jzckytb4g3ckwemcny3ihv4i5p4lqzdpi624cxisu35my5fwi5qd.onion/"  # 여기에 실제 URL 입력
    medusa = osint_medusa(url)
    result = medusa.process()
    print(result)

if __name__ == "__main__":
    main()
