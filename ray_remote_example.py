import ray
import time

# Ray Cluster Head Address
# Ray Client default port: 10001 (ray://<HEAD_IP>:10001)
# GCS/Redis default port: 6379 (<HEAD_IP>:6379)
HEAD_NODE_IP = "192.168.225.130"
RAY_ADDRESS = f"ray://{HEAD_NODE_IP}:10001"


# Define a remote task using the @ray.remote decorator
@ray.remote
def process_task(task_id: int, data: list) -> dict:
    """Ray Cluster 노드에서 실행되는 Remote 함수 예제.
    
    각 task_id와 데이터 리스트를 받아서 계산 결과 및 노드 실행 정보를 반환합니다.
    """
    start_time = time.time()
    
    # 노드 및 실행 환경 정보 수집
    context = ray.get_runtime_context()
    node_id = context.get_node_id()
    
    # 예시 연산: 리스트 내부 수의 제곱합 계산 및 지연 시뮬레이션
    total_sum = sum(x ** 2 for x in data)
    time.sleep(0.5)
    
    duration = time.time() - start_time
    
    return {
        "task_id": task_id,
        "node_id": node_id,
        "result": total_sum,
        "elapsed_sec": round(duration, 4)
    }


def main():
    print(f"Connecting to Ray Cluster Head Node at {RAY_ADDRESS}...")
    
    try:
        # Ray 클러스터 헤드 노드 연결
        ray.init(address=RAY_ADDRESS)
        print("Successfully connected to Ray Cluster!")
        
        # 클러스터 리소스 정보 출력
        cluster_resources = ray.cluster_resources()
        print(f"Cluster Resources: {cluster_resources}")
        
        # 1. 단일 Remote 함수 실행 예제
        print("\n--- [1] Single Remote Function Execution ---")
        ref = process_task.remote(1, [1, 2, 3, 4, 5])
        result = ray.get(ref)
        print(f"Single Task Result: {result}")
        
        # 2. 병렬 (Parallel) Remote 함수 실행 예제
        print("\n--- [2] Parallel Remote Functions Execution ---")
        task_data = [
            (i, list(range(i * 10, (i + 1) * 10))) for i in range(5)
        ]
        
        # .remote()를 사용해 비동기 태스크 제출
        futures = [process_task.remote(tid, data) for tid, data in task_data]
        
        # ray.get()으로 모든 병렬 태스크 완료까지 대기 및 결과 수집
        results = ray.get(futures)
        
        print(f"Gathered {len(results)} Parallel Task Results:")
        for res in results:
            print(f"  - Task #{res['task_id']}: Result={res['result']}, Node={res['node_id'][:12]}..., Time={res['elapsed_sec']}s")
            
    except Exception as e:
        print(f"Failed to connect or execute tasks on Ray cluster: {e}")
        print("Tip: Check if Ray head node port 10001 (Ray Client) or 6379 is open and ray is running with `ray start --head`.")
    finally:
        if ray.is_initialized():
            ray.shutdown()
            print("Ray session closed.")


if __name__ == "__main__":
    main()
