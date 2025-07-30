import re
import sys
import io
import json
import time
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from soynlp.word import WordExtractor
from soynlp.tokenizer import LTokenizer

# 한글 출력 문제 방지 (필요 시 사용)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 실행 인자(영화 ID) 없으면 에러 메시지 출력 후 종료
if len(sys.argv) < 2:
    print(json.dumps({"error": "검색어 인자가 없습니다."}, ensure_ascii=False))
    sys.exit(1)

movie_id = sys.argv[1]
url = f'https://m.kinolights.com/title/{movie_id}?tab=review'

# Selenium 크롬 드라이버 옵션 설정 (헤드리스, User-Agent 등)
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(1)  # 페이지 로딩 대기

# 리뷰가 포함된 스크롤 영역 요소 찾기
scrollable = driver.find_element(By.ID, "content__body")

prev_count = 0
no_change_count = 0
max_no_change = 2  # 더 이상 리뷰가 늘어나지 않을 때 멈추기 위한 기준

# 무한 스크롤하면서 리뷰 더 불러오기 시도
while True:
    reviews = driver.find_elements(By.CSS_SELECTOR, 'section.review-list-section article')
    current_count = len(reviews)

    if current_count > prev_count:
        prev_count = current_count
        no_change_count = 0
    else:
        no_change_count += 1

    if no_change_count >= max_no_change:  # 일정 횟수 리뷰 수 변화 없으면 종료
        break

    if reviews:
        # 마지막 리뷰 요소로 스크롤 이동
        driver.execute_script("arguments[0].scrollIntoView(true);", reviews[-1])
    else:
        # 리뷰 없으면 스크롤 영역 맨 아래로 이동
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)

    time.sleep(1)  # 페이지 로딩 대기

html = driver.page_source
driver.quit()  # 브라우저 종료

# BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(html, 'html.parser')

# 리뷰 카드(글) 요소 선택
review_cards = soup.select('section.review-list-section article')

review_list = []
for card in review_cards:
    # 리뷰 제목(내용) 선택
    content = card.select_one('.contents__title')
    content_text = content.get_text(strip=True) if content else ''
    if content_text:
        review_list.append(content_text)

# 리뷰 텍스트들을 하나로 합침
text = " ".join(review_list)

# 한글과 공백만 남기고 모두 제거
text = re.sub(r'[^가-힣\s]', '', text)

# soynlp 단어 추출
word_extractor = WordExtractor()
word_extractor.train(text)
word_scores = word_extractor.extract()

# 단어 결속력 점수를 이용해 LTokenizer 초기화
tokenizer = LTokenizer(scores={word: float(score.cohesion_forward) for word, score in word_scores.items()})

# 텍스트 토크나이즈
tokens = tokenizer.tokenize(text)

# 불용어 목록 = 띄어쓰기 기준
stopwords = ['그', '안', '더', '이', '의', '을', '는', '도', '로', '과', '와', '께', '영화']

# 토큰에서 접미사 제거 함수 = 단어 맨 마지막 글자 기준
def filter_suffix(token):
    suffixes = ['이', '의', '을', '는', '도', '과', '와', '가', '과는', '와는', '은', '를', '으로']
    for suffix in suffixes:
        if token.endswith(suffix) and len(token) > len(suffix):
            return token[:-len(suffix)]
    return token

# 불용어 및 길이 조건으로 기본 필터링
tokens_filtered_basic = [token for token in tokens if token not in stopwords and len(token) > 1]

filtered_tokens = []
for token in tokens_filtered_basic:
    # 접미사 제거 후 재검사
    token_filtered = filter_suffix(token)
    if token_filtered not in stopwords and len(token_filtered) > 1:
        filtered_tokens.append(token_filtered)

# 단어 빈도 계산 후 상위 20개 선택
count = Counter(filtered_tokens)
top_items = count.most_common(20)

# 결과 JSON 형식으로 변환
data = [{"text": word, "value": freq} for word, freq in top_items]

# 출력
print(json.dumps(data, ensure_ascii=False))
