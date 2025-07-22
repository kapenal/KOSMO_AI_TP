import json
import sys
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# User-Agent 설정 (브라우저처럼 위장)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

# 인자 확인
movie_id = sys.argv[1]
url = f'https://m.kinolights.com/title/{movie_id}'

# URL로 GET 요청 보내기
response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')

# [3. 정보 가져오기]
# 제목
title_tag = soup.select_one('.title-kr')
title = title_tag.get_text(strip=True) if title_tag else ""

# 장르
genres_tags = soup.select('#contents > div.info.tab-item > section:nth-child(1) > ul > li:nth-child(2) > span.item__body')
if genres_tags:
    genres = [g.get_text(strip=True) for g in genres_tags]
else:
    genres = []  # 없으면 빈 리스트로 처리

# 연도
year_tag = soup.select_one('#contents > div.info.tab-item > section:nth-child(1) > ul > li:nth-child(4) > span.item__body')
year = year_tag.get_text(strip=True) if year_tag else ""

# 평점
rating_tag = soup.select_one('.movie-star-wrap > .score') # 실제 클래스명 확인 필요
rating = rating_tag.get_text(strip=True) if rating_tag else ""
rating = rating + "점"
# 이미지
img_tag = soup.select_one('.poster img')  # 더 유연한 셀렉터
if img_tag and img_tag.has_attr('src'):
    img = img_tag['src']
else:
    img = None

# 감독
staff_tag = soup.select_one('.staffList_0')
staff = title_tag.get_text(strip=True) if title_tag else ""

# 줄거리
overview_tag = soup.select_one('.synopsis__text-wrap')
overview = overview_tag.get_text(strip=True) if overview_tag else ""

if overview.endswith("더보기"):
    overview = overview[:-3]

# 결과를 딕셔너리로 정리
movie_info = {
    "제목": title or "정보 없음",
    "장르": genres,
    "연도": year or "정보 없음",
    "평점": rating or "정보 없음",
    "포스터": img or "정보 없음",
    "감독" : staff or "정보 없음",
    "줄거리" : overview or "정보 없음"
}

# JSON 문자열 출력 (한글 깨짐 방지용 ensure_ascii=False)
print(json.dumps(movie_info, ensure_ascii=False))