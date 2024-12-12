import sys, os
from default.basic_tor import osint_tor_default
from bs4 import BeautifulSoup
import re

class osint_cactus(osint_tor_default):
    def __init__(self, url):
        super().__init__(url)
        self.totalResults = {}
        self.baseUrl=url

    def request_default_url(self):
        try:
            response = self.session.get(self.url, verify=False)
            self.response = response
        except Exception as e:
            print(f"Error at request_default_url : {e}")
            exit(1)

    def using_bs4(self):
        html = self.response.text
        bsobj = BeautifulSoup(html, 'html.parser')
        results={}
        for idx, h2 in enumerate(bsobj.find_all('h2', class_='text-[16px] font-bold leading-6 text-white')):
            parts = re.split(r'\\', h2.text)
            if len(parts) >= 3:
                company = parts[0].strip()
                country = parts[2].strip()

            # h2와 연결된 <a> 태그의 href 추출
            href = h2.find_parent('a')['href']
            fullUrl = self.baseUrl + href
            print(f"Processing URL: {fullUrl}")
            # 새로운 URL에서 세부 정보 가져오기
            formatted_date, data_description = self.details(fullUrl)

            # 결과 딕셔너리에 저장
            results[idx] = {
                'company': company,
                'country': country,
                'href': fullUrl,
                'updateDate': formatted_date,
                'DATA DESCRIPTIONS': data_description
            }

        return results

    def details(self,url):
        self.make_tor_session()
        response = self.session.get(url, verify=False)
        new_html = response.text
        new_soup = BeautifulSoup(new_html, 'html.parser')

        # 날짜 추출 및 포맷 변경
        formatted_date = None
        data_description = None

        update_element = new_soup.find('mark', class_='marker-yellow')
        if update_element and update_element.find('strong'):
            update_date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', update_element.text)
            if update_date_match:
                date_str = update_date_match.group(1)
                day, month, year = date_str.split('.')
                formatted_date = f"{year}{month}{day}"

        # DATA DESCRIPTIONS 추출
        data_description_element = new_soup.find('mark', string='DATA DESCRIPTIONS:')
        if data_description_element:
            data_description = data_description_element.find_parent('p').text.split('DATA DESCRIPTIONS:')[-1].strip()

        return formatted_date, data_description

    def process(self):
        super().process()
        #for i in range(1,):
        for i in [1]:
            self.url=self.baseUrl+f'?page={i}'
            self.request_default_url()
            print(self.url)
            self.totalResults.update({f'{i}page':self.using_bs4()})

        print(self.totalResults)


def main():
    url = "https://cactusbloguuodvqjmnzlwetjlpj6aggc6iocwhuupb47laukux7ckid.onion/"
    cactus = osint_cactus(url)
    cactus.process()


if __name__ == "__main__":
    main()
