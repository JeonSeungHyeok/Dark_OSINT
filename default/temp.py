from playwright.sync_api import sync_playwright
from requests.models import Response



# 사용 예제
class MyCrawler:
    def __init__(self, url):
        self.url = url
        self.response = None

    def tor_playwright_crawl(self):
        with sync_playwright() as p:
            browser = p.firefox.launch(
                headless=True,
                proxy={"server": "socks5://127.0.0.1:9050"}
            )
            page = browser.new_page()
            try:
                page.goto(self.url, timeout=60000)
                page.wait_for_timeout(5000)
                html = page.content()
                response = Response()
                response._content = html.encode('utf-8')  # HTML 바이너리로 설정
                response.status_code = 200  # 성공 코드 설정
                response.url = self.url  # 요청된 URL
                response.headers = {"Content-Type": "text/html; charset=utf-8"}
                self.response = response
                print("Crawling successful")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                browser.close()

crawler = MyCrawler("https://check.torproject.org")
crawler.tor_playwright_crawl()
if crawler.response:
    print(f"Response URL: {crawler.response.url}")
    print(f"Response Status Code: {crawler.response.status_code}")
    print(f"Response Content: {crawler.response.text[:500]}...")  # 출력할 HTML 내용 길이 제한
