import google.generativeai as genai
import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import os
import time

st.set_page_config(
    page_title="핏멘토",
    page_icon="🏋️‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 환경 변수 로드
load_dotenv()
my_key = os.getenv('MY_KEY')
genai.configure(api_key=my_key)

generation_config = genai.GenerationConfig(temperature=0.5)

safety_settings=[
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_LOW_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_LOW_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_LOW_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_LOW_AND_ABOVE",
    },
]

@st.cache_resource
def load_model():
    model = genai.GenerativeModel('gemini-1.5-flash-latest', generation_config=generation_config, safety_settings=safety_settings)
    print("Model loaded...")
    return model

model = load_model()

# Streamlit 애플리케이션 제목
st.title("핏멘토 🏋️‍♀️ : 맞춤 피트니스 코칭")

with st.sidebar:
    choice = option_menu("", ["맞춤 코칭", "오늘의 운동", "AI 멘토 상담"],
    icons=['house', 'bi bi-check2-all', 'bi bi-robot'],
    menu_icon="app-indicator", default_index=0,
    styles={
        "container": {"padding": "4!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
        "nav-link-selected": {"background-color": "#08c7b4"},
    }
    )

if choice == '맞춤 코칭':
    goal_category = st.selectbox(
        "피트니스 목표를 선택하세요.",
        ["체중 감량", "근육 증가", "유연성 향상", "전반적인 건강 개선"]
    )
    goal_description = st.text_input("목표에 대한 자세한 설명을 입력하세요.")
    fit_day = st.text_input("운동 기간을 입력하세요.")
    fit_time = st.text_input("하루에 평균 운동 가능 시간을 입력하세요.")
    experience_level = st.selectbox(
        "운동 경험 수준을 선택하세요.",
        ["초급", "중급", "고급"]
    )

    if st.button("추천 받기"):
        if goal_description:
            with st.spinner("🏃‍♀️ 맞춤 운동 계획을 준비 중입니다 🏃‍♂️"):
                chat = model.start_chat(history=[])
                prompt = f"""
                사용자 피트니스 목표: {goal_category}
                목표에 대한 자세한 설명: {goal_description}
                운동 기간 : {fit_day}
                하루 평균 운동 시간 : {fit_time}
                운동 경험 수준: {experience_level}

                운동 계획을 800자 이내로 추천해 주세요. 
                답변에는 표를 포함하고, 각 운동의 종류와 세트 및 반복 수를 포함해 주세요.
                표 안에는 마크다운 문법이 포함되지 않도록 답변하세요.
                """
                response_placeholder = st.empty()
                # response = chat.send_message(prompt)
                model.generate_content(prompt, stream=True)
                response_text = response.text

                # for i in range(len(response_text) + 1):
                #     response_placeholder.markdown(response_text[:i])
                #     time.sleep(0.02)

                st.write(response.text)
                st.write("오늘도 화이팅! 운동 목표를 잊지 마세요!")

        else:
            st.warning("목표를 입력해주세요.")

    feedback = st.text_area("핏멘토의 맞춤 운동 추천에 대해 피드백을 남겨주세요!")
    if st.button("피드백 제출"):
        st.success("피드백이 제출되었습니다. 감사합니다!")

elif choice == '오늘의 운동':
    st.subheader("오늘 한 운동에 체크 해주세요 ✅")
    st.checkbox("준비운동")
    st.checkbox("근력운동")
    st.checkbox("유산소운동")
    st.checkbox("마무리운동")

    if st.button("제출"):
        st.success("오늘의 운동 결과가 제출되었습니다. 고생하셨습니다!")

elif choice == 'AI 멘토 상담':
    if "chat_session" not in st.session_state:
        st.session_state["chat_session"] = model.start_chat(history=[])

    for content in st.session_state.chat_session.history:
        with st.chat_message("AI 멘토" if content.role == "model" else "user"):
            st.markdown(content.parts[0].text)

    if prompt := st.chat_input("무엇이든 편하게 상담해 주세요!"):
        with st.chat_message("user"):
            st.markdown(prompt)
        full_prompt = f"""
        당신은 사용자에게 맞춤형 피트니스 코칭을 해주는 AI 멘토입니다. 
        사용자 상담 요청: {prompt}
        사용자 상담 요청에 따라 적절한 조언이나 정보를 친절하게 제공해 주세요.
        답변은 800자 이내로 하고, 답변에 표정 이모티콘을 반드시 하나 이상 포함해 주세요.
        """
        with st.chat_message("ai"):
            with st.spinner("🏃‍♀️ AI 멘토가 답변 중입니다 🏃‍♂️"):
                # response_placeholder = st.empty()
                # response = st.session_state.chat_session.send_message(full_prompt)
                model.generate_content(prompt, stream=True)
                response_text = response.text
                # for i in range(len(response_text) + 1):
                #     response_placeholder.markdown(response_text[:i])
                #     time.sleep(0.02)
                st.markdown(response.text)
