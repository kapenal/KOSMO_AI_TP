import sys
import json
import numpy as np
import joblib
from soynlp.tokenizer import LTokenizer
import io, os

# 콘솔 출력 인코딩 설정 (한글 깨짐 방지)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 현재 파일 위치 기준 모델 데이터 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.normpath(os.path.join(BASE_DIR, '..', '..', 'model'))

# 모델 및 데이터 불러오기
model = joblib.load(os.path.join(PATH, "word2vec_movie.model"))
movie_vectors = joblib.load(os.path.join(PATH, "movie_vectors.pkl"))
movies = joblib.load(os.path.join(PATH, "movies.pkl"))
title_tokens = joblib.load(os.path.join(PATH, "title_tokens.pkl"))
raw_word_scores = joblib.load(os.path.join(PATH, "soynlp_word_scores.pkl"))

# soynlp tokenizer 초기화
word_scores = {w: s.cohesion_forward for w, s in raw_word_scores.items()}
tokenizer = LTokenizer(scores=word_scores)

# 제목 토큰화 함수
def tokenize_title(text):
    if not text:
        return []
    text = text.strip().replace(" ", "")
    return tokenizer.tokenize(text)

# 자카드 유사도 함수
def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

# 가장 유사한 영화 제목 인덱스 찾기
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

# 영화 추천 함수
def recommend_movie(input_title, movies, movie_vectors, title_tokens, top_n=5):
    matched_idx = find_similar_movie(input_title, title_tokens)

    if matched_idx == -1:
        input_vec = np.mean(movie_vectors, axis=0)
        input_genres = set()
        input_overview_vec = input_vec
    else:
        input_vec = movie_vectors[matched_idx]
        input_genres = set(movies[matched_idx].get("genres", []))
        input_overview_vec = input_vec

    input_norm = np.linalg.norm(input_vec)
    vectors_norm = np.linalg.norm(movie_vectors, axis=1)
    dot_products = movie_vectors @ input_vec

    with np.errstate(divide='ignore', invalid='ignore'):
        cosine_similarities = dot_products / (vectors_norm * input_norm)
        cosine_similarities = np.nan_to_num(cosine_similarities)

    if matched_idx >= 0:
        cosine_similarities[matched_idx] = -1

    adjusted_similarities = cosine_similarities.copy()
    for idx, m in enumerate(movies):
        if "애니메이션" in m.get("genres", []):
            adjusted_similarities[idx] *= 0.7

    top_indices = np.argpartition(-adjusted_similarities, top_n)[:top_n]
    top_indices = top_indices[np.argsort(-adjusted_similarities[top_indices])]

    recommendations = []
    for i in top_indices:
        m = movies[i]
        rec_genres = set(m.get("genres", []))
        genre_overlap = jaccard_similarity(input_genres, rec_genres)

        rec_vec = movie_vectors[i]
        overview_similarity = float(np.dot(input_overview_vec, rec_vec) /
                                    (np.linalg.norm(input_overview_vec) * np.linalg.norm(rec_vec)))

        recommendations.append({
            "movie_id": m.get("movie_id", ""),
            "title_ko": m.get('title_ko', ''),
            "genres": m.get("genres", []),
            "release_date": m.get('release_date', ''),
            "vote_average": m.get('vote_average', 0),
            "poster_path": m.get('poster_path', ''),
            "similarity": round(float(adjusted_similarities[i]), 4),
            "genre_overlap": round(genre_overlap, 4)
        })

    return recommendations

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "영화 제목을 입력하세요. 예: python movie_recommender.py 해운대"}, ensure_ascii=False))
        sys.exit(1)

    input_title = " ".join(sys.argv[1:])
    recs = recommend_movie(input_title, movies, movie_vectors, title_tokens, top_n=5)

    result = {
        "input_title": input_title,
        "recommendations": recs
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
