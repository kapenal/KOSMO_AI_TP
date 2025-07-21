from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# [1. 크롬 옵션 설정]
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# [2. URL 목록]
urls = {
    '넷플릭스': 'https://m.kinolights.com/ranking/netflix',
    '티빙': 'https://m.kinolights.com/ranking/tving',
    '디즈니 플러스': 'https://m.kinolights.com/ranking/disney',
    '박스오피스': 'https://m.kinolights.com/ranking/boxoffice'
}

# [3. 웹드라이버 실행]
driver = webdriver.Chrome(options=options)

# [4. 크롤링]
all_ranklists = {}

for category, url in urls.items():
    print(f"크롤링 중: {category} ...")
    driver.get(url)
    time.sleep(3)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    title = [t.get_text(strip=True) for t in soup.select('#contents .content-ranking-list .info__title span')][:10]
    type_ = [t.get_text(strip=True) for t in soup.select('#contents .content-ranking-list .info__subtitle span')][:10]
    poster_img = []
    DEFAULT_IMAGE = "../img/unimg.jpg"
    for container in soup.select('ul.content-ranking-list li.ranking-item'):
        img_tags = container.select('img.image-container__image')
        for img in img_tags:
            if img.has_attr('src') and img['src'].startswith('http'):
                DEFAULT_IMAGE = img['src']
                break
        poster_img.append(DEFAULT_IMAGE)
    poster_img = poster_img[:10]  # 들여쓰기 고침

    # [7. 합치기 및 저장]
    ranklist = list(zip(title, type_, poster_img))
    all_ranklists[category] = ranklist

driver.quit()

# 출력 확인
for category, ranklist in all_ranklists.items():
    print(f"\n=== {category} ===")
    for idx, (title, type_, poster_img) in enumerate(ranklist, 1):
        print(f"{idx}. 제목: {title}, 장르/방송일: {type_}, 이미지 URL: {poster_img}")

# -----------------------------------------------------------------------json 으로 변환
import json, os

folder_path = "public/mj_data"
json_path = os.path.join(folder_path, "OttRanking.json")

data_dict = {}

for category, ranklist in all_ranklists.items():
    
    if category not in data_dict:
        data_dict[category] = []

    for title, typ, poster in ranklist:
        data_dict[category].append({
            "제목": title,
            "장르": typ,
            "포스터": poster
        })

with open(json_path, 'w', encoding='utf-8') as jf:
    json.dump(data_dict, jf, ensure_ascii=False, indent=2)
