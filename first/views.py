import streamlit as st
import subprocess
from PIL import Image
import os
import pandas as pd
from db import get_db_connection
from datetime import datetime, timedelta
import sqlite3
from openai_api import get_recipe_recommendations

def show_my_fridge():
    st.markdown("<h1 style='text-align: center; color: #FF6347;'>내 냉장고</h1>", unsafe_allow_html=True)
    st.header("현재 냉장고 사진")

    # connect.py 실행하여 냉장고 사진 촬영
    result = subprocess.run(['python', 'connect.py'], capture_output=True, text=True)
    if result.returncode != 0:
        st.error(f"Error running connect.py: {result.stderr}")
        return

    # inside.jpg 파일이 있는지 확인하고, 있으면 보여줌
    image_path = './yolo/whole_images/inside.jpg'
    if os.path.isfile(image_path):
        fridge_image = Image.open(image_path)
        st.image(fridge_image, caption='현재 냉장고', use_column_width=True, output_format='JPEG')
    else:
        st.warning("Inside image not found.")

def show_ingredient_list():
    st.markdown("<h1 style='text-align: center; color: #FF6347;'>식자재 리스트</h1>", unsafe_allow_html=True)
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM detections", conn)

        # 중복 제거 (각 클래스의 가장 먼저 찍힌 항목만 남기기)
        df_sorted = df.sort_values(by='detected_time')
        df_unique = df_sorted.drop_duplicates(subset='class_name', keep='first')

        # 유통기한 계산 (입력시간 + 5일)
        df_unique['detected_time'] = pd.to_datetime(df_unique['detected_time'])
        df_unique['expiration_date'] = df_unique['detected_time'] + timedelta(days=5)

        if not df_unique.empty:
            for index, row in df_unique.iterrows():
                st.write(f"### {index + 1}. {row['class_name']}")
                # 이미지 경로 설정
                image_path = os.path.join('yolo', row['class_name'], f"{row['class_name']}.jpg")
                if os.path.exists(image_path):
                    st.image(image_path, width=100)
                st.write(f"이름: {row['class_name']}")
                st.write(f"기간: {row['detected_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"유통기한: {row['expiration_date'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write("---")
        else:
            st.warning("No items found in the database.")
    except sqlite3.OperationalError as e:
        st.error(f"Error: {e}")
    finally:
        conn.close()

def show_recipe_recommendations():
    st.markdown("<h1 style='text-align: center; color: #FF6347;'>레시피 추천</h1>", unsafe_allow_html=True)
    st.write("현재 냉장고에 있는 재료들로 만들 수 있는 레시피를 추천합니다.")

    # 데이터베이스에서 클래스들을 가져와서 리스트로 저장
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT class_name FROM detections WHERE class_name != 'Not Apple'")
    classes = cursor.fetchall()
    class_list = [class_[0] for class_ in classes]

    # 모든 클래스를 사용하여 레시피 생성 및 출력
    recipe = get_recipe_recommendations(class_list)
    if recipe:
        st.markdown(f"### 추천 레시피")
        st.write(recipe)
    else:
        st.error("레시피를 생성하는 중 오류가 발생했습니다.")

    conn.close()
