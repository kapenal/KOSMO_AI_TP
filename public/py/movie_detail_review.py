import json
import sys
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# User-Agent 설정 (브라우저처럼 위장)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

# 인자 확인
movie_id = sys.argv[1]
url = f'https://m.kinolights.com/title/{movie_id}?tab=review'

# URL로 GET 요청 보내기
response = requests.get(url, headers=headers)

# 페이지 소스 가져오기
soup = BeautifulSoup(response.text, 'html.parser')

# 리뷰 카드 선택
review_cards = soup.select('section.review-list-section article')
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

# 결과 JSON 출력
json_data = json.dumps(review_list, ensure_ascii=False, indent=2)
print(json_data)