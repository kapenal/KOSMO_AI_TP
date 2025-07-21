from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# 1. 셀레니움 옵션 설정
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(options=options)

# 2. 페이지 열기
url = "https://m.kinolights.com/title/130583?tab=review"
driver.get(url)
time.sleep(3)  # 로딩 대기

# 3. 전체 페이지 소스 가져오기
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# 4. 리뷰 카드 선택
review_cards = soup.select('.review-card')  # 기본 리뷰 카드

review_list = []
for card in review_cards:
    content_tag = card.select_one('.review-card__desc')
    like_tag = card.select_one('.review-card__like')
    
    if content_tag and like_tag:
        content = content_tag.get_text(strip=True)
        like = int(like_tag.get_text(strip=True).replace('좋아요', '').strip())
        review_list.append({'리뷰': content, '좋아요': like})

# 5. 좋아요 순 정렬 및 상위 10개 선택
sorted_reviews = sorted(review_list, key=lambda x: x['좋아요'], reverse=True)
top_10_reviews = sorted_reviews[:10]

print("상위 10개 리뷰:", top_10_reviews)

# # 6. CSV 저장
# df = pd.DataFrame(top_10_reviews)
# df.to_csv('top10_reviews.csv', index=False, encoding='utf-8-sig')

# print("✅ 'top10_reviews.csv' 파일 저장 완료!")