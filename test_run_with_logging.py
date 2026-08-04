import logging
import numpy as np


# def generate_data(num_rows: int = 1_000_000):
#     print(f"start generate_data...")
#     logging.info(f"[Generator] Data: {num_rows}")
#     for i in range(0, num_rows, 100_000):
#         logging.info(f"[Generator] Data: {i}")
#         yield {
#             "id": list(range(i, i + 100_000)),
#             "age": np.random.randint(18, 70, size=100_000).tolist(),
#             "income": np.random.randint(2000, 10000, size=100_000).astype(float).tolist(),
#             "category": np.random.choice(["A", "B", "C", "D"], size=100_000).tolist(),
#             "comment": np.random.choice(["  Hello World! ", "ERROR: fail", "SUCCESS :)", "  Test Data  "], size=100_000).tolist()
#         }
# logging 출력 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def generate_data(num_rows: int = 1_000_000):
    print(f"start generate_data...")
    logging.info(f"[Generator] Total Data Rows: {num_rows}")
    for i in range(0, num_rows, 100_000):
        logging.info(f"[Generator] Processing index: {i}")
        yield {
            "id": list(range(i, i + 100_000)),
            "age": np.random.randint(18, 70, size=100_000).tolist(),
            "income": np.random.randint(2000, 10000, size=100_000).astype(float).tolist(),
            "category": np.random.choice(["A", "B", "C", "D"], size=100_000).tolist(),
            "comment": np.random.choice(["  Hello World! ", "ERROR: fail", "SUCCESS :)", "  Test Data  "], size=100_000)
        }

# 제너레이터 데이터 순회(소비)
for batch in generate_data(1_000_000):
    print(f"Fetched batch size: {len(batch['id'])}")

for i in range(0, 10000, 1000):
    logging.info(f"[Generator] Processing index: {i}")    