# [1. 데이터 전처리]

# 1. 키노라이츠 - 트랜드 랭킹 스크레이핑
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os, csv, time

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 메인
url = 'https://m.kinolights.com/ranking/kino'
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(2)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

detail_base_url = "https://m.kinolights.com"
movie_detail_Link = soup.select('#contents .content-list-card__body')
movie_links = []
for detail_href in movie_detail_Link:
    hrefi = detail_href.get('href')
    if hrefi:
        full_url = detail_base_url + hrefi + "?tab=review"
        movie_links.append(full_url)
print(movie_links)

# [4. 상세 정보 리뷰 페이지에서 리뷰를 전부 크롤링 ]
review_texts = []

for link in movie_links:
    print(f"크롤링 중: {link}")
    driver.get(link)
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.select_one("h2").get_text(strip=True)
    reviews = soup.select('h5')

    count = 0
    for r in reviews:
        text = r.get_text(strip=True).strip()
        if text:
            review_texts.append([title, text])
            count += 1
    print(f"---------- {count} 개의 리뷰 크롤링")

# CSV 파일로 저장
folder_path = r"E:/KOSMO/TeamProject/KOSMO_AI_TP/public/mj_data/"
file_path = os.path.join(folder_path, "TrendRankReviews.csv")

# 폴더가 없으면 생성
os.makedirs(folder_path, exist_ok=True)

with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['movie_title', 'review'])  # 헤더 작성
    writer.writerows(review_texts)  # 리뷰 데이터 작성

print(f"리뷰가 '{file_path}' 파일로 {len(review_texts)}개 저장되었습니다.")
print("크롤링 완료! reviews.csv 생성")

driver.quit()