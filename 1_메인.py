import streamlit as st

# 이미지 URL (GitHub Raw URL)
image_url = "https://raw.githubusercontent.com/JUNG-PFe/pitcher-visualization_2/main/wordmark.jpg"

# 상단 레이아웃: 로고는 왼쪽 상단에 배치
col1, col2 = st.columns([1, 4])  # 비율을 조정해 로고를 왼쪽 정렬
with col1:
    st.image(image_url, width=200)  # 로고 크기를 150x50으로 유지

# 타이틀: 중앙에 정렬
st.markdown(
    """
    <h1 style="text-align: center; margin-top: 10px; font-size: 4em;">KIA 투수 데이터 분석</h1>
    """,
    unsafe_allow_html=True,
)

# 설명 텍스트: 한 칸 아래로 내리고 글자 크기를 2배로 설정
st.markdown(
    """
    <p style="text-align: center; font-size: 1.5em; margin-top: 20px;">사이드에서 분석 페이지를 선택하세요.</p>
    """,
    unsafe_allow_html=True,
)

# 페이지 하단 추가 내용
st.write("---")
st.write("1.PTS 데이터 24 : 24시즌 구속, 스크라이트, 볼 비율 등과 투구 로케이션 확인")
st.write("2.PTS 데이터 데이터 존별 타구속도 24 : 24시즌 투수 존별 안타 타구 속도 확인")
st.write("3.호크아이 데이터 23-24 : 기본 트래킹 데이터 확인, 구종별 로케이션, 무브먼트 차트 확인")
st.write("4.호크아이 선수비교 : 선수간 트래킹 데이터 비교")
st.write("4.호크아이 트랜드 분석 : 각 선수 트래킹 데이터 추이 분석")