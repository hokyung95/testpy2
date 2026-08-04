import json
from dataclasses import dataclass

# 1. dataclass 정의
@dataclass
class User:
    name: str
    age: int
    city: str

# 2. JSON 파일 읽어오기
file_path = "jsondata/users.json"

with open(file_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)  # JSON 배열이 파이썬의 list[dict] 형태로 변환됨

# 3. for문과 언패킹(**)을 사용해 dataclass 객체 리스트 생성
user_list = []
for item in json_data:
    # 딕셔너리 키와 dataclass 필드명이 일치하므로 **item으로 언패킹 가능
    user = User(**item)
    user_list.append(user)

# (참고) 리스트 컴프리헨션을 사용한다면 한 줄로도 가능합니다:
# user_list = [User(**item) for item in json_data]

# 4. 결과 확인
for user in user_list:
    print(f"이름: {user.name}, 나이: {user.age}, 도시: {user.city} (객체 타입: {type(user)})")