from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

LOGIN_URL = "http://quotes.toscrape.com/login"
USER_ID = "abc123xyz789_test"
PASSWORD = "Scraping_Test_2026_99x"
MAX_PAGE = 5

def create_driver():
  options = Options()
  return webdriver.Chrome(options=options)

def login(driver, wait):
  driver.get(LOGIN_URL)

  wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(USER_ID)
  driver.find_element(By.ID, "password").send_keys(PASSWORD)

  driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

  wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Logout")))
  print("ログイン成功")

def scrape_quotes(driver, wait):
  data = []

  for page in range(MAX_PAGE):
    print(f"{page+1}ページ目")

    quotes = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "quote")))

    for quote in quotes:
      text = quote.find_element(By.CLASS_NAME, "text").text.strip('“”')
      author = quote.find_element(By.CLASS_NAME, "author").text

      data.append({
        "名言": text,
        "作者": author
      })

    if not go_next_page(driver, wait):
      break

  return data

def go_next_page(driver, wait):
  try:
    next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next > a")))
    next_btn.click()

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "quote")))
    return True
  
  except:
    print("次ページなし")
    return False
  
def save_csv(data):
  df = pd.DataFrame(data)
  df.to_csv("quotes.csv", index=False, encoding="utf-8-sig")

def main():
  driver = create_driver()
  wait = WebDriverWait(driver, 10)

  try:
    login(driver, wait)
    data = scrape_quotes(driver, wait)
    save_csv(data)

  finally:
    driver.quit()
    print("終了")
    
if __name__ == "__main__":
  main()