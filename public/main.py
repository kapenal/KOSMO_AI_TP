# main.py
import sys
import json

# UTF-8 인코딩 설정
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "텍스트 인자가 필요합니다."}))
        sys.exit(1)
    
    search_text = sys.argv[1]  # Node.js에서 전달된 텍스트 인자

    # 검색 URL 생성 (구글 검색 예시)
    search_url = search_text

    # URL을 JSON 형태로 출력
    print(json.dumps({"search_url": search_url}, ensure_ascii=False))