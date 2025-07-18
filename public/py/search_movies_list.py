#search_movies_list.py
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 2:
        print(json.dumps({"error": "검색어 인자가 없습니다."}, ensure_ascii=False))
        sys.exit(1)

input_title = sys.argv[1]
search_text = input_title
encoded_text = quote(search_text)
url = f"https://m.kinolights.com/search?keyword={encoded_text}"

# User-Agent 설정 (브라우저처럼 위장)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

# Request 객체 생성
req = urllib.request.Request(url, headers=headers)

# HTML 요청 및 파싱
res = urllib.request.urlopen(req)
soup = BeautifulSoup(res, "html.parser")

# id가 searchContentList인 div 찾기
search_div = soup.find("div", id="searchContentList")

if search_div:
    movies = []
    a_tags = search_div.find_all("a")  # 모든 a 태그
    for a in a_tags:
        href = a.get('href')
        title_tag = a.select_one('.metadata__title')
        genres_tag = a.select_one('.metadata__subtitle')
        img = a.select_one('img')['src'] if a.select_one('img') else ''
        title = title_tag.get_text(strip=True) if title_tag else ''
        genres = genres_tag.get_text(strip=True) if genres_tag else ''
        
        movies.append({
            "link": href,
            "title": title,
            "genres": genres,
            "img": img
        })

    result = {
    "input_title": search_text,
    "movies": movies
    }
    
    # JSON 문자열 출력
    json_result = json.dumps(result, ensure_ascii=False, indent=2)
    print(json_result)
else:
    print("searchContentList 영역을 찾을 수 없습니다.")