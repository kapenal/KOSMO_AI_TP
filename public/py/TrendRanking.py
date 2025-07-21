# 1. 키노라이츠 - 트랜드 랭킹 스크레이핑
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
# 기본 대체 이미지 경로 (예: 로컬 경로나 CDN 경로)
DEFAULT_IMAGE = "../img/unimg.jpg"

poster_img = []

# 'responsive-image__image-container'만 선택 (fallback 제외)
for div in soup.select('div.responsive-image__image-container:not(.responsive-image__image-container--fallback)'):
    img = div.find('img')  # img 태그가 있는지 확인

    if img and img.get('src') and img['src'].startswith('http'):
        poster_img.append(img['src'])  # 정상적인 http 이미지
    else:
        poster_img.append(DEFAULT_IMAGE)  # 비어있거나 base64 → 기본 이미지로 대체

# 각 데이터 합치기
ranklist = list(zip(rankNum, title, type, poster_img))
print(ranklist)

# -----------------------------------------------------------------------json 으로 변환
import json, os

folder_path = "public/mj_data"
json_path = os.path.join(folder_path, "TrendRanking.json")
data_list = []

for rank, title, typ, poster in ranklist:
    data_list.append({
        "순위": rank,
        "제목": title,
        "장르": typ,
        "포스터": poster
    })

with open(json_path, 'w', encoding='utf-8') as jf:
    json.dump({"movies": data_list}, jf, ensure_ascii=False, indent=2)
