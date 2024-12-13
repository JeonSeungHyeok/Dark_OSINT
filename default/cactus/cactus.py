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
        for h2 in bsobj.find_all('h2', class_='text-[16px] font-bold leading-6 text-white'):
            parts = re.split(r'\\', h2.text)
            if len(parts) >= 3:
                title = parts[0].strip()
                country = parts[2].strip()
                dataSize = parts[3].strip()

            # h2와 연결된 <a> 태그의 href 추출
            href = h2.find_parent('a')['href']
            fullUrl = self.baseUrl + href
            print(f"Processing URL: {fullUrl}")
            # 새로운 URL에서 세부 정보 가져오기
            formattedDate, dataDescription, address, tel, site, images, comDescription = self.details(fullUrl)

            allData=f'size({dataSize}) {dataDescription}'

            # 결과 딕셔너리에 저장
            results = {
                'title': title,
                'Description': comDescription,
                'site': site,
                'address': address,
                'country': country,
                'tel': tel,
                'images':images,
                'updateDate': formattedDate,
                'all data': allData
            }
            self.totalResults[title]=results

        return results

    def details(self,url):
        self.make_tor_session()
        response = self.session.get(url, verify=False)
        new_html = response.text
        newSoup = BeautifulSoup(new_html, 'html.parser')
        # 날짜 추출 및 포맷 변경
        formattedDate = None
        dataDescription = None

        update_element = newSoup.find('mark', class_='marker-yellow')
        if update_element and update_element.find('strong'):
            update_date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', update_element.text)
            if update_date_match:
                date_str = update_date_match.group(1)
                day, month, year = date_str.split('.')
                formattedDate = f"{year}{month}{day}"

        # DATA DESCRIPTIONS 추출
        dataDescriptionElement = newSoup.find('mark', string='DATA DESCRIPTIONS:')
        if dataDescriptionElement:
            dataDescription = dataDescriptionElement.find_parent('p').text.split('DATA DESCRIPTIONS:')[-1].strip()

        # Address 추출
        addressElement = newSoup.find(string=re.compile(r'Address:'))
        address = None
        if addressElement:
            address = addressElement.text.split('Address:')[-1].split('Phone Number:')[0].strip()
        
        # Phone Number 추출
        telElement = newSoup.find(string=re.compile(r'Phone Number:'))
        tel = None
        if telElement:
            tel = telElement.text.split('Phone Number:')[-1].strip()

        # Website URL 추출
        websiteElement = newSoup.find('a', href=True, string=re.compile(r'https://'))
        site = websiteElement['href'] if websiteElement else None

        # 이미지 추출 (리스트 형태로)
        imageElements = newSoup.find_all('img')
        images = [f"{self.baseUrl}{img['src']}" for img in imageElements if 'src' in img.attrs]

        markerElement = newSoup.find('mark', class_='marker-yellow')
        comDescription = None

        if markerElement:
            # 마커 다음에 나오는 첫 번째 <p> 태그 찾기
            nextP = markerElement.find_next('p')
            if nextP:
                comDescription = nextP.text.strip()

        return formattedDate, dataDescription, address, tel, site, images, comDescription

    def process(self):
        super().process()
        #for i in range(1,):
        for i in [1]:
            self.url=self.baseUrl+f'?page={i}'
            self.request_default_url()
            self.using_bs4()

        return self.totalResults


def main():
    url = "https://cactusbloguuodvqjmnzlwetjlpj6aggc6iocwhuupb47laukux7ckid.onion/"
    cactus = osint_cactus(url)
    cactus.process()


if __name__ == "__main__":
    main()
