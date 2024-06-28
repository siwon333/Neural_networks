import openai

# OpenAI API 키 설정
openai.api_key = 'sk-<YOUR_API'

def get_recipe_recommendations(class_list):
    try:
        # 클래스 리스트를 문자열로 변환
        ingredients = ', '.join(class_list)
        prompt = f'''
        레시피를 적을때에 {ingredients}는 모두 한국어로 답변해 주십시오!!
당신은 경험 많은 요리사입니다. 내 냉장고에 있는 재료들을 활용해 맛있고 영양가 있는 요리 레시피를 3가지 추천해주세요. 각 레시피에는 요리 이름, 필요한 재료 목록, 간단한 조리 방법을 포함해주세요.
레시피 3개 중 하나 이상은 반드시 {ingredients}을(를) 사용하는 레시피여야 합니다.
레시피를 적을때에 {ingredients}는 모두 한국어로 답변해 주십시오!!

냉장고 속 재료:
[{ingredients}, 쌀, 닭고기, 소고기, 돼지고기, 국수, 파스타면, 각종 양념류, 계란 ]

추가 요구사항:
1. 난이도(상, 중, 하)도 함께 제안해주세요.
2. 각 레시피에 대해 왜 이 조합이 좋은지 간단히 설명해주세요.
3. 선택적으로 사용할 수 있는 대체 재료도 제안해주세요.

레시피 형식:
요리 이름:
재료:
조리 방법:
추천 이유:
대체 재료 제안:
레시피를 적을때에 {ingredients}는 모두 한국어로 답변해 주십시오!!
        '''
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        recipe = response.choices[0].message['content'].strip()
        return recipe
    except Exception as e:
        return None
