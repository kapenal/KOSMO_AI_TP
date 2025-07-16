import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 추가
import numpy as np
import joblib
# from konlpy.tag import Okt

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "검색어 인자가 없습니다."}, ensure_ascii=False))
        sys.exit(1)

    input_title = sys.argv[1].strip()
    # print("Default JVM path:", jpype.getDefaultJVMPath())
    # 그냥 입력받은 검색어만 리턴
    result = {
        "input_title": input_title,
        "recommendations": []
    }

    print(json.dumps(result, ensure_ascii=False))