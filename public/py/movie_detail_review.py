import json
import sys
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

#셀레니움 옵션 설정
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(options=options)

# 인자 확인
movie_id = sys.argv[1]
url = f'https://m.kinolights.com/title/{movie_id}?tab=review'

#페이지 열기
# url = "https://m.kinolights.com/title/130583?tab=review"
driver.get(url)
time.sleep(2)  # 로딩 대기

#전체 페이지 소스 가져오기
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

#리뷰 카드 선택
review_cards = soup.select('section.review-list-section article')  # 기본 리뷰 카드
# print(review_cards)
review_list = []
for card in review_cards:
    name = card.select_one('.title__movie-title').get_text(strip=True)
    content = card.select_one('.contents__title').get_text(strip=True)
    like = card.select_one('.user-star-score').get_text(strip=True)

    review_list.append({
        '닉네임': name,
        '리뷰': content,
        '평점': like
    })
    
json_data = json.dumps(review_list, ensure_ascii=False, indent=2)

print(json_data)