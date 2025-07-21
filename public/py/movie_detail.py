from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# [1. 페이지 요청]
url = 'https://m.kinolights.com/title/130583'
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(3)  # JS 로딩 대기

# [2. html 파싱]
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# [3. 정보 가져오기]
# 제목
title = soup.select_one('.title-kr')
print("제목:", title.get_text() if title else "제목 없음")

# 장르
genres = soup.select('#contents > div.info.tab-item > section:nth-child(1) > ul > li:nth-child(2) > span.item__body')
print("장르:")
for g in genres:
    print("-", g.get_text())

# 연도
year = soup.select_one('#contents > div.info.tab-item > section:nth-child(1) > ul > li:nth-child(4) > span.item__body')
print("연도:", year.get_text() if year else "없음")

# 평점
rating = soup.select_one('.score')  # 실제 클래스명 확인 필요
print("평점:", rating.get_text() if rating else "없음")

# 리뷰
# 리뷰 전체 수집
review_cards = soup.select('.review-card')

# 각 리뷰에서 텍스트와 좋아요 수 추출
review_list = []
for card in review_cards:
    content = card.select_one('.review-card__desc')
    like = card.select_one('.review-card__like')

    if content and like:
        review_text = content.get_text(strip=True)
        like_count = int(like.get_text(strip=True))
        review_list.append((review_text, like_count))

# 좋아요 순으로 정렬 후 상위 10개 추출
sorted_reviews = sorted(review_list, key=lambda x: x[1], reverse=True)
top_reviews = sorted_reviews[:10]

# 출력
print("👍 좋아요 순 리뷰 Top 10:")
for review, like in top_reviews:
    print(f"- {review} (좋아요 {like}개)")


# print("리뷰 (최대 10개):")
# for review in reviews[:10]:
#     print("-", review.get_text(strip=True))

driver.quit()