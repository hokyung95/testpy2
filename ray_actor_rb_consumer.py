import json
import os
import time
import pika
import ray


def load_config(config_path="config.json"):
    """설정 파일(json)을 로드하는 함수. 파일이 없으면 기본 설정을 반환합니다."""
    default_config = {
        "rabbitmq": {
            "host": "localhost",
            "port": 5672,
            "queue_name": "hello",
            "username": "user1",
            "password": "user1",
            "vhost": "/"
        },
        "ray": {
            "address": "ray://192.168.225.130:10001",
            "namespace": "my_app",
            "actor_name": "rb_consumer_actor"
        }
    }

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                print(f"[*] Configuration loaded from '{config_path}'")
                return config
        except Exception as e:
            print(f"[!] Failed to load '{config_path}': {e}. Using default configuration.")
            return default_config
    else:
        print(f"[!] Config file '{config_path}' not found. Using default configuration.")
        return default_config


# 설정 로드
config = load_config("config.json")
rb_config = config.get("rabbitmq", {})
ray_config = config.get("ray", {})

# Ray Cluster 연결
ray.init(
    address=ray_config.get("address", "ray://192.168.225.130:10001"),
    namespace=ray_config.get("namespace", "my_app"),
    ignore_reinit_error=True
)


# detached 옵션으로 메인 프로세스가 꺼져도 유지되는 액터 생성
@ray.remote
class RabbitMQConsumerActor:
    def __init__(self, config=None):
        if config is None:
            config = {
                "host": "localhost",
                "port": 5672,
                "queue_name": "hello",
                "username": "user1",
                "password": "user1",
                "vhost": "/"
            }
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 5672)
        self.queue_name = config.get("queue_name", "hello")
        self.username = config.get("username", "user1")
        self.password = config.get("password", "user1")
        self.vhost = config.get("vhost", "/")

    def start_consuming(self):
        # 1. RabbitMQ 서버에 연결
        # 1. 인증 정보 설정 (사용자명, 비밀번호)
        credentials = pika.PlainCredentials(self.username, self.password)

        # 2. 연결 매개변수에 credentials 추가
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.vhost,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # 2. 큐 선언 (Producer와 동일한 이름)
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)

        # 3. 메시지 처리 콜백 함수 정의
        def callback(ch, method, properties, body):
            print(f" [x] Received {body.decode()}")

            # 여기서 메시지 처리 로직 수행 (예: DB 저장, 외부 API 호출 등)
            time.sleep(2)
            print(" [x] Done")

            # 4. 수동 ACK 전송
            ch.basic_ack(delivery_tag=method.delivery_tag)

        # 4. 큐에서 메시지를 가져오도록 설정
        channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=False
        )

        print(f" [*] Waiting for messages on {self.host}:{self.port} (queue: '{self.queue_name}'). To exit press CTRL+C")
        channel.start_consuming()


# Detached 액터 생성 및 비동기 수신 시작
actor_name = ray_config.get("actor_name", "rb_consumer_actor")
try:
    actor = ray.get_actor(actor_name)
    print(f"Found existing detached actor '{actor_name}'.")
except ValueError:
    actor = RabbitMQConsumerActor.options(
        name=actor_name,
        lifetime="detached"
    ).remote(config=rb_config)
    print(f"Created detached actor '{actor_name}'.")
    actor.start_consuming.remote()
