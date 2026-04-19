import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BookScraper:
    def __init__(self):
        self.base_url = 'https://books.toscrape.com/catalogue/page-{}.html'
        self.rate = 211
        self.results = []
        self.rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch_soup(self, url):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return BeautifulSoup(r.text, 'html.parser')
        
        except requests.RequestException as e:
            logging.error(f"URL取得失敗: {url} - {e}")
            return None
        
        finally:
            sleep(1)

    def parse_book(self, content):
        try:
            name = content.select_one('h3 a')['title']
            
            price_text = content.select_one('.price_color').text
            price_raw = float(re.sub(r"[^\d.]", "", price_text))
            yen = int(price_raw * self.rate)
            
            classes = content.find('p', class_='star-rating').get("class", [])
            rating_class = next((c for c in classes if c in self.rating_map), None)
            
            return {
                '商品名': name,
                '価格(円)': yen,
                '評価': self.rating_map.get(rating_class, 0)
            }
        
        except Exception as e:
            logging.warning(f"要素解析失敗: {e}")
            return None
        
    def run(self, max_pages=5):
        for i in range(1, max_pages + 1):
            logging.info(f"ページ {i} を処理中...")
            soup = self.fetch_soup(self.base_url.format(i))
            if not soup:
                continue

            contents = soup.find_all('li', class_='col-xs-6')

            for content in contents:
                data = self.parse_book(content)
                if data:
                    self.results.append(data)
        
        self.save_data()

    def save_data(self):
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        filename = f"books_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=None, encoding='utf-8-sig')
        logging.info(f"保存完了: {filename}")

if __name__ == "__main__":
    scraper = BookScraper()
    scraper.run(max_pages=3)