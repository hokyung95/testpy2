# pyrefly: ignore [missing-import]
import ray

# ray.init(address="auto")
ray.init(address="ray://192.168.225.130:10001", namespace="my_app")

# 1. 이름으로 액터 핸들 가져오기 (동일한 namespace)
actor_handle = ray.get_actor("my_shared_actor")

# 2. 액터 종료
ray.kill(actor_handle)
print("my_shared_actor killed successfully!")