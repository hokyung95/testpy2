from dataclasses import dataclass, asdict

@dataclass
class Human:
    name: str
    age: int
    address: str
    job: str
    hobby: str

    def introduce(self):
        print(f"안녕하세요, {self.name}입니다! ({self.job}, {self.address} 거주)")
        print(self.to_dict())

    def to_dict(self) -> dict:
        return asdict(self)


# 사용 예시
if __name__ == "__main__":
    person = Human(
        name="김철수",
        age=25,
        address="경기도 성남시",
        job="데이터 분석가",
        hobby="독서"
    )

    print(person)  # 자동 생성된 __repr__ 출력
    person.introduce()
    person.name = "김영희"
    person.age = 30
    person.address = "경기도 수원시"
    person.job = "데이터 과학자"
    person.hobby = "등산"
    person.introduce()
    
    person2 = Human(
        name="김철수",
        age=25,
        address="경기도 성남시",
        job="데이터 분석가",
        hobby="독서"
    )

    print("person2.to_dict(): ({0})--{1}".format(person2,person2.job))
    person2.introduce()
