import ray

# ray.init(address="auto") # 또는 클러스터 주소
ray.init(address="ray://192.168.225.130:10001", namespace="my_app")

# detached 옵션으로 메인 프로세스가 꺼져도 유지되는 액터 생성
@ray.remote
class SharedActor:
    def ping(self):
        return "pong"


actor = SharedActor.options(name="my_shared_actor", lifetime="detached").remote()
print("Actor created:", ray.get(actor.ping.remote()))