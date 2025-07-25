import json
import torch
from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import BertTokenizerFast, BertForSequenceClassification, BertForTokenClassification
from torch.nn.functional import softmax

app = FastAPI()

# --- 데이터 & 모델 로드 ---
with open("data/megabox_cinema_with_showtimes.json", "r", encoding="utf-8") as f:
    cinema_data = json.load(f)

intent_tokenizer = BertTokenizerFast.from_pretrained("model/intent_model")
intent_model = BertForSequenceClassification.from_pretrained("model/intent_model")
intent_model.eval()

ner_tokenizer = BertTokenizerFast.from_pretrained("model/ner_model")
ner_model = BertForTokenClassification.from_pretrained("model/ner_model")
ner_model.eval()

intent_id2label = {
    0: "cinema_location",
    1: "showtime",
    2: "movie_info",   # 제거된 의도 (사용 안함)
    3: "unknown"
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

# --- 요청 형식 ---
class ChatRequest(BaseModel):
    question: str

# --- 엔티티 추출 함수 ---
def extract_entities(entities):
    result = {"region": "", "cinema": "", "movie": ""}
    current = {"region": "", "cinema": "", "movie": ""}
    current_label = None

    for token, tag in entities:
        if tag.startswith("B-"):
            current_label = tag[2:].lower()
            current[current_label] = token.replace("##", "")
        elif tag.startswith("I-") and current_label == tag[2:].lower():
            current[current_label] += token.replace("##", "")
        else:
            current_label = None
    result.update(current)
    return result

# --- 상영시간 찾기 함수 ---
def find_showtimes(region, cinema, movie):
    for c in cinema_data:
        if region and region not in c.get("region", []):
            continue
        if cinema and cinema not in c.get("cinema_name", ""):
            continue
        if movie:
            for mv in c.get("movies", []):
                if movie in mv.get("title", ""):
                    return mv.get("showtimes", [])
    return []

# --- 챗봇 응답 처리 함수 ---
def chatbot_response(text: str) -> str:
    print(f"\n[사용자 입력] {text}")

    # Intent 추론
    inputs_intent = intent_tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs_intent = intent_model(**inputs_intent)
        probs = softmax(outputs_intent.logits, dim=1)
        intent_id = probs.argmax(dim=1).item()
        intent = intent_id2label[intent_id]
    print(f"[의도] {intent}")

    # NER 추론
    tokens = ner_tokenizer.tokenize(text)
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
    region = extracted["region"]
    cinema = extracted["cinema"]
    movie = extracted["movie"]

    # 의도별 응답
    if intent == "showtime":
        showtimes = find_showtimes(region, cinema, movie)
        if showtimes:
            times = ", ".join(showtimes)
            return f"{region} {cinema}에서 {movie} 상영시간은 {times}입니다."
        else:
            return "죄송하지만 해당 상영시간 정보를 찾지 못했습니다."

    elif intent == "cinema_location":
        for c in cinema_data:
            if region and region not in c.get("region", []):
                continue
            if cinema and cinema not in c.get("cinema_name", ""):
                continue
            address = c.get("address", "")
            return f"{region} {cinema}의 주소는 {address}입니다."
        return "해당 영화관 정보를 찾지 못했습니다."

    else:
        return "죄송합니다. 영화관 위치나 상영시간에 대한 질문만 처리할 수 있어요."

# --- FastAPI 라우팅 ---
@app.post("/qa")
def ask(request: ChatRequest):
    answer = chatbot_response(request.question)
    return {"answer": answer}