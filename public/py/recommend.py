import sys
import json
import numpy as np
import joblib
import numpy as np
from soynlp.tokenizer import LTokenizer
import io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# # 파일 로드 경로 설정
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PATH = os.path.join(BASE_DIR, "..", "model")
# 현재 recommend.py 파일 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# public/py → public → TeamProject → model 로 올라감
PATH = os.path.normpath(os.path.join(BASE_DIR, '..', '..', 'model'))



# 모델 및 토큰 로드
model = joblib.load(os.path.join(PATH, "word2vec_movie.model"))        # 학습된 Word2Vec 모델
# movie_vectors = np.array(os.path.join(joblib.load(PATH, "movie_vectors.pkl")))  # 영화별 벡터 (줄거리+장르 기반)
movie_vectors = joblib.load(os.path.join(PATH, "movie_vectors.pkl"))
movies = joblib.load(os.path.join(PATH, "movies.pkl"))                 # 영화 정보 리스트 (제목, 줄거리, 장르 등)
title_tokens = joblib.load(os.path.join(PATH, "title_tokens.pkl"))     # 영화 제목을 토큰화한 리스트 (검색용)

# 제목 검색용 토큰나이저
tokenizer = LTokenizer()

# 제목 문자열 토큰화(공백 기준)
def tokenize_title(text):
    if not text:
        return []
    text = text.strip().replace(" ", "")  # ← 공백 제거
    return tokenizer.tokenize(text)

# 자카드 유사도 계산
def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

# 입력한 제목과 가장 유사한 제목의 영화를 반환 함수 / 유사도는 자카드 유사도 기반, 유사도가 threshold 미만이면 -1 반환
def find_similar_movie(input_title, title_tokens, threshold=0.1):
    input_tokens = set(tokenize_title(input_title))
    best_match_idx = -1
    best_score = 0.0
    for idx, tokens in enumerate(title_tokens):
        score = jaccard_similarity(input_tokens, set(tokens))
        if score > best_score and score >= threshold:
            best_score = score
            best_match_idx = idx
    return best_match_idx

# 입력한 제목과 유사한 영화 1개를 찾은 후,
# 그 영화의 벡터(장르+줄거리)를 기준으로 가장 유사한 영화 top_n개를 추천
def recommend_movie(input_title, movies, movie_vectors, title_tokens, top_n=5):
    
    matched_idx = find_similar_movie(input_title, title_tokens)

    # 유사한 제목을 찾지 못했을 경우: 모든 영화 벡터의 평균을 사용
    if matched_idx == -1:
        # print(f"'{input_title}'과(와) 비슷한 영화를 찾지 못했습니다. 전체 평균 벡터로 추천합니다.")
        input_vec = np.mean(movie_vectors, axis=0)
    else:
        # print(f"입력하신 '{input_title}'과(와) 가장 비슷한 영화는 '{movies[matched_idx]['title_ko']}'입니다.")
        input_vec = movie_vectors[matched_idx]

    # --- 코사인 유사도 계산 ---
    input_norm = np.linalg.norm(input_vec)
    vectors_norm = np.linalg.norm(movie_vectors, axis=1)
    dot_products = movie_vectors @ input_vec  # 내적

    with np.errstate(divide='ignore', invalid='ignore'):
        cosine_similarities = dot_products / (vectors_norm * input_norm)  # 유사도 계산
        cosine_similarities = np.nan_to_num(cosine_similarities)  # NaN 방지

    # 자기 자신은 제외 (중복 추천 방지)
    if matched_idx >= 0:
        cosine_similarities[matched_idx] = -1

    # 상위 top_n 유사한 영화 인덱스 선택
    top_indices = np.argpartition(-cosine_similarities, top_n)[:top_n]
    top_indices = top_indices[np.argsort(-cosine_similarities[top_indices])]  # 유사도 내림차순 정렬

    # 추천 영화 정보 구성
    recommendations = []
    for i in top_indices:
        m = movies[i]
        recommendations.append({
            "title_ko": m.get('title_ko', ''),
            "release_date": m.get('release_date', ''),
            "vote_average": m.get('vote_average', 0),
            "poster_path": m.get('poster_path', ''),
            "similarity": cosine_similarities[i]
        })

    return recommendations


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "검색어 인자가 없습니다."}, ensure_ascii=False))
        sys.exit(1)

    # 예시: 사용자 입력 영화 제목
    input_title = sys.argv[1]  # ← 원하는 제목으로 변경 가능

    # 추천 실행
    recs = recommend_movie(input_title, movies, movie_vectors, title_tokens, top_n=5)

    result = {
    "input_title": input_title,
    "recommendations": []
}

    for rec in recs:
        # rec는 recommend_movie 함수에서 가져온 영화 정보 딕셔너리임
        # 원본 movies에서 movie_id, genres 등 추가 정보 가져오려면 movies 리스트에서 찾아야 함

        # 영화 고유 ID와 장르를 movies 리스트에서 찾아서 가져오기
        movie_info = next((m for m in movies if m.get('title_ko') == rec.get('title_ko')), {})

        result["recommendations"].append({
            "movie_id": movie_info.get("movie_id", ""),
            "title_ko": rec.get("title_ko", ""),
            "genres": movie_info.get("genres", []),
            "release_date": rec.get("release_date", ""),
            "vote_average": rec.get("vote_average", 0),
            "poster_path": rec.get("poster_path", "")
    })

    print(json.dumps(result, ensure_ascii=False))