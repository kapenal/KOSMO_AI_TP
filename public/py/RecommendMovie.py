import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import os, re

# 1. 데이터 불러오기
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, '..', 'mj_data', 'review_dummy.txt')
review_dummy_df = pd.read_csv(file_path, sep='\t')
# print(" === 데이터 상위 5개 === \n", review_dummy_df.head())
# print(" === review_dummy_df.info() ===")
# review_dummy_df.info()
# print("\n === label 컬럼 확인 === \n", review_dummy_df['label'].value_counts())
# print("\n === label 유니크 값 === \n", review_dummy_df['label'].unique())
# print('review_dummy_df 데이터 확인')
# review_dummy_df


# 2. 잘못 들어간 행 제거
review_dummy_df = review_dummy_df[review_dummy_df['label'] != 'label']
# 3. label 컬럼을 숫자형으로 변환
review_dummy_df['label'] = review_dummy_df['label'].astype(int)

# 4. train / test 분리
train_df, test_df = train_test_split(
    review_dummy_df,
    test_size=0.2,
    random_state=42,
    stratify=review_dummy_df['label']
)
# print(f"Train 데이터 개수: {len(train_df)}")
# print(f"Test 데이터 개수: {len(test_df)}")

# 5. 저장
# train_df.to_csv('public/mj_data/train_data.txt', sep='\t', index=False, encoding='utf-8')
# test_df.to_csv('public/mj_data/test_data.txt', sep='\t', index=False, encoding='utf-8')


# 6. 학습 데이터 파일 로드
try:
    train_df = pd.read_csv('public/mj_data/train_data.txt', sep='\t')
    test_df = pd.read_csv('public/mj_data/train_data.txt', sep='\t')
except FileNotFoundError:
    print("Error: 'ratings_train.txt' or 'ratings_test.txt' not found.")
    print("Please download them from https://github.com/e9t/nsmc and place them in the same directory as this script.")
    exit()

# 7. 결측치 제거 (학습을 위해)
train_df = train_df.dropna(how='any')
test_df = test_df.dropna(how='any')

# 8. 텍스트 전처리 (정규표현식)
def clean_text(text):
    text = re.sub(r'[^가-힣\s]', '', text) 
    return text
train_df['document'] = train_df['document'].apply(clean_text)
test_df['document'] = test_df['document'].apply(clean_text)

# 9. 모델 학습/테스트를 위한 데이터셋 분리
X_train = train_df['document']
y_train = train_df['label']
X_test = test_df['document']
y_test = test_df['label']

# 10. 텍스트 벡터화 (TF-IDF)
# ngram_range=(1, 2): ‘스토리’, ‘스토리 좋다’ 같은 단어 묶음도 학습.
tfidf_vectorizer = TfidfVectorizer(min_df=3, ngram_range=(1, 2))

# 11. 어휘 학습
# 텍스트 → 숫자 벡터로 바꾸기 위한 단어 사전 생성
tfidf_vectorizer.fit(X_train)
# transform 적용 (어휘 학습 및 변환)
X_train_tfidf = tfidf_vectorizer.transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

# 12. 모델 학습 (로지스틱 회귀)
# 벡터화된 숫자 데이터를 이용해 긍정/부정 분류 모델 학습
model = LogisticRegression(random_state=42, solver='liblinear', C=1.0)
model.fit(X_train_tfidf, y_train)

# 13. 모델 평가
# 테스트 데이터셋으로 모델 성능을 평가합니다.
model_predict = model.predict(X_test_tfidf)

# 14. 정확도 계산 (실제 정답, 모델 예측 결과)
accuracy = accuracy_score(y_test, model_predict)
# print(f"모델 정확도 : {accuracy:.4f}")

# 15. 모델 평가 지표
# print("\n모델 평가 지표:")
# print(classification_report(y_test, model_predict,
#                             target_names=['긍정(Negative)(0)', '부정(Positive)(1)']))

# 16. 리뷰 긍/부정 감정 예측 함수
def predict_sentiment_fc(new_review):
    # 입력 텍스트 전처리
    cleaned_review = clean_text(new_review)
    # 텍스트를 벡터화
    new_review_tfidf = tfidf_vectorizer.transform([cleaned_review])
    # 모델로 예측
    prediction = model.predict(new_review_tfidf)[0]
    # 긍/부정일 확률 각각 계산
    prediction_proba = model.predict_proba(new_review_tfidf)[0]
    sentiment = "Positive" if prediction == 1 else "Negative"

    # print(f"\n--- 예측 결과 ---")
    # print(f"리뷰: '{new_review}'")
    # print(f"리뷰 반응: {sentiment}")
    # print(f"긍정 확률: {prediction_proba[1]:.4f}, 부정 확률: {prediction_proba[0]:.4f}")
    
    return sentiment, prediction_proba



# 파일 호출 시 작동
import sys, json

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "리뷰를 인자로 넣어주세요."}, ensure_ascii=False))
        sys.exit(1)

    input_review = sys.argv[1]
    sentiment, proba = predict_sentiment_fc(input_review)

    # JSON 결과만 stdout에 출력
    result = {
        "label": sentiment,
        "positive": round(float(proba[1]), 4),
        "negative": round(float(proba[0]), 4)
    }
    print(json.dumps(result, ensure_ascii=False))

# # ------------------------------------------------------------------------------------------------------------------
# # test


# test 1
# review1 = "이 영화 정말 최고였어요! 배우들 연기도 좋고 스토리도 완벽합니다."
# predict_sentiment_fc(review1)
# review2 = "시간 낭비였어요. 지루하고 개연성도 없네요. 추천하지 않습니다."
# predict_sentiment_fc(review2)
# review3 = "그럭저럭 볼만했습니다. 기대했던 것보다는 아니지만 나쁘지 않았어요."
# predict_sentiment_fc(review3)

# test 2
# # 리뷰 데이터 불러오기
# reviews_df = pd.read_csv('public/mj_data/TrendRankReviews.csv')
# # 리뷰 데이터에 감정 라벨링
# sentiments = []
# for review in reviews_df['review']:
#     sentiment, Probability = predict_sentiment_fc(review)
#     sentiments.append(sentiment)
# # 새 컬럼으로 추가
# reviews_df['sentiment'] = sentiments
# # 새 파일로 저장
# reviews_df.to_csv('public/mj_data/fi_reviews.csv', index=False, encoding='utf-8')

# test 3
# 리뷰를 입력 받아 결과 출력
# review_text = input("리뷰 입력 \n")
# # 입력한 리뷰를 모델에 넣어 예측
# sentiment, proba = predict_sentiment_fc(review_text)
# # 예측 결과 출력
# print(f"예측 결과: {sentiment}")

# if sentiment == "부정(Negative)":
#     print("만족스럽지 않은 콘텐츠였나봐요. 더 좋은 콘텐츠를 추천해드릴게요!")
# else :
#     print("마음에 꼭 드셨군요!")
