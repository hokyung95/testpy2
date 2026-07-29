import ray
import time



@ray.remote(num_cpus=1)  # 필요 자원(CPU, GPU) 명시 가능
def process_data(x: int) -> int:
    time.sleep(1)  # 무거운 연산 가정
    return x * x

# ----------------------------------------------------
# Task 제출 및 병렬 실행
# ----------------------------------------------------

# 1. 원격 Ray Cluster에 연결 (Head Node IP 및 Port 지정)
ray.init(address="ray://192.168.225.130:10001")

# 로컬 단일 컴퓨터에서 테스트할 경우:
# ray.init() 

print(f"Cluster Resources: {ray.cluster_resources()}")

# 1. 비동기식으로 5개 Task 제출 (즉시 반환)
futures = [process_data.remote(i) for i in range(5)]

# 2. 결과 수집 (blocking)
results = ray.get(futures)
print(f"Task Results: {results}")  # [0, 1, 4, 9, 16]