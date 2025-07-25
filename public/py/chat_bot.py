from fastapi import FastAPI
from pydantic import BaseModel
import json
import re
import torch
from transformers import BertTokenizer, BertForQuestionAnswering
from fuzzywuzzy import fuzz, process
from collections import defaultdict

app = FastAPI()

# 데이터 불러오기
with open('data/movies_DB_partial.json', 'r', encoding='utf-8') as f:
    movies_db = json.load(f)

with open('data/megabox_cinema_with_showtimes.json', 'r', encoding='utf-8') as f:
    megabox_data = json.load(f)

# 모델 로드
tokenizer = BertTokenizer.from_pretrained("beomi/kcbert-base")
model = BertForQuestionAnswering.from_pretrained("beomi/kcbert-base")

# 지역명 집합 (소문자)
ALL_REGIONS = set()
for c in megabox_data:
    for r in c.get("region", []):
        ALL_REGIONS.add(r.lower())

class QARequest(BaseModel):
    question: str

def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()

def simple_movie_answer(question: str, movie: dict):
    q = question.lower()
    if "감독" in q:
        return movie.get('director', '감독 정보가 없습니다.')
    elif any(k in q for k in ["줄거리", "내용", "스토리"]):
        return movie.get('overview', '줄거리 정보가 없습니다.')
    elif any(k in q for k in ["장르", "종류"]):
        genres = movie.get('genres', [])
        return ", ".join(genres) if genres else "장르 정보가 없습니다."
    elif any(k in q for k in ["개봉", "날짜", "언제"]):
        return movie.get('release_date', '개봉일 정보가 없습니다.')
    elif any(k in q for k in ["평점", "점수", "평균"]):
        vote = movie.get('vote_average')
        if vote:
            return f"평점은 {vote}점 입니다."
        else:
            return "평점 정보가 없습니다."
    else:
        return None

def find_movie_exclude_animation(title: str):
    norm_title = normalize(title)
    for m in movies_db:
        genres = m.get('genres', [])
        if "애니메이션" in genres:
            continue
        if normalize(m['title_ko']) == norm_title:
            return m
    for m in movies_db:
        genres = m.get('genres', [])
        if "애니메이션" in genres:
            continue
        if norm_title in normalize(m['title_ko']):
            return m
    for m in movies_db:
        if normalize(m['title_ko']) == norm_title:
            return m
    for m in movies_db:
        if norm_title in normalize(m['title_ko']):
            return m
    return None

def parse_question(text: str):
    text = re.sub(r"[?!.，,.]", "", text)  # 문장부호 제거
    intent = None
    region = None
    cinema = None
    movie_title = None

    # 1) 의도 판단
    if any(k in text for k in ["위치", "어디", "주소", "장소", "어디"]):
        intent = "cinema_location"
    elif any(k in text for k in ["상영시간", "몇시", "상영", "시간"]):
        intent = "showtime"
    elif any(k in text for k in ["줄거리", "내용", "스토리", "감독", "장르", "평점", "개봉"]):
        intent = "movie_info"
    else:
        intent = "unknown"

    # 2) 지역명 찾기
    for r in ALL_REGIONS:
        if r in text:
            region = r
            break

    # 3) 영화관명 찾기 (예: 메가박스)
    if "메가박스" in text:
        cinema = "메가박스"

    # 4) 영화 제목 추출 (키워드, 지역, 영화관명 제거 후 남은 텍스트)
    keywords = [
        "위치", "어디", "주소", "장소", "상영시간", "몇시", "상영", "시간",
        "줄거리", "내용", "스토리", "감독", "장르", "평점", "개봉",
        "알려줘", "좀", "는", "이", "가", "을", "를", "에", "도", "은", "와", "과",
        "메가박스",
    ]
    # 지역명도 키워드 제거 대상에 포함
    if region:
        keywords.append(region)

    temp = text
    if cinema:
        temp = temp.replace(cinema, "")

    # 키워드 + 조사(은/는/이/가/을/를 등) 제거를 위해 정규식 패턴 작성
    # 예: (위치|어디|주소|...) + (은|는|이|가|을|를)? 같이 제거
    pattern = r"(" + "|".join(map(re.escape, keywords)) + r")(은|는|이|가|을|를|과|와)?"

    temp = re.sub(pattern, "", temp)
    temp = re.sub(r'\s+', ' ', temp).strip()

    movie_title = temp if temp else None

    print(f"[LOG] 파싱 결과 - 지역: {region}, 영화제목: {movie_title}, 의도: {intent}")
    return {
        "intent": intent,
        "region": region,
        "cinema": cinema,
        "movie_title": movie_title,
    }

@app.post("/qa")
def answer_question(req: QARequest):
    entities = parse_question(req.question)
    intent = entities['intent']
    region = entities['region']
    cinema = entities['cinema']
    movie_title = entities['movie_title']

    # 위치 질문 처리
    if intent == "cinema_location":
        target_region = region
        filtered_cinemas = megabox_data
        if target_region:
            filtered_cinemas = [c for c in megabox_data if target_region in [r.lower() for r in c.get("region", [])]]

        # 영화관 후보군
        choices = [c["cinema_name"] for c in filtered_cinemas]
        # 후보와 영화관명 fuzzy matching
        match_name = cinema if cinema else ""
        matched, score = process.extractOne(match_name, choices, scorer=fuzz.token_set_ratio)
        if score < 70 and len(match_name) < 1:
            # 영화관명 안 주어졌으면 지역 내 첫번째 영화관 정보 리턴
            if filtered_cinemas:
                cinema = filtered_cinemas[0]
                return {"answer": f"{cinema['cinema_name']} 위치는 {cinema['address']} 입니다."}
            else:
                return {"answer": "해당 지역에 영화관 정보가 없습니다."}
        elif score >= 70:
            cinema = next(c for c in filtered_cinemas if c["cinema_name"] == matched)
            return {"answer": f"{cinema['cinema_name']} 위치는 {cinema['address']} 입니다."}
        else:
            return {"answer": "해당 영화관을 찾을 수 없습니다."}

    # 상영시간 질문 처리
    elif intent == "showtime":
        if not movie_title:
            return {"answer": "상영시간을 알고 싶은 영화 제목을 알려주세요."}
        movie_title_norm = normalize(movie_title)

        # region과 영화관명 필터링
        filtered_cinemas = megabox_data
        if region:
            filtered_cinemas = [c for c in megabox_data if region in [r.lower() for r in c.get("region", [])]]
        if cinema:
            # 영화관명 fuzzy matching
            matched_cinema = None
            max_score = 0
            for c in filtered_cinemas:
                score = fuzz.token_set_ratio(normalize(cinema), normalize(c['cinema_name']))
                if score > max_score:
                    max_score = score
                    matched_cinema = c
            if matched_cinema and max_score >= 70:
                filtered_cinemas = [matched_cinema]
            else:
                return {"answer": "해당 영화관을 찾을 수 없습니다."}

        results = []
        results = []

        for c in filtered_cinemas:
            # 영화 제목 -> 버전 -> 상영시간 리스트 구조 생성
            movie_version_showtimes = defaultdict(lambda: defaultdict(list))

            for m in c.get("movies", []):
                title_norm = normalize(m["title"])
                if movie_title_norm == title_norm or movie_title_norm in title_norm:
                    version = m.get('version', '').strip()  # 버전, 없으면 빈 문자열
                    showtimes = m.get("showtimes", [])
                    movie_version_showtimes[m["title"]][version].extend(showtimes)

            for movie_title, versions in movie_version_showtimes.items():
                for version, times in versions.items():
                    times_sorted = ", ".join(sorted(set(times)))
                    version_str = f"({version}) " if version else ""
                    results.append(f"{c['cinema_name']} {version_str}{movie_title} 상영시간:<br>\n{times_sorted}<br>\n")

        if results:
            return {"answer": "\n".join(results)}
        else:
            return {"answer": "해당 영화 상영시간 정보를 찾을 수 없습니다."}

    # 영화 정보 질문 처리
    elif intent == "movie_info":
        if not movie_title:
            return {"answer": "영화 제목을 알려주세요."}
        movie = find_movie_exclude_animation(movie_title)
        if not movie:
            return {"answer": "영화를 찾을 수 없습니다."}

        simple_answer = simple_movie_answer(req.question, movie)
        if simple_answer is not None:
            return {"answer": simple_answer}

        # BERT QA 처리
        context = movie.get('overview', '')
        inputs = tokenizer.encode_plus(req.question, context, return_tensors="pt", truncation=True)
        outputs = model(**inputs)

        start_idx = torch.argmax(outputs.start_logits)
        end_idx = torch.argmax(outputs.end_logits) + 1

        if start_idx >= end_idx:
            return {"answer": "질문에 대한 적절한 답을 찾을 수 없습니다."}

        answer_ids = inputs['input_ids'][0][start_idx:end_idx]
        answer = tokenizer.decode(answer_ids, skip_special_tokens=True).strip()

        if len(answer) <= 1 or answer in ["[CLS]", "[SEP]"]:
            return {"answer": "질문에 대한 적절한 답을 찾을 수 없습니다."}

        return {"answer": answer}

    else:
        return {"answer": "무슨 질문인지 잘 모르겠습니다. 다시 질문해 주세요."}
