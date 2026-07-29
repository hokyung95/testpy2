import os
from mutagen.mp3 import MP3

def get_mp3_duration(folder_path):
    # 폴더 내 파일 목록 가져오기
    # files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    files = sorted(
    [f for f in os.listdir(folder_path) if f.endswith('.mp3')],
    key=lambda x: os.path.getmtime(os.path.join(folder_path, x)),
    reverse=True
)
    
    if not files:
        print("폴더에 MP3 파일이 없습니다.")
        return

    print(f"{'파일명':<30} | {'재생 시간'}")
    print("-" * 50)

    for file in files:
        file_path = os.path.join(folder_path, file)
        try:
            audio = MP3(file_path)
            total_seconds = int(audio.info.length) + 1
            
            # 시간, 분, 초 계산
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = (total_seconds % 60 ) 
            
            time_str = f"{minutes:02d}:{seconds:02d}"
            # print(f"{file[:28]:<30}          | ")
            print(f"{time_str}  {file[:90]}")
            
        except Exception as e:
            print(f"{file}: 정보를 읽을 수 없습니다. ({e})")

# 사용 예시: 'C:/Music' 폴더의 경로를 입력하세요
folder_path = "D:\\유튜브작업\\롱폼\\SUNO음악\\20260727" 
get_mp3_duration(folder_path)