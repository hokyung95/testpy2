# run.py
import os
from streamlit.web import bootstrap

if __name__ == "__main__":
    # 대시보드 메인 파일 경로 지정
    app_path = os.path.abspath("dashboard_1.py")
    
    # Streamlit 내부 실행 설정 플래그
    flag_options = {
        "server.port": 8501,
        "global.developmentMode": False,
    }
    
    # Streamlit 서버 부트스트랩 실행
    bootstrap.run(app_path, "streamlit run", [], flag_options)