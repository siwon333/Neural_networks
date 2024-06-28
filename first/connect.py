import cv2
import datetime
from ultralytics import YOLO
import sqlite3
import os

# 저장할 디렉토리 생성
save_dir = './yolo/whole_images'
os.makedirs(save_dir, exist_ok=True)

# 카메라 초기화
cap = cv2.VideoCapture(0)

# 카메라에서 프레임 읽기
ret, frame = cap.read()

# 카메라 해제
cap.release()

if ret:
    # 이미지 파일 경로 설정
    image_path = os.path.join(save_dir, 'inside.jpg')
    
    # 이미지 저장
    cv2.imwrite(image_path, frame)
    print(f"Inside image saved: {image_path}")

# 윈도우를 닫음
cv2.destroyAllWindows()

# 모델 로드
model = YOLO('./new_yolov8_100.pt')

# 데이터베이스 초기화
conn = sqlite3.connect('object_detection.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT,
                    detected_time TEXT)''')  # detected_time을 TEXT로 저장
conn.commit()

# 이미지 저장 여부를 확인할 딕셔너리
saved_images = {}

# 사진을 촬영하고 물체 인식 수행하여 데이터베이스에 저장하는 함수 정의
def capture_and_detect(model, conn, cursor):
    # 사진 촬영 (예시로 비디오 캡처 사용)
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        # 물체 인식
        results = model(frame)
        detected_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 문자열로 변환
        
        for result in results:
            for obj in result.boxes:
                if obj.conf > 0.1:  # 예측 확률이 일정 값 이상인 경우에만 처리
                    class_index = int(obj.cls.item())  # 클래스 인덱스를 int로 변환
                    class_name = model.names[class_index]  # 클래스 이름을 가져옴
                    
                    # 바운딩 박스 좌표
                    x1, y1, x2, y2 = map(int, obj.xyxy[0])  # obj.xyxy는 [x1, y1, x2, y2] 형태의 네 개의 좌표
                    
                    # 데이터베이스에 저장 (중복 클래스는 가장 높은 확률만 남김)
                    cursor.execute("DELETE FROM detections WHERE class_name = ?", (class_name,))
                    cursor.execute("INSERT INTO detections (class_name, detected_time) VALUES (?, ?)",
                                   (class_name, detected_time))
                    conn.commit()

                    # 이미지 크롭 및 저장
                    if class_name not in saved_images:
                        saved_images[class_name] = True  # 이미지 저장 여부 업데이트
                        
                        # 크롭된 이미지 저장
                        class_dir = os.path.join('./yolo', class_name)
                        os.makedirs(class_dir, exist_ok=True)
                        crop_filename = f"{class_name}.jpg"
                        crop_path = os.path.join(class_dir, crop_filename)
                        
                        # 이미지 크롭
                        cropped_image = frame[y1:y2, x1:x2]
                        
                        # 크롭된 이미지 저장
                        cv2.imwrite(crop_path, cropped_image)

# 10장의 사진을 촬영하고 물체 인식 수행
for i in range(5):
    capture_and_detect(model, conn, cursor)

# 데이터베이스 연결 해제
conn.close()

import pandas as pd

# 데이터베이스에서 데이터 불러오기
conn = sqlite3.connect('object_detection.db')
df = pd.read_sql_query("SELECT * FROM detections", conn)

# 중복 제거
df_sorted = df.sort_values(by='detected_time')
df_unique = df_sorted.drop_duplicates(subset='class_name', keep='first')

# 기존 데이터 삭제 후 중복 제거된 데이터 삽입
conn = sqlite3.connect('object_detection.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM detections")
conn.commit()

df_unique.to_sql('detections', conn, if_exists='append', index=False)

conn.close()
