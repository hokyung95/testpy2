import ray
from ray import serve
from starlette.requests import Request
import requests

# Ray Cluster Head Address & Serve HTTP Config
HEAD_NODE_IP = "192.168.225.130"
RAY_ADDRESS = f"ray://{HEAD_NODE_IP}:10001"
SERVE_HTTP_PORT = 8000


# Define a Ray Serve Deployment
@serve.deployment(
    name="prediction_service",
    num_replicas=1,
    ray_actor_options={"num_cpus": 1}
)
class ModelPredictor:
    def __init__(self, model_name: str = "DemoPredictor-v1"):
        self.model_name = model_name

    async def __call__(self, request: Request) -> dict:
        """HTTP 요청을 수신하여 처리하는 엔드포인트 메서드"""
        if request.method == "POST":
            try:
                json_data = await request.json()
            except Exception:
                json_data = {}
                
            inputs = json_data.get("inputs", [])
            operation = json_data.get("operation", "sum")
            
            if operation == "sum":
                prediction = sum(inputs)
            elif operation == "multiply":
                prediction = 1
                for x in inputs:
                    prediction *= x
            else:
                prediction = None

            return {
                "model": self.model_name,
                "operation": operation,
                "inputs": inputs,
                "prediction": prediction,
                "status": "success"
            }
        else:
            return {
                "model": self.model_name,
                "status": "active",
                "message": "Send a POST request with JSON body {'inputs': [1, 2, 3], 'operation': 'sum'}"
            }

    def predict_direct(self, inputs: list, operation: str = "sum") -> dict:
        """Python Serve Handle을 통한 직접 호출용 메서드"""
        if operation == "sum":
            prediction = sum(inputs)
        else:
            prediction = 0
        return {
            "model": self.model_name,
            "prediction": prediction,
            "via": "ServeHandle"
        }


def main():
    print(f"Connecting to Ray Cluster Head at {RAY_ADDRESS}...")
    
    try:
        # 1. Ray 클러스터 초기화 및 연결
        ray.init(address=RAY_ADDRESS)
        print("Successfully connected to Ray Cluster!")

        # 2. Ray Serve 애플리케이션 바인딩 및 배포
        print("\n--- Deploying Ray Serve Application ---")
        # deployment를 인스턴스화하여 바인딩
        app = ModelPredictor.bind(model_name="RayServe-Production-Model")
        
        # Ray Cluster에 Serve 애플리케이션 배포 및 시작
        # route_prefix="/api/predict" 경로로 엔드포인트 노출
        handle = serve.run(app, name="prediction_app", route_prefix="/api/predict")
        print(f"Deployment successfully deployed to cluster!")
        print(f"HTTP Endpoint URL: http://{HEAD_NODE_IP}:{SERVE_HTTP_PORT}/api/predict")

        # 3. HTTP Client를 통한 API 호출 테스트 예제
        print("\n--- [Test 1] Testing Service via HTTP Client (requests) ---")
        target_url = f"http://{HEAD_NODE_IP}:{SERVE_HTTP_PORT}/api/predict"
        
        payload = {
            "inputs": [10, 20, 30, 40],
            "operation": "sum"
        }
        
        try:
            print(f"Sending POST request to {target_url} with payload: {payload}")
            response = requests.post(target_url, json=payload, timeout=5)
            print(f"HTTP Status Code: {response.status_code}")
            print(f"HTTP Response Data: {response.json()}")
        except Exception as http_err:
            print(f"HTTP Request Note: Could not reach HTTP endpoint directly ({http_err}).")
            print(f"Make sure port {SERVE_HTTP_PORT} is open on host {HEAD_NODE_IP}.")

        # 4. Ray Serve Handle (Python In-Memory) 호출 테스트 예제
        print("\n--- [Test 2] Testing Service via Serve Handle ---")
        result_ref = handle.predict_direct.remote(inputs=[5, 15, 25], operation="sum")
        handle_result = ray.get(result_ref)
        print(f"Serve Handle Result: {handle_result}")

    except Exception as e:
        print(f"Failed to deploy Ray Serve module: {e}")
        print("Tip: Check if Ray Cluster Head is running and Ray Serve components are available.")
    finally:
        print("\nDeployment process completed.")


if __name__ == "__main__":
    main()
