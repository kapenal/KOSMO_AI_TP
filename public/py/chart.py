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

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

if len(sys.argv) < 2:
    print(json.dumps({"error": "검색어 인자가 없습니다."}, ensure_ascii=False))
    sys.exit(1)

# 인자 확인
movie_id = sys.argv[1]
url = f'https://m.kinolights.com/title/{movie_id}?tab=review'

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(1)

scrollable = driver.find_element(By.ID, "content__body")

prev_count = 0
no_change_count = 0
max_no_change = 2

while True:
    reviews = driver.find_elements(By.CSS_SELECTOR, 'section.review-list-section article')
    current_count = len(reviews)

    if current_count > prev_count:
        prev_count = current_count
        no_change_count = 0
    else:
        no_change_count += 1

    if no_change_count >= max_no_change:
        break

    if reviews:
        driver.execute_script("arguments[0].scrollIntoView(true);", reviews[-1])
    else:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)

    time.sleep(1)

html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, 'html.parser')
review_cards = soup.select('section.review-list-section article')

review_list = []
for card in review_cards:
    content = card.select_one('.contents__title')
    content_text = content.get_text(strip=True) if content else ''
    if content_text:
        review_list.append(content_text)

text = " ".join(review_list)
text = re.sub(r'[^가-힣\s]', '', text)

word_extractor = WordExtractor()
word_extractor.train(text)
word_scores = word_extractor.extract()

tokenizer = LTokenizer(scores={word: float(score.cohesion_forward) for word, score in word_scores.items()})
tokens = tokenizer.tokenize(text)

stopwords = ['그', '안', '더', '이', '의', '을', '는', '도', '로', '과', '와', '께']

def filter_suffix(token):
    suffixes = ['이', '의', '을', '는', '도', '과', '와', '가', '과는', '와는', '은', '를', '으로']
    for suffix in suffixes:
        if token.endswith(suffix):
            return token[:-len(suffix)]
    return token

# '영화' 제거 추가
filtered_tokens = []
for token in tokens:
    if token in stopwords or len(token) <= 1:
        continue
    base = filter_suffix(token)
    if base != '영화':
        filtered_tokens.append(base)

count = Counter(filtered_tokens)
top_items = count.most_common(20)

data = [{"text": word, "value": freq} for word, freq in top_items]
print(json.dumps(data, ensure_ascii=False))