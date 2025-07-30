import json
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import BertTokenizerFast, BertForSequenceClassification, BertForTokenClassification
from torch.nn.functional import softmax
from difflib import get_close_matches

app = FastAPI()

# FastAPI
# 자연어 처리 전 사용자 입력을 안정적으로 검증, 비동기 처리 지원(사용자 많아도 지연X),
# FastAPI에서는 이걸 애플리케이션 시작 시 1번만 로딩하고, 이후 요청에선 메모리에 상주된 모델을 바로 사용
# 영화관 및 상영시간 데이터 로드
with open("data/all_cinema_with_showtimes.json", "r", encoding="utf-8") as f:
    cinema_data = json.load(f)

# BERT의 intent
intent_tokenizer = BertTokenizerFast.from_pretrained("model/intent_model")
intent_model = BertForSequenceClassification.from_pretrained("model/intent_model")
intent_model.eval()
# BERT의 ner
ner_tokenizer = BertTokenizerFast.from_pretrained("model/ner_model")
ner_model = BertForTokenClassification.from_pretrained("model/ner_model")
ner_model.eval()

intent_id2label = {
    0: "cinema_location",
    1: "showtime",
    2: "unknown"
}

ner_id2label = {
    0: "O",
    1: "B-REGION",
    2: "I-REGION",
    3: "B-CINEMA",
    4: "I-CINEMA",
    5: "B-MOVIE",
    6: "I-MOVIE"
}

class ChatRequest(BaseModel):
    question: str

# 조사 제거 함수
def clean_entity(entity: str) -> str:
    # 조사를 제거하여 지역명 정규화 전처리
    for josa in ["에서", "으로", "에게", "에게서", "한테", "로", "에", "도", "은", "는", "이", "가", "시"]:
        if entity.endswith(josa):
            return entity[: -len(josa)]
    return entity

# BERT 기반 NER 모델 토큰 추출 및 후처리
def extract_entities(entities):
    result = {"region": [], "cinema": [], "movie": []}
    current_entity = ""
    current_label = None

    for token, tag in entities:
        if tag.startswith("B-"):
            if current_label and current_entity:
                cleaned = clean_entity(current_entity)
                result[current_label].append(cleaned)
            current_label = tag[2:].lower()
            current_entity = token.replace("##", "")
        elif tag.startswith("I-") and current_label == tag[2:].lower():
            current_entity += token.replace("##", "")
        else:
            if current_label and current_entity:
                cleaned = clean_entity(current_entity)
                result[current_label].append(cleaned)
            current_label = None
            current_entity = ""

    if current_label and current_entity:
        cleaned = clean_entity(current_entity)
        result[current_label].append(cleaned)

    return result

# 텍스트 전처리 함수
def normalize_text(text):
    return text.replace(" ", "").lower()

# 유사한 영화를 찾는 함수
def find_similar_movie_name(user_input, movie_list):
    normalized_input = normalize_text(user_input)
    normalized_movies = {normalize_text(title): title for title in movie_list}
    matches = get_close_matches(normalized_input, normalized_movies.keys(), n=1, cutoff=0.6)
    if matches:
        return normalized_movies[matches[0]]
    return None

# 상영 시간 찾는 함수
def find_showtimes(regions, cinemas, movies, user_input):
    for c in cinema_data:
        if regions and not any(any(region in reg for reg in c.get("region", [])) for region in regions):
            continue
        if cinemas and not any(cinema in c.get("cinema_name", "") for cinema in cinemas):
            continue
        
        movie_titles = [m.get("title", "") for m in c.get("movies", [])]

        # 정확한 매칭이 되었을 경우
        for mv in c.get("movies", []):
            if any(movie in mv.get("title", "") for movie in movies):
                return c.get("region", [""])[0], c.get("cinema_name", ""), mv.get("title", ""), mv.get("showtimes", [])

        # 정확한 매칭이 안되었을 경우
        candidates = movies if movies else [user_input]
        for candidate in candidates:
            movie_name = find_similar_movie_name(candidate, movie_titles)
            if movie_name:
                for mv in c.get("movies", []):
                    if mv.get("title") == movie_name:
                        return c.get("region", [""])[0], c.get("cinema_name", ""), mv.get("title", ""), mv.get("showtimes", [])

    return None, None, None, []

def chatbot_response(text: str) -> str:
    print(f"\n[사용자 입력] {text}")

    # 의도 분류 intent
    inputs_intent = intent_tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs_intent = intent_model(**inputs_intent)
        probs = softmax(outputs_intent.logits, dim=1)
        intent_id = probs.argmax(dim=1).item()
        intent = intent_id2label[intent_id]
    print(f"[의도] {intent}")

    # 개체명 인식 ner = 입력 문장을 토큰화 → 모델 예측(추론) → 태깅 결과 추출
    tokens = ner_tokenizer.tokenize(text) # 토큰화하여 서브워드 단위로 나누기
    inputs_ner = ner_tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs_ner = ner_model(**inputs_ner)
        predictions = torch.argmax(outputs_ner.logits, dim=2)[0].tolist()

    entities = []
    for token, pred_id in zip(tokens, predictions[1:-1]):
        tag = ner_id2label.get(pred_id, "O")
        if tag != "O":
            entities.append((token, tag))

    print("[개체명]")
    for token, tag in entities:
        print(f"  {token} -> {tag}")

    extracted = extract_entities(entities)
    regions = extracted["region"]
    cinemas = extracted["cinema"]
    movies = extracted["movie"]

    # NER 개체값에 맞는 출력
    if intent == "showtime":
        if not movies:
            return "해당 영화관과 상영시간을 확인할 영화를 입력해주세요."

        region, cinema, movie, showtimes = find_showtimes(regions, cinemas, movies, text)
        if showtimes:
            return f"[{cinema}]에서 [{movie}] 상영시간은<br>{', '.join(showtimes)}입니다."
        else:
            return "죄송하지만 해당 상영시간 정보를 찾지 못했습니다.<br>정확한 영화관명과 영화제목을 다시 입력해주세요."

    elif intent == "cinema_location":
        if not cinemas or all(name == "영화관" for name in cinemas):
            cinemas_in_region = [
                c for c in cinema_data
                if any(any(region in reg for reg in c.get("region", [])) for region in regions)
            ]
            if cinemas_in_region:
                reply = f"{' / '.join(regions)} 지역의 영화관 목록입니다.<br><br>\n"
                for c in cinemas_in_region:
                    reply += f"[{c.get('cinema_name')}]<br>\n"
                    reply += f"{c.get('address')}<br><br>\n"
                return reply.strip()
            else:
                return f"{' / '.join(regions)} 지역에 영화관 정보가 없습니다."

        for c in cinema_data:
            if regions and not any(any(region in reg for reg in c.get("region", [])) for region in regions):
                continue
            if cinemas and not any(cinema in c.get("cinema_name", "") for cinema in cinemas):
                continue
            address = c.get("address", "")
            return f"{', '.join(regions)} {', '.join(cinemas)}의 주소는 {address}입니다."

    return "해당 영화관 정보를 찾지 못했습니다."

@app.post("/qa")
def ask(request: ChatRequest):
    answer = chatbot_response(request.question)
    return {"answer": answer}
