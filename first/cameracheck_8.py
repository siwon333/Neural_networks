import cv2
import numpy as np
from ultralytics import YOLO

# YOLOv8 모델 로드
model = YOLO('./new_yolov8_100.pt')

# 웹캠 초기화
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # 이미지 전처리 및 예측
    results = model(frame)

    # 바운딩 박스 및 클래스 이름 추출
    if results and len(results) > 0:
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # 바운딩 박스 좌표
                class_id = int(box.cls[0])  # 클래스 ID
                class_name = model.names[class_id]  # 클래스 이름
                confidence = box.conf[0]  # 예측 확률

                # 바운딩 박스 및 클래스 이름 그리기
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'{class_name} {confidence:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # 이미지 보여주기
    cv2.imshow("YOLOv8 Detection", frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 캡처 종료 및 자원 해제
cap.release()
cv2.destroyAllWindows()
