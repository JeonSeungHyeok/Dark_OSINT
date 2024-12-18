from playwright.sync_api import sync_playwright

class CaptchaHandler:
    def __init__(self, url):
        self.url = url

    def handle_captcha(self, page):
        try:
            print("CAPTCHA를 해결한 후, 엔터 키를 누르세요...")
            input()  # 사용자가 CAPTCHA를 해결한 후 엔터 키를 누름
            print("CAPTCHA 해결 완료!")
        except Exception as e:
            print(f"Error handling CAPTCHA: {e}")

    def crawl_with_captcha(self, using_bs4_callback):
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False, proxy={"server": "socks5://127.0.0.1:9050"})
            page = browser.new_page()
            page.goto(self.url, timeout=60000)

            # CAPTCHA 해결 프로세스 호출
            self.handle_captcha(page)

            # HTML 로드 및 데이터 처리
            html = page.content()
            using_bs4_callback(html)  # 외부에서 전달된 BS4 처리 함수 호출

            # 페이징 처리
            while True:
                try:
                    next_button = page.locator("div.next-page-btn")
                    if next_button.is_visible() and not next_button.is_disabled():
                        next_button.click()
                        page.wait_for_timeout(2000)
                        html = page.content()
                        using_bs4_callback(html)
                    else:
                        break
                except Exception as e:
                    print(f"Error while navigating pages: {e}")
                    break

            browser.close()
