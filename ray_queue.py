import sys
import types

# Windows 환경에서 resource 모듈 및 getrlimit 우회 패치
if sys.platform == "win32":
    try:
        import resource
    except ImportError:
        resource = types.ModuleType("resource")
        sys.modules["resource"] = resource
    
    if not hasattr(resource, "getrlimit"):
        resource.RLIMIT_NOFILE = 7
        resource.getrlimit = lambda res: (8192, 8192)
        
        
import logging        
import time
import ray
from ray.util.queue import Queue

# Ray 클러스터 연결 (log_to_driver=False 로 원격 stdout 중복 스트리밍 차단 가능)
# ray.init(address="ray://192.168.225.130:10001")
# ray.init에 log_to_driver=False 전달
ray.init(address="ray://192.168.225.130:10001")


# 1. 공유 큐 생성
queue = Queue(maxsize=10)

logger = logging.getLogger(__name__)
# 2. 데이터를 생성하는 Producer 액터
@ray.remote
class Producer:
    def __init__(self, q: Queue):
        self.q = q

    def produce(self):
        for i in range(5):
            # print(f"[Producer] 데이터 전달: {i}")
            logger.info(f"[Producer] 데이터 전달: {i}")
            message = f"내 나이는 {i}살입니다."
            self.q.put(message)
            time.sleep(0.2)

# 3. 데이터를 소비하는 Consumer 액터
@ray.remote
class Consumer:
    def __init__(self, q: Queue):
        self.q = q

    def consume(self):
        received = []
        for _ in range(5):
            item = self.q.get()
            # print(f"[Consumer] 데이터 수신: {item}")
            logger.info(f"[Consumer] 데이터 수신: {item}")
            received.append(item)
        return received  # print 대신 결과를 return


# 4. 액터 인스턴스 생성 및 실행
producer = Producer.remote(queue)
consumer = Consumer.remote(queue)

producer_task = producer.produce.remote()

ray.get(producer_task)

# 메인 스크립트에서 받아서 1번만 출력
consumed_items = ray.get(consumer.consume.remote())
for item in consumed_items:
    print(f"[Consumer] 데이터 수신: {item}")

# consumer_task = consumer.consume.remote()

# # 작업 완료 대기
# ray.get([producer_task), consumer_task])