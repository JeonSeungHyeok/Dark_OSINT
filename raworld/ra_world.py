from default.basic_tor import osint_tor_default
from bs4 import BeautifulSoup
import re
import chardet

class osint_rawolrd(osint_tor_default):
    def __init__(self, url):
        super().__init__(url)
        self.base_url = url.rstrip("/")  # URL 마지막 슬래시 제거
        self.progress = True
        self.result = {}
        
    def request_default_url(self):
        try:
            response = self.session.get(self.url, verify=False)
            # 자동으로 인코딩 감지
            result = chardet.detect(response.content)
            encoding = result['encoding']
            response.encoding = encoding  # 인코딩을 감지된 값으로 설정
            self.response = response
        except Exception as e:
            print(f"Error at request_default_url : {e}")
            exit(1)
            
    def using_bs4(self):
        html = self.response.text
        bsobj = BeautifulSoup(html, 'html.parser')
        
        portfolio_items = bsobj.find_all("div", class_="portfolio-content")
        
        for item in portfolio_items:
          link = item.find('a')
          if link:
            title = link.text.strip()
            href = link['href'].strip()
            full_url = self.base_url + href
            
          time_element = item.find("div", class_="portfolio_content")
          time = time_element.text.strip() if time_element else 'none'
          
          site, content = self.details(full_url)
          
          result = {
            "title": title,
            "link": full_url,
            #"times": time,
            "site": site,
            "all data": content
          }
          self.result[title]=result
          #print(result)
          
    def details(self,url):
      self.make_tor_session()
      response = self.session.get(url, verify=False)
      # 자동으로 인코딩 감지
      result = chardet.detect(response.content)
      encoding = result['encoding']
      response.encoding = encoding  # 인코딩을 감지된 값으로 설정
      new_html = response.text
      newSoup = BeautifulSoup(new_html, 'html.parser')
      site, content = None, None
      
      site_element = newSoup.find('a', href=True, string=re.compile(r'https://'))
      site = site_element['href'] if site_element else 'none'

      content_element = newSoup.find('h5', text="Content:")
      if content_element:
          next_div = content_element.find_next('div', class_='black-background') 
          if next_div:
              content = ', '.join(sorted([item.strip() for item in next_div.decode_contents().splitlines() if item.strip()]))
          else:
              content = 'none'
      else:
          content = 'none'

      return site, content
    
    def remove_char(self, key):
        for char in ['#', ':', '.']:
            key = key.replace(char, '').lower()
        return key.lower()

    def process(self):
        super().process()
        #self.url=self.base_url
        #self.request_default_url()
        #self.using_bs4()
        return self.result