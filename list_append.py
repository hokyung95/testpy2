from dataclasses import dataclass

@dataclass
class Book:
    title: str
    author: str
    price: int

# 딕셔너리 형태의 데이터 리스트
book_data = [
    {"title": "파이썬 완벽 가이드", "author": "홍길동", "price": 30000},
    {"title": "데이터 분석 입문", "author": "김파이", "price": 25000},
]

# 언패킹을 활용한 객체 생성 및 리스트 추가
book_list = []
for data in book_data:
    book = Book(data["title"], data["author"], data["price"])  # 딕셔너리의 키가 dataclass 필드명과 일치할 때 사용 가능
    book_list.append(book)

# 결과 확인
for b in book_list:
    print(b)