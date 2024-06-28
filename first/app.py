import streamlit as st
from views import show_my_fridge, show_ingredient_list, show_recipe_recommendations
from utils import local_css, get_image_base64

def main():
    local_css("./styles.css")  # Apply custom CSS if needed

    # Define sidebar layout using st.sidebar.button
    st.sidebar.title("내 냉장고")  # Sidebar title


    # Define sidebar buttons for each menu item
    if st.sidebar.button("지금 내 냉장고 보기"):
        show_my_fridge()

    if st.sidebar.button("식자재 리스트 보기"):
        show_ingredient_list()

    if st.sidebar.button("레시피 추천 보기"):
        show_recipe_recommendations()

if __name__ == '__main__':
    main()

 