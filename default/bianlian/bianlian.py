from default.basic_tor import osint_tor_render_js
from bs4 import BeautifulSoup


class osint_bianlian(osint_tor_render_js):
    def __init__(self, url):
        super().__init__(url)
        self.base_url = url.rstrip("/")  # URL 끝 슬래시 제거
        self.result = {}

    def extract_readmore_data(self, page_content):
        """Readmore 페이지에서 데이터를 추출합니다."""
        soup = BeautifulSoup(page_content, 'html.parser')

        # 설명 추출
        description = soup.find("p").text.strip() if soup.find("p") else "No Description"

        # 전화번호 추출
        tel = []
        tel_elements = soup.find_all("div", class_="highlight")
        for element in tel_elements:
            for line in element.get_text(separator="\n", strip=True).split("\n"):
                if "Phone" in line or "Cell" in line:  # 'Phone' 또는 'Cell'이 포함된 라인만 추출
                    tel.append(line.strip())

        # 회사 사이트 추출
        site_tag = soup.find("a", href=True, string=lambda s: s and s.startswith("http"))
        site = site_tag["href"] if site_tag else "No Site"

        # 데이터 정보 추출 (data_info)
        data_info = []
        data_info_element = soup.select_one("strong:-soup-contains('Data description')")
        if data_info_element:
            ul = data_info_element.find_next("ul")
            if ul:
                data_info = [li.text.strip() for li in ul.find_all("li")]
        else:
            ul_elements = soup.find_all("ul")
            for ul in ul_elements:
                if ul.find_previous("strong", text=lambda t: "Data description" in t):
                    data_info = [li.text.strip() for li in ul.find_all("li")]
                    break

        if not data_info:
            data_info = ["No Data Info"]

        return {
            "description": description,
            "tel": tel,
            "site": site,
            "data_info": data_info
        }

    def using_bs4(self):
        """첫 페이지에서 데이터를 수집합니다."""
        html = self.response.text
        soup = BeautifulSoup(html, 'html.parser')
        sections = soup.find_all("section", class_="list-item")

        for section in sections:
            # 제목과 링크
            title_tag = section.find("h1", class_="title")
            title_link = title_tag.find("a") if title_tag else None
            title = title_link.text.strip() if title_link else "No Title"
            link = f"{self.base_url}{title_link['href']}" if title_link else "No URL"

            # 설명 추출
            description_tag = section.find("div", class_="description")
            description = description_tag.text.strip() if description_tag else "No Description"

            # readmore 페이지 데이터 가져오기
            readmore_data = {}
            if link != "No URL":
                for _ in range(2):  # 최대 2번 재시도
                    try:
                        self.page.goto(link, timeout=60000, wait_until="domcontentloaded")
                        detail_html = self.page.content()
                        readmore_data = self.extract_readmore_data(detail_html)
                        break
                    except Exception:
                        pass

            # 결과 저장 (title을 명시적으로 추가)
            self.result[title] = {
                "title": title,
                "link": link,
                "Description": readmore_data.get("description", description),
                "site": readmore_data.get("site", "No Site"),
                "tel": readmore_data.get("tel", []),
                "data_info": readmore_data.get("data_info", [])
            }

    def process(self):
        """브라우저를 초기화하고 데이터를 수집합니다."""
        super().init_browser()  # 브라우저 초기화
        try:
            super().tor_playwright_crawl()  # Tor 크롤링 실행
            self.using_bs4()  # 데이터 처리
        except Exception as e:
            print(f"[ERROR] Process failed: {e}")
        finally:
            super().close_browser()  # 브라우저 종료
        return self.result  # 결과 반환