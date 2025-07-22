import requests
from bs4 import BeautifulSoup
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def crawl_movies_requests(max_results=6):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    url = "https://search.naver.com/search.naver?query=현재상영영화"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # 네이버 '현재상영영화' 결과 내에서 영화 데이터 div.data_area (원본 셀렉터 참고)
    movies = soup.select("div.data_area")[:max_results]

    results = []
    for movie in movies:
        title_tag = movie.select_one("div.title a.this_text")
        title = title_tag.text.strip() if title_tag else ""

        img_tag = movie.select_one("a.img_box img")
        poster = img_tag["src"] if img_tag and img_tag.has_attr("src") else "이미지 없음"

        overview_tag = movie.select_one("dl.info_group dd")
        overview = overview_tag.text.strip() if overview_tag else "개요 없음"

        rating_tag = movie.select_one("dl.info_group.type_visible dd span.num")
        rating = rating_tag.text.strip() if rating_tag else "별점 없음"

        results.append({
            "제목": title,
            "별점": rating,
            "개요": overview,
            "포스터": poster
        })

    return results

if __name__ == "__main__":
    data = crawl_movies_requests()
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"message": "❌ 현재 상영작을 가져올 수 없습니다."}, ensure_ascii=False))

# 2025_07_22 수정 전
# import sys
# import io
# import json
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import NoSuchElementException
# from bs4 import BeautifulSoup
# import time
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# # 현재상영영화 페이지를 크롤링하는 함수 정의
# def crawl_movies_fixed_scroll(max_pages=8, scroll_position=800, max_results=6):
#     options = Options()
#     options.add_argument('--headless')
#     options.add_argument('--disable-gpu')
#     options.add_argument('window-size=1920x1080')
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_argument("user-agent=Mozilla/5.0")

#     driver = webdriver.Chrome(options=options)
#     url = "https://search.naver.com/search.naver?query=현재상영영화"
#     driver.get(url)
#     time.sleep(2)

#     results = []
#     page = 1
#     # keyword = keyword.lower()  # 원본 : 키워드 소문자 변환 (필터용)
#     # 변경 : keyword 필터를 제거하여 모든 현재 상영작을 가져오기 위해 주석 처리

#     while page <= max_pages:
#         driver.execute_script(f"window.scrollTo(0, {scroll_position});")
#         time.sleep(1)

#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         movies = soup.select("div.data_area")

#         for movie in movies:
#             title_tag = movie.select_one("div.title a.this_text")
#             title = title_tag.text.strip() if title_tag else ""

#             img_tag = movie.select_one("a.img_box img")
#             poster = img_tag["src"] if img_tag and img_tag.has_attr("src") else "이미지 없음"

#             overview_tag = movie.select_one("dl.info_group dd")
#             overview = overview_tag.text.strip() if overview_tag else "개요 없음"

#             rating_tag = movie.select_one("dl.info_group.type_visible dd span.num")
#             rating = rating_tag.text.strip() if rating_tag else "별점 없음"

#             # 원본 코드 : 키워드 포함 여부 검사하여 필터링
#             # title_lower = title.lower()
#             # overview_lower = overview.lower()
#             # overview_parts = [part.strip() for part in overview_lower.split('/')]
#             # if keyword in title_lower or any(keyword in part for part in overview_parts):
#             #     results.append({...})
#             #     if len(results) >= max_results:
#             #         driver.quit()
#             #         return results

#             # 변경 : 필터 제거, 그냥 모든 영화 추가
#             results.append({
#                 "제목": title,
#                 "별점": rating,
#                 "개요": overview,
#                 "포스터": poster
#             })
#             if len(results) >= max_results:
#                 driver.quit()
#                 return results

#         try:
#             next_btn = driver.find_element(By.CSS_SELECTOR, "a.pg_next")
#             if next_btn.get_attribute("aria-disabled") == "true":
#                 break
#             next_btn.click()
#             page += 1
#             time.sleep(2)
#         except NoSuchElementException:
#             break

#     driver.quit()
#     return results


# if __name__ == "__main__":
#     # 원본 : 입력 인자 받음
#     # if len(sys.argv) < 2:
#     #     print(json.dumps({"error": "검색어 인자가 없습니다."}, ensure_ascii=False))
#     #     sys.exit(1)

#     # input_title = sys.argv[1]
#     # keyword = input_title.strip().lower()

#     # 변경 : 입력 키워드 무시, 그냥 현재 상영작 전체를 가져오기 때문에
#     # 아래처럼 바로 함수 호출
#     data = crawl_movies_fixed_scroll()

#     if data:
#         print(json.dumps(data, ensure_ascii=False, indent=2))
#     else:
#         print(json.dumps({"message": "❌ 현재 상영작을 가져올 수 없습니다."}, ensure_ascii=False))







# 2025_07_18 수정 전
# def crawl_movies_fixed_scroll(keyword, max_pages=8, scroll_position=800, max_results=5):
#     options = Options()  # Chrome 옵션 설정 객체 생성
#     options.add_argument('--headless')  # 브라우저 창을 띄우지 않도록 설정 (백그라운드 실행)
#     options.add_argument('--disable-gpu')  # GPU 사용 안함 (headless 모드에서 필수는 아님)
#     options.add_argument('window-size=1920x1080')  # 브라우저 창 크기 설정
#     options.add_argument('--disable-blink-features=AutomationControlled')  # 자동화 감지 방지
#     options.add_argument("user-agent=Mozilla/5.0")  # User-Agent 설정 (봇으로 오인 방지)

#     driver = webdriver.Chrome(options=options)  # 위 옵션으로 크롬 드라이버 실행
#     url = "https://search.naver.com/search.naver?query=현재상영영화"  # 검색할 URL
#     driver.get(url)  # 해당 URL로 이동
#     time.sleep(2)  # 페이지 로딩 대기

#     results = []  # 수집한 영화 정보를 저장할 리스트
#     page = 1  # 시작 페이지 번호
#     keyword = keyword.lower()  # 입력한 키워드를 소문자로 변환 (대소문자 무시)

#     while page <= max_pages:  # 최대 페이지 수만큼 반복
#         # driver.execute_script를 통해 지정 위치로 스크롤 이동
#         driver.execute_script(f"window.scrollTo(0, {scroll_position});")
#         time.sleep(1)  # 스크롤 후 약간 대기 (렌더링 시간)

#         soup = BeautifulSoup(driver.page_source, "html.parser")  # 현재 페이지의 HTML을 파싱
#         movies = soup.select("div.data_area")  # 영화 데이터가 있는 블록들을 모두 선택

#         for movie in movies:  # 각 영화에 대해 반복
#             title_tag = movie.select_one("div.title a.this_text")  # 영화 제목 태그 선택
#             title = title_tag.text.strip() if title_tag else ""  # 텍스트 추출 (없으면 빈 문자열)

#             img_tag = movie.select_one("a.img_box img")  # 포스터 이미지 태그 선택
#             poster = img_tag["src"] if img_tag and img_tag.has_attr("src") else "이미지 없음"  # 포스터 URL 추출

#             overview_tag = movie.select_one("dl.info_group dd")  # 개요 정보 추출
#             overview = overview_tag.text.strip() if overview_tag else "개요 없음"  # 개요 텍스트 추출

#             rating_tag = movie.select_one("dl.info_group.type_visible dd span.num")  # 별점 태그 선택
#             rating = rating_tag.text.strip() if rating_tag else "별점 없음"  # 별점 텍스트 추출

#             title_lower = title.lower()  # 제목을 소문자로 변환
#             overview_lower = overview.lower()  # 개요도 소문자로 변환

#             overview_parts = [part.strip() for part in overview_lower.split('/')]  # 개요를 "/"로 나누고 공백 제거

#             # 제목 또는 개요 중 하나라도 키워드 포함 시 저장
#             if keyword in title_lower or any(keyword in part for part in overview_parts):

#                 results.append({
#                     "제목": title,
#                     "별점": rating,
#                     "개요": overview,
#                     "포스터": poster
#                 })

#                 if len(results) >= max_results:
#                     driver.quit()  # ✅ 드라이버를 여기서 미리 종료
#                     return results  # ✅ 함수 자체를 바로 종료

#         if len(results) >= max_results:  # ✅ 루프 종료 조건 추가
#             break

#         # 다음 페이지 이동 시도
#         try:
#             next_btn = driver.find_element(By.CSS_SELECTOR, "a.pg_next")  # 다음 버튼 찾기
#             if next_btn.get_attribute("aria-disabled") == "true":  # 더 이상 페이지가 없으면 종료
#                 break
#             next_btn.click()  # 다음 버튼 클릭
#             page += 1  # 페이지 번호 증가
#             time.sleep(2)  # 페이지 로딩 대기
#         except NoSuchElementException:  # 다음 버튼이 없는 경우
#             break

#     driver.quit()  # 드라이버 종료 (브라우저 닫기)
#     return results  # 결과 리스트 반환

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print(json.dumps({"error": "검색어 인자가 없습니다."}, ensure_ascii=False))
#         sys.exit(1)

#     input_title = sys.argv[1]
#     # keyword = input_title.strip().lower()  # 사용자에게 키워드 입력 받기
#     keyword = " "
#     # ✅ 공백만 입력한 경우 차단
#     if not keyword:
#         print(json.dumps({"message": "❌ 공백만으로는 검색할 수 없습니다."}, ensure_ascii=False))
#         sys.exit(0)

#     data = crawl_movies_fixed_scroll(keyword)  # 함수 호출하여 영화 데이터 수집

#     # if data:  # 결과가 있다면 출력
#     #     for movie in data:
#     #         print("\n🎬 제목:", movie["제목"])
#     #         print("⭐️ 별점:", movie["별점"])
#     #         print("📝 개요:", movie["개요"])
#     #         print("🖼 포스터:", movie["포스터"])
#     # else:
#     #     print("❌ 해당 키워드의 영화가 없습니다.")  # 결과가 없을 때 메시지 출력

#     if data:  # 결과가 있다면 JSON으로 반환
#         result = []
#         for movie in data:
#             result.append({
#                 "제목": movie["제목"],
#                 "별점": movie["별점"],
#                 "개요": movie["개요"],
#                 "포스터": movie["포스터"]
#             })
#         json_result = json.dumps(result, ensure_ascii=False, indent=2)
#         print(json_result)
#     else:
#         print(json.dumps({"message": "❌ 해당 키워드의 영화가 없습니다."}, ensure_ascii=False))
