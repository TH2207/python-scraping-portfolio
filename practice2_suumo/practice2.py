import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

def get_property_iterator(max_pages=3):
    base_url = 'https://suumo.jp/chintai/saitama/sa_saitama/?page={}'
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    for page in range(1, max_pages + 1):
        print(f"--- ページ {page} 取得中 ---")

        try:
            res = requests.get(base_url.format(page), headers=headers, timeout=15)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div.cassetteitem')

        except requests.RequestException as e:
            print(f"ページ取得エラー: {e}")
            break

        for item in items:
            title_el = item.select_one('.cassetteitem_content-title')
            building_name = title_el.text.strip() if title_el else "不明"
            
            rows = item.select('tr.js-cassette_link')
            
            for row in rows:
                try:
                    rent_el = row.select_one('.cassetteitem_other-emphasis')
                    layout_el = row.select_one('.cassetteitem_madori')
                    cost_item = row.select_one('.cassetteitem_price--administration')

                    rent_text = rent_el.text.replace('万円', '').strip()
                    rent_val = float(rent_text)
                    
                    fee_text = cost_item.text.strip() if cost_item else ""
                    management_fee = "なし" if fee_text in ["", "-"] else fee_text
                    
                    yield {
                        '建物名': building_name,
                        '家賃(万円)': rent_val,
                        '間取り': layout_el.text.strip() if layout_el else "不明",
                        '管理費': management_fee
                    }

                except (IndexError, ValueError):
                    continue

        sleep(1.5)

data = list(get_property_iterator(max_pages=5))

if data:
    df = pd.DataFrame(data)
    print(f"\n平均家賃: {df['家賃(万円)'].mean():.2f}万円")
    df.to_csv('suumo_refined.csv', index=False, encoding='utf-8-sig')
else:
    print("データが取得できませんでした。")