import logging
import random
from dataclasses import dataclass, asdict

# logging 출력 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class Human:
    name: str
    age: int
    address: str
    job: str
    hobby: str

    def introduce(self):
        print(f"안녕하세요, {self.name}입니다! (나이: {self.age}, 직업: {self.job}, 주소: {self.address}, 취미: {self.hobby})")

    def to_dict(self) -> dict:
        return asdict(self)


# 무작위 데이터 생성을 위한 데이터 후보
NAMES = ["김철수", "이영희", "박민수", "정수진", "최동현", "강지은", "윤서준", "한지민", "임현우", "송유진"]
ADDRESSES = ["서울시 강남구", "경기도 성남시", "부산시 해운대구", "인천시 연수구", "대구시 수성구", "대전시 유성구", "광주시 서구"]
JOBS = ["소프트웨어 엔지니어", "데이터 분석가", "디자이너", "기획자", "교사", "의사", "연구원", "마케터"]
HOBBIES = ["독서", "등산", "게임", "영화 감상", "요리", "수영", "자전거 타기", "사진 촬영"]


def generate_random_humans(count: int = 100):
    """각 필드값을 random하게 생성하여 Human 객체 count개를 순차적으로 반환하는 제너레이터 함수"""
    logging.info(f"[Generator] Starting generation of {count} Human objects...")
    for i in range(count):
        human = Human(
            name=random.choice(NAMES),
            age=random.randint(20, 65),
            address=random.choice(ADDRESSES),
            job=random.choice(JOBS),
            hobby=random.choice(HOBBIES)
        )
        yield human


# 100개의 Human 객체 생성 및 테스트 실행
if __name__ == "__main__":
    humans = []
    
    for i, human in enumerate(generate_random_humans(100), start=1):
        humans.append(human)
        logging.info(f"[Human #{i:03d}] {human}")

    print(f"\n총 {len(humans)}개의 Human 객체 생성이 완료되었습니다.")
    print("생성된 첫 번째 객체 샘플:", humans[0].to_dict())