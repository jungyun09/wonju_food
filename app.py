import streamlit as st
import pandas as pd

# 앱 페이지 제목 및 디자인
st.set_page_config(page_title="원주 맞춤 점메추", page_icon="🍽️")

st.title("🍽️ 원주 맞춤형 점메추 / 저메추")
st.caption("당신의 취향과 오늘 컨디션을 분석해 원주 맛집을 추천합니다!")

# 사이드바: 1회성 온보딩 데이터 입력
with st.sidebar:
    st.header("👤 1회성 취향 온보딩")
    age = st.number_input("나이", min_value=10, max_value=80, value=17)
    gender = st.radio("성별", ["남성", "여성"])
    spicy_pref = st.slider("매운맛 선호도 (1:맵질이 ~ 5:매운맛마니아)", 1, 5, 3)
    soup_pref = st.select_slider("취향 밸런스", options=["완전 국물파", "국물 선호", "상관없음", "비빔/볶음 선호", "완전 비빔파"])
    st.success("취향 정보가 저장되었습니다!")

# 메인 화면: 일일 퀵 체크인 (3~5초 소요)
st.subheader("오늘의 퀵 체크인 (3초 소요)")
col1, col2 = st.columns(2)

with col1:
    stress = st.slider("🔥 오늘 스트레스 지수는?", 1, 5, 3)
with col2:
    happy = st.slider("😊 오늘 행복도는?", 1, 5, 3)

weather = st.selectbox("🌧️ 오늘 날씨는 어떤가요?", ["맑음", "흐림", "비/눈"])

# 추천 버튼 클릭 시 결과 출력
if st.button("🎯 오늘의 맞춤 메뉴 추천받기"):
    st.divider()
    st.balloons() # 축하 효과 애니메이션
    
    # (이 부분에 앞서 작성한 머신러닝 추천 로직이 들어갑니다)
    st.header("🏆 오늘의 추천 메뉴: [ 마라탕 ]")
    st.write(f"오늘 스트레스({stress}점)가 높아 자극적이고 매콤한 국물 요리를 추천합니다!")
    
    # 원주시 공공데이터 식당 예시 표 출력
    st.subheader("📍 원주 지역 추천 식당")
    sample_wonju_data = pd.DataFrame({
        "식당 이름": ["신향마라탕", "탕화쿵푸 마라탕 무실점"],
        "주요 메뉴": ["마라탕, 꿔바로우", "마라탕, 마라샹궈"],
        "위치": ["원주시 단계동", "원주시 무실동"]
    })
    st.dataframe(sample_wonju_data, use_container_width=True)