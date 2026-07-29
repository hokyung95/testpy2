import sys
import types

# Windows 환경 resource 모듈 패치
if sys.platform == "win32":
    try:
        import resource
    except ImportError:
        resource = types.ModuleType("resource")
        sys.modules["resource"] = resource
    if not hasattr(resource, "getrlimit"):
        resource.RLIMIT_NOFILE = 7
        resource.getrlimit = lambda res: (8192, 8192)

import ray

# 1. 원격 Ray 클러스터에 연결
ray.init(address="ray://192.168.225.130:10001")

# 2. 클러스터 내부 노드에서 State API를 실행하는 원격 함수 정의 (State 필터 파라미터 추가)
@ray.remote
def get_cluster_actors(state: str = None):
    # pyrefly: ignore [missing-import]
    from ray.util.state import list_actors
    
    if state:
        state_upper = state.upper()
        try:
            # Ray State API의 filters 파라미터 활용
            return list_actors(filters=[("state", "=", state_upper)])
        except Exception:
            # filters 실패 시 파이썬 단에서 상태 필터링 처리 (Fallback)
            all_actors = list_actors()
            return [
                a for a in all_actors
                if (a.get("state") if isinstance(a, dict) else getattr(a, "state", "")).upper() == state_upper
            ]
    return list_actors()


def print_actors(actors, title="액터 목록"):
    print(f"\n=== {title} ===")
    if not actors:
        print("조건에 해당하는 액터가 없습니다.")
        return
    for idx, actor in enumerate(actors, 1):
        actor_id = actor.get("actor_id") if isinstance(actor, dict) else getattr(actor, "actor_id", "N/A")
        name = (actor.get("name") if isinstance(actor, dict) else getattr(actor, "name", None)) or "<무명 액터>"
        st = actor.get("state") if isinstance(actor, dict) else getattr(actor, "state", "UNKNOWN")
        class_name = actor.get("class_name") if isinstance(actor, dict) else getattr(actor, "class_name", "N/A")
        namespace = actor.get("ray_namespace") if isinstance(actor, dict) else getattr(actor, "ray_namespace", "N/A")

        print(f"{idx}. Name: {name:<20} | State: {st:<10} | Class: {class_name:<15} | Namespace: {namespace:<10} | ID: {actor_id}")


try:
    # 1) 'ALIVE' 상태 액터만 조회
    alive_actors = ray.get(get_cluster_actors.remote(state="ALIVE"))
    print_actors(alive_actors, "현재 활성화(ALIVE) 상태인 액터 목록")

    # 2) 'DEAD' 상태 액터만 조회
    dead_actors = ray.get(get_cluster_actors.remote(state="DEAD"))
    print_actors(dead_actors, "종료(DEAD)된 액터 목록")

    # 3) 전체 액터 조회 (state=None)
    # all_actors = ray.get(get_cluster_actors.remote())
    # print_actors(all_actors, "전체 액터 목록")

except Exception as e:
    print(f"액터 목록 조회 실패: {e}")
