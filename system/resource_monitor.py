import time
import psutil

def get_size(bytes, suffix="B"):
    """바이트 크기를 읽기 쉬운 단위(KB, MB, GB 등)로 변환하는 함수"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor
    return f"{bytes:.2f} Y{suffix}"

def monitor_system():
    print("=== 시스템 모니터링 시작 (종료하려면 Ctrl + C) ===")
    
    # 네트워크 사용량의 '초당 속도'를 계산하기 위해 이전 바이트 값 저장
    net_io = psutil.net_io_counters()
    prev_bytes_sent = net_io.bytes_sent
    prev_bytes_recv = net_io.bytes_recv
    prev_time = time.time()

    try:
        while True:
            time.sleep(2)
            current_time = time.time()
            time_interval = current_time - prev_time
            
            # 1. CPU 부하 체크 (1초 동안 측정)
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True) # 코어별 사용량

            # 2. 메모리 부하 체크
            mem = psutil.virtual_memory()
            mem_total = get_size(mem.total)
            mem_used = get_size(mem.used)
            mem_percent = mem.percent

            # 3. 네트워크 부하 체크 (초당 전송/수신 속도 계산)
            net_io = psutil.net_io_counters()
            bytes_sent_speed = (net_io.bytes_sent - prev_bytes_sent) / time_interval
            bytes_recv_speed = (net_io.bytes_recv - prev_bytes_recv) / time_interval
            
            prev_bytes_sent = net_io.bytes_sent
            prev_bytes_recv = net_io.bytes_recv
            prev_time = current_time

            # --- 결과 출력 ---
            print("\n" + "="*50)
            # CPU 출력
            print(f"[CPU] 전체 사용량: {cpu_percent}%")
            print(f"      코어별 사용량: {cpu_per_core}")
            
            # 메모리 출력
            print(f"[Memory] 전체: {mem_total} | 사용 중: {mem_used} ({mem_percent}%)")
            
            # 네트워크 출력
            print(f"[Network] 송신 속도(Upload): {get_size(bytes_sent_speed)}/s")
            print(f"          수신 속도(Download): {get_size(bytes_recv_speed)}/s")

    except KeyboardInterrupt:
        print("\n모니터링을 종료합니다.")

if __name__ == "__main__":
    monitor_system()