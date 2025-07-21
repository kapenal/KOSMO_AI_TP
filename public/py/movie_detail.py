import json
import sys
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 인자 확인
movie_id = sys.argv[1]
url = f'https://m.kinolights.com/title/{movie_id}'

# [1. 페이지 요청]
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(3)  # JS 로딩 대기

# [2. html 파싱]
html = driver.page_source

# 여기 바로 추가
# print("=== 페이지 HTML 일부 ===")
# print(html[:1000])  # HTML 앞부분 출력해보기
# print("=====================")

soup = BeautifulSoup(html, 'html.parser')

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
rating_tag = soup.select_one('.score')  # 실제 클래스명 확인 필요
rating = rating_tag.get_text(strip=True) if rating_tag else ""

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

driver.quit()

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