import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------
# 1. 앱 기본 모바일 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="원주 맞춤 점메추 🎯",
    page_icon="🍱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. 원주시 공공데이터 & 음식 속성 데이터베이스 구축
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # (실제 공공데이터 CSV가 깃허브에 있다면 pd.read_csv('wonju_food.csv')로 불러옵니다)
    wonju_shops = pd.DataFrame({
        '업소명': ['원주복추어탕', '스시노백쉐프 원주혁신점', '미소노라멘', '신향마라탕', '원주봉화산 떡볶이', '시골보리밥', '단계동 샐러디'],
        '카테고리': ['매운_국물류', '일식/초밥', '일식/초밥', '매운_국물류', '고칼로리_분식', '든든한_한식', '가벼운_샐러드'],
        '주요메뉴': ['추어탕, 매운탕', '모듬초밥 정식', '돈코츠라멘', '마라탕, 꿔바로우', '떡볶이, 튀김', '보리밥정식', '연어 포케, 샐러드'],
        '위치': ['원주시 행구로 1', '원주시 혁신로 2', '원주시 무실동 3', '원주시 단계동 4', '원주시 단계동 5', '원주시 소초면 6', '원주시 무실동 7']
    })

    food_features = pd.DataFrame({
        '카테고리': ['매운_국물류', '시원한_면류', '고칼로리_분식', '가벼운_샐러드', '든든한_한식', '일식/초밥'],
        'spicy': [5, 2, 4, 0, 2, 1],
        'oily': [3, 1, 4, 1, 3, 2],
        'soup': [5, 4, 1, 0, 3, 2],
        'heavy': [4, 2, 4, 1, 4, 3]
    }).set_index('카테고리')
    
    return wonju_shops, food_features

wonju_shops, food_features = load_data()

# ---------------------------------------------------------
# 3. 앱 세션 메모리(상태) 초기화 (앱 접속 동안 취향 기억)
# ---------------------------------------------------------
if 'user_profile' not in st.session_state:
    # 기본 초기 취향 (국물 3, 매운맛 3)
    st.session_state['user_profile'] = np.array([3.0, 3.0, 3.0, 3.0])
    st.session_state['is_onboarded'] = False

# ---------------------------------------------------------
# 4. 앱 UI 탭 구획 나누기
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🎯 오늘의 추천", "👤 내 취향 설정", "📍 원주 맛집 DB"])

# ---------------------------------------------------------
# TAB 1: 메인 기능 (일일 퀵 체크인 & 추천)
# ---------------------------------------------------------
with tab1:
    st.title("🍱 오늘의 점메추 / 저메추")
    st.caption("당신의 기본 취향과 오늘 컨디션을 분석하여 원주 맛집을 매칭합니다!")
    
    if not st.session_state['is_onboarded']:
        st.info("💡 '👤 내 취향 설정' 탭에서 온보딩을 진행하면 더욱 정확한 추천을 받을 수 있습니다.")

    st.markdown("---")
    st.subheader("⚡ 3초 퀵 체크인")
    
    col1, col2 = st.columns(2)
    with col1:
        stress = st.slider("🔥 스트레스 지수", 1, 5, 3)
    with col2:
        happy = st.slider("😊 오늘 행복도", 1, 5, 3)
        
    weather = st.selectbox("🌧️ 현재 날씨", ["맑음", "흐림", "비/눈"])
    temp = st.slider("🌡️ 현재 기온 (°C)", -5, 35, 20)

    if st.button("🎯 맞춤 메뉴 추천받기", use_container_width=True):
        # 1. 정적 취향 가져오기
        base_vector = st.session_state['user_profile'].copy()
        
        # 2. 동적 상태 보정 벡터 계산
        dynamic_delta = np.array([0.0, 0.0, 0.0, 0.0])
        if stress >= 4:
            dynamic_delta += np.array([2.0, 1.0, 0.0, 1.5])
        if happy <= 2:
            dynamic_delta += np.array([0.5, 1.5, 0.0, 1.0])
        if weather == '비/눈':
            dynamic_delta += np.array([0.5, 0.0, 2.5, 0.5])
        if temp >= 28:
            dynamic_delta += np.array([-1.0, -1.0, 1.0, -1.5])

        final_user_vector = base_vector + dynamic_delta

        # 3. 코사인 유사도 계산
        all_vectors = np.vstack([final_user_vector, food_features.values])
        scaled_vecs = StandardScaler().fit_transform(all_vectors)
        
        user_vec = scaled_vecs[0].reshape(1, -1)
        food_vecs = scaled_vecs[1:]
        
        sim_scores = cosine_similarity(user_vec, food_vecs)[0]
        
        res_df = pd.DataFrame({
            '카테고리': food_features.index,
            '점수': np.round(sim_scores * 100, 1)
        }).sort_values(by='점수', ascending=False)
        
        top1_cat = res_df.iloc[0]['카테고리']
        top1_score = res_df.iloc[0]['점수']
        
        # 결과 화면 출력
        st.balloons()
        st.success(f"🏆 오늘 당신을 위한 1위 메뉴: **[{top1_cat}]** (적합도: {top1_score}점)")
        
        # 원주 공공데이터 맛집 매칭
        st.markdown("### 📍 추천 원주 지역 식당")
        matched = wonju_shops[wonju_shops['카테고리'] == top1_cat]
        if not matched.empty:
            for _, row in matched.iterrows():
                with st.expander(f"🍽️ {row['업소명']} ({row['주요메뉴']})"):
                    st.write(f"**위치:** {row['위치']}")
        else:
            st.write("해당 카테고리의 원주 추천 식당을 준비 중입니다.")

# ---------------------------------------------------------
# TAB 2: 취향 온보딩 (1회성 입력)
# ---------------------------------------------------------
with tab2:
    st.header("👤 나만의 취향 프로필 등록")
    st.write("앱이 기억할 당신의 평소 음식 취향을 입력해 주세요.")
    
    age = st.number_input("나이", 10, 90, 17)
    gender = st.radio("성별", ["남성", "여성"])
    
    spicy_input = st.slider("🌶️ 평소 매운맛 선호도", 1, 5, 3)
    soup_input = st.select_slider("🍜 국물 vs 비빔 취향", options=[1, 2, 3, 4, 5], 
                                  format_func=lambda x: {1:"완전국물파", 3:"상관없음", 5:"완전비빔파"}[x] if x in [1,3,5] else f"{x}단계")
    
    if st.button("💾 취향 저장하기", use_container_width=True):
        # 입력값을 기반으로 정적 취향 벡터 저장
        soup_score = 6 - soup_input
        st.session_state['user_profile'] = np.array([float(spicy_input), 3.0, float(soup_score), 3.0])
        st.session_state['is_onboarded'] = True
        st.success("내 취향이 성공적으로 앱 메모리에 저장되었습니다! 이제 '오늘의 추천' 탭을 이용해 보세요.")

# ---------------------------------------------------------
# TAB 3: 원주 공공데이터 목록
# ---------------------------------------------------------
with tab3:
    st.header("📍 원주시 공공데이터 식당 DB")
    st.caption("강원특별자치도 원주시 식당 기본정보 데이터셋")
    st.dataframe(wonju_shops, use_container_width=True)