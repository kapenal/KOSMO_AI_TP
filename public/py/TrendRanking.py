# 1. 키노라이츠 - 트랜드 랭킹 스크레이핑
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time, os, csv

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# [1. 페이지 요청]
url = 'https://m.kinolights.com/ranking/kino'
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(3)

# [2. html 파싱]
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# [3. 정보 가져오기]
# 랭킹 순위
rankNum = soup.select('#contents .content-ranking-list .rank__number span')
rankNum = [num.get_text(strip=True) for num in rankNum]
# 제목
title = soup.select('#contents .content-ranking-list .info__title span')
title = [t.get_text(strip=True) for t in title]
# 장르, 방송일
type = soup.select('#contents .content-ranking-list .info__subtitle span')
type = [t.get_text(strip=True) for t in type]
# 포스터 이미지
poster_img = soup.select('ul.content-ranking-list img.image-container__image')
poster_img = [img['src'] for img in poster_img if img.has_attr('src')]
# 각 데이터 합치기
ranklist = list(zip(rankNum, title, type, poster_img))
print(ranklist)
