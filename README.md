# RabbitMQ & Ray Integration 작업 내역 및 보고서

본 저장소에서 진행된 주요 수정 사항 및 Ray 프레임워크 연동 개발 작업 내역을 정리한 문서입니다.

---

## 1. Consumer.py 에러 해결 내역

### 1.1 현상 및 에러 로그
`consumer.py` 실행 도중 다음과 같은 채널 종료 에러가 발생하였습니다.
```text
pika.exceptions.ChannelClosedByBroker: (406, 'PRECONDITION_FAILED - unknown delivery tag 1')
```

### 1.2 원인 분석
* **자동 수신 확인(auto_ack=True)**과 **수동 수신 확인(ch.basic_ack)**의 혼용으로 인해 발생했습니다.
* `basic_consume`에서 `auto_ack=True`로 설정되면 브로커가 메시지를 컨슈머로 보내는 순간 자동으로 ACK를 승인합니다. 
* 이 상태에서 콜백 함수가 수동으로 `ch.basic_ack`를 중복 호출하면, 이미 처리되었거나 존재하지 않는 `delivery_tag`를 확인하려고 시도하여 브로커가 에러를 발생시키고 채널을 강제 종료시킵니다.

### 1.3 조치 내역
[consumer.py](file:///d:/pyprj/testpy/consumer.py)에서 `auto_ack=True` 설정을 `auto_ack=False`로 변경하여, 콜백 내부의 수동 ACK 처리가 정상적으로 연동되도록 조치하였습니다.

```python
# consumer.py 수정 부분
channel.basic_consume(
    queue='hello',
    on_message_callback=callback,
    auto_ack=False  # True -> False 로 변경
)
```

---

## 2. Ray 프레임워크를 이용한 분산 Producer/Consumer 구성

Ray 프레임워크를 활용하여 **1개의 Producer Actor와 2개의 Consumer Actor**가 RabbitMQ 큐를 통해 메시지를 병렬로 송수신하는 분산 아키텍처를 새로 구성하였습니다.

### 2.1 주요 구현 파일
새로 생성된 구현 코드는 [ray_rabbitmq.py](file:///d:/pyprj/testpy/ray_rabbitmq.py)에서 확인하실 수 있습니다.

### 2.2 구현 방식
* **`RayConsumer` (Ray Actor)**:
  * 각 Consumer가 생성될 때 고유 ID(`consumer_id`)를 부여받습니다.
  * `prefetch_count=1` 및 `auto_ack=False` 설정을 사용하여 여러 컨슈머가 공정하게 메시지를 분배(Round-robin)받아 처리하며 수동 ACK를 반환합니다.
* **`RayProducer` (Ray Actor)**:
  * 지정된 개수만큼의 메시지를 RabbitMQ의 `hello` 큐로 순차적으로 발행합니다.
* **메인 제어 흐름**:
  * `ray.init()`으로 로컬 Ray 클러스터를 기동합니다.
  * `RayConsumer.remote(i)`로 2개의 컨슈머 Actor를 백그라운드에 구동합니다.
  * `RayProducer.remote()`를 생성하여 메시지를 큐에 적재합니다.
  * 모든 메시지가 퍼블리시되고 컨슈머들이 처리를 완료할 때까지 대기한 후 Ray를 안전하게 종료합니다.

---

## 3. 실시간 로깅 및 로그 파일 동시 기록 (신규 기능)

Ray 분산 환경에서 여러 액터(Actor)가 동일한 로그 파일에 동시에 쓰기를 수행하면 Windows 환경에서 파일 잠금(Locking) 문제 및 로그 꼬임 현상이 발생할 수 있습니다. 이를 안전하고 안정적으로 해결하기 위해 **중앙 집중형 로깅 액터 패턴**을 도입하였습니다.

### 3.1 구현 방식 (`LogActor`)
* **`LogActor` (Ray Actor)**:
  * 로그 파일(`ray_rabbitmq.log`) 쓰기를 단일 액터가 전담하도록 구현하여 프로세스/스레드 안전성(Process/Thread-safe)을 보장합니다.
  * 각 `RayConsumer` 및 `RayProducer` 액터는 로그 출력이 필요할 때 `logger.log.remote(message)`를 호출하여 비동기적으로 로그 출력을 위임합니다.
  * 수신된 로그는 화면 콘솔(stdout) 출력과 동시에 `ray_rabbitmq.log` 파일에 시간(timestamp) 정보와 함께 순차적으로 추가(append)됩니다.

### 3.2 로깅 코드 세부 구현
```python
@ray.remote
class LogActor:
    def __init__(self, log_filepath="ray_rabbitmq.log"):
        self.log_filepath = log_filepath
        self.file = open(self.log_filepath, "a", encoding="utf-8")

    def log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        print(formatted)
        self.file.write(formatted + "\n")
        self.file.flush()

    def close(self):
        self.file.close()
```

### 3.3 로깅 실행 결과 로그 파일 (`ray_rabbitmq.log`) 예시
실제 실행 후 로컬 디렉토리에 저장된 [ray_rabbitmq.log](file:///d:/pyprj/testpy/ray_rabbitmq.log) 파일의 로그 내역입니다.

```text
[2026-07-14 15:35:29] System initialized. Starting Actors...
[2026-07-14 15:35:29] [Consumer 1] Started consuming...
[2026-07-14 15:35:29] [Consumer 0] Started consuming...
[2026-07-14 15:35:31] [Consumer 0] Received: Message #0 from Ray Producer
[2026-07-14 15:35:31] [Producer] Starting to publish 10 messages...
[2026-07-14 15:35:31] [Producer] Sent: Message #0 from Ray Producer
[2026-07-14 15:35:31] [Producer] Sent: Message #1 from Ray Producer
[2026-07-14 15:35:31] [Consumer 1] Received: Message #1 from Ray Producer
[2026-07-14 15:35:32] [Producer] Sent: Message #2 from Ray Producer
[2026-07-14 15:35:32] [Producer] Sent: Message #3 from Ray Producer
[2026-07-14 15:35:33] [Consumer 0] Done processing.
[2026-07-14 15:35:33] [Consumer 0] Received: Message #2 from Ray Producer
[2026-07-14 15:35:33] [Producer] Sent: Message #4 from Ray Producer
[2026-07-14 15:35:33] [Consumer 1] Done processing.
[2026-07-14 15:35:33] [Consumer 1] Received: Message #3 from Ray Producer
[2026-07-14 15:35:33] [Producer] Sent: Message #5 from Ray Producer
[2026-07-14 15:35:34] [Producer] Sent: Message #6 from Ray Producer
[2026-07-14 15:35:34] [Producer] Sent: Message #7 from Ray Producer
[2026-07-14 15:35:35] [Consumer 0] Done processing.
[2026-07-14 15:35:35] [Consumer 0] Received: Message #4 from Ray Producer
[2026-07-14 15:35:35] [Producer] Sent: Message #8 from Ray Producer
[2026-07-14 15:35:35] [Consumer 1] Done processing.
[2026-07-14 15:35:35] [Consumer 1] Received: Message #5 from Ray Producer
[2026-07-14 15:35:35] [Producer] Sent: Message #9 from Ray Producer
[2026-07-14 15:35:36] [Producer] Finished publishing all messages.
[2026-07-14 15:35:36] Waiting for consumers to finish processing...
[2026-07-14 15:35:37] [Consumer 0] Done processing.
[2026-07-14 15:35:37] [Consumer 0] Received: Message #6 from Ray Producer
[2026-07-14 15:35:37] [Consumer 1] Done processing.
[2026-07-14 15:35:37] [Consumer 1] Received: Message #7 from Ray Producer
[2026-07-14 15:35:39] [Consumer 0] Done processing.
[2026-07-14 15:35:39] [Consumer 0] Received: Message #8 from Ray Producer
[2026-07-14 15:35:39] [Consumer 1] Done processing.
[2026-07-14 15:35:39] [Consumer 1] Received: Message #9 from Ray Producer
[2026-07-14 15:35:41] [Consumer 0] Done processing.
[2026-07-14 15:35:41] [Consumer 1] Done processing.
[2026-07-14 15:35:51] Shutting down Ray...
```
