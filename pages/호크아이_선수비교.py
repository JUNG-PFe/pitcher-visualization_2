import pandas as pd
import streamlit as st
import plotly.express as px
import io

# 데이터 컬러 설정
cols = {
    "직구": "#4C569B",
    "투심": "#B590C3",
    "커터": "#45B0D8",
    "슬라": "firebrick",
    "스위퍼": "#00FF00",
    "체인": "#FBE25E",
    "포크": "MediumSeaGreen",
    "커브": "orange",
    "너클": "black"
}

@st.cache_data
def load_data():
    # 데이터 URL
    data_url1 = "https://github.com/JUNG-PFe/pitcher-visualization_2/raw/refs/heads/main/24_merged_data_%EC%88%98%EC%A0%95.xlsx"
    data_url2 = "https://github.com/JUNG-PFe/pitcher-visualization_2/raw/refs/heads/main/23_merged_data_%EC%88%98%EC%A0%95.xlsx"
    
    # 데이터 로드
    df1 = pd.read_excel(data_url1)
    df2 = pd.read_excel(data_url2)
    
    # 날짜 형식 통일
    df1['Date'] = pd.to_datetime(df1['Date'])
    df2['Date'] = pd.to_datetime(df2['Date'])
    
    # 병합
    combined_df = pd.concat([df1, df2], ignore_index=True)
    return combined_df

# 데이터 로드
df = load_data()

st.set_page_config(
    page_title="23-24 호크아이 데이터 선수간 비교",
    page_icon="⚾",
    layout="wide"
)

# -------------------------------
# 로그인 여부 확인
# -------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("로그인 후에 이 페이지를 이용할 수 있습니다.")
    st.stop()  # 로그인 상태가 아니면 여기서 실행 중지

st.title("호크아이 데이터 선수 간 비교분석")

# 탭 생성
tab1, tab2 = st.tabs(["선수 간 비교", "기간 간 비교"])

# -------------------
# Tab 1: 선수 간 비교
# -------------------
with tab1:
    st.subheader("선수 간 비교")

    # 선수 1과 선수 2 검색 및 선택 가로 배치
    col1, col2 = st.columns(2)

    with col1:
        # 선수 1 검색 및 선택
        search_query_1 = st.text_input("선수 1 검색", key="search_query_1").strip()
        if search_query_1:
            suggestions_1 = [name for name in sorted(df['투수'].unique()) if search_query_1.lower() in name.lower()]
        else:
            suggestions_1 = sorted(df['투수'].unique())

        if suggestions_1:
            pitcher1 = st.selectbox("선수 1 선택", suggestions_1, key="pitcher1")
        else:
            st.warning("선수 1 검색 결과가 없습니다.")
            pitcher1 = None

    with col2:
        # 선수 2 검색 및 선택
        search_query_2 = st.text_input("선수 2 검색", key="search_query_2").strip()
        if search_query_2:
            suggestions_2 = [name for name in sorted(df['투수'].unique()) if search_query_2.lower() in name.lower()]
        else:
            suggestions_2 = sorted(df['투수'].unique())

        if suggestions_2:
            pitcher2 = st.selectbox("선수 2 선택", suggestions_2, key="pitcher2")
        else:
            st.warning("선수 2 검색 결과가 없습니다.")
            pitcher2 = None
            
    # 구종 선택
    pitch_type = st.multiselect("구종 선택", df['구종'].unique(), key="pitch_type")

    # 비교할 변수 선택
    compare_variables = [
        "RelSpeed", "SpinRate", "회전효율", 
        "Tilt", "InducedVertBreak", "HorzBreak", 
        "RelHeight", "RelSide", "Extension"
    ]
    selected_variables = st.multiselect("비교할 변수 선택", compare_variables)

    if pitcher1 and pitcher2 and selected_variables:
        # 데이터 필터링
        pitcher1_data = df[df['투수'] == pitcher1]
        pitcher2_data = df[df['투수'] == pitcher2]

        if not pitcher1_data.empty and not pitcher2_data.empty:
            comparison_results = []
            for variable in selected_variables:
                # Tilt 처리
                if variable == "Tilt":
                    pitcher1_value = pitcher1_data[variable].mode().iloc[0] if not pitcher1_data[variable].mode().empty else "N/A"
                    pitcher2_value = pitcher2_data[variable].mode().iloc[0] if not pitcher2_data[variable].mode().empty else "N/A"
                else:
                    # 평균값 계산
                    pitcher1_value = round(pitcher1_data[variable].mean(), 2)
                    pitcher2_value = round(pitcher2_data[variable].mean(), 2)

                # 결과 저장
                comparison_results.append({
                    "변수": variable,
                    "선수 1 평균": pitcher1_value,
                    "선수 2 평균": pitcher2_value,
                    "차이": abs(pitcher1_value - pitcher2_value) if variable != "Tilt" else "N/A"
                })

            # 결과를 데이터프레임으로 표시
            comparison_df = pd.DataFrame(comparison_results)
            st.subheader("선수 간 변수 비교 결과")
            st.dataframe(comparison_df)

            # 여러 변수 시각화
            for variable in selected_variables:
                if variable == "Tilt":
                    st.warning(f"{variable} 변수는 시각화에 적합하지 않습니다.")
                    continue

                # 변수별 막대그래프 생성
                combined_df = pd.DataFrame({
                    "선수": [pitcher1, pitcher2],
                    "평균값": [
                        comparison_df.loc[comparison_df["변수"] == variable, "선수 1 평균"].values[0],
                        comparison_df.loc[comparison_df["변수"] == variable, "선수 2 평균"].values[0]
                    ]
                })

                fig = px.bar(
                    combined_df,
                    x="선수",
                    y="평균값",
                    title=f"{variable} 선수 간 비교 ({pitcher1} vs {pitcher2})",
                    labels={"평균값": variable},
                    color="평균값",
                    color_continuous_scale="Viridis"
                )

                # y축 범위 조정
                fig.update_layout(
                    yaxis=dict(
                        range=[
                            min(combined_df["평균값"]) - 15,
                            max(combined_df["평균값"]) + 15
                        ],
                        title=variable
                    ),
                    xaxis=dict(title="선수"),
                    title_font=dict(size=20),
                    width=800,
                    height=600
                )
                st.plotly_chart(fig)

            # 구종별 수평/수직 무브먼트 시각화
            st.subheader("구종별 수평/수직 무브먼트")
            pitcher1_grouped = (
                pitcher1_data.groupby("구종")[["HorzBreak", "InducedVertBreak"]]
                .mean()
                .reset_index()
                .assign(투수=pitcher1)
            )
            pitcher2_grouped = (
                pitcher2_data.groupby("구종")[["HorzBreak", "InducedVertBreak"]]
                .mean()
                .reset_index()
                .assign(투수=pitcher2)
            )

            # 두 선수의 데이터 결합
            combined_data = pd.concat([pitcher1_grouped, pitcher2_grouped])

            fig = px.scatter(
                combined_data,
                x="HorzBreak",
                y="InducedVertBreak",
                color="투수",
                symbol="구종",
                title="구종별 수평/수직 무브먼트",
                hover_data=["구종", "투수"],
                labels={"HorzBreak": "수평 무브 (cm)", "InducedVertBreak": "수직 무브 (cm)"},
                color_discrete_map={pitcher1: "red", pitcher2: "blue"}
            )

            # 축 및 레이아웃 설정
            fig.update_traces(marker=dict(size=12))
            fig.update_layout(
                width=800,
                height=750,
                xaxis=dict(range=[-70, 70], linecolor="black"),
                yaxis=dict(range=[-70, 70], linecolor="black"),
            )
            fig.add_shape(type="line", x0=0, y0=-70, x1=0, y1=70, line=dict(color="black", width=2))
            fig.add_shape(type="line", x0=-70, y0=0, x1=70, y1=0, line=dict(color="black", width=2))

            st.plotly_chart(fig)
# -------------------
# Tab 2: 기간 간 비교
# -------------------
with tab2:
    st.subheader("기간 간 비교")

    # 선수 검색 및 선택
    search_query = st.text_input("선수 이름 검색", "").strip()
    if search_query:
        filtered_suggestions = [name for name in sorted(df['투수'].unique()) if search_query.lower() in name.lower()]
    else:
        filtered_suggestions = sorted(df['투수'].unique())

    if filtered_suggestions:
        pitcher_name = st.selectbox("투수 이름 선택", filtered_suggestions, key="pitcher_search")
    else:
        st.warning("검색된 선수가 없습니다.")
        pitcher_name = None

    # 기간 1 설정 (가로 배치)
    col1, col2 = st.columns(2)
    with col1:
        start_date_1 = st.date_input("기간 1 시작 날짜", df['Date'].min(), key="start_date_1")
    with col2:
        end_date_1 = st.date_input("기간 1 종료 날짜", df['Date'].max(), key="end_date_1")

    # 기간 2 설정 (가로 배치)
    col3, col4 = st.columns(2)
    with col3:
        start_date_2 = st.date_input("기간 2 시작 날짜", df['Date'].min(), key="start_date_2")
    with col4:
        end_date_2 = st.date_input("기간 2 종료 날짜", df['Date'].max(), key="end_date_2")

    # 비교할 변수 선택 (여러 변수)
    selected_variables = st.multiselect("비교할 변수 선택", compare_variables, key="period_variables")

    # 데이터 필터링 (선수 이름 포함)
    if pitcher_name and selected_variables:
        filtered_df_1 = df[(df['투수'] == pitcher_name) & 
                           (df['Date'] >= pd.Timestamp(start_date_1)) & 
                           (df['Date'] <= pd.Timestamp(end_date_1))]

        filtered_df_2 = df[(df['투수'] == pitcher_name) & 
                           (df['Date'] >= pd.Timestamp(start_date_2)) & 
                           (df['Date'] <= pd.Timestamp(end_date_2))]

        if not filtered_df_1.empty and not filtered_df_2.empty:
            comparison_results = []
            for variable in selected_variables:
                # Tilt 처리
                if variable == "Tilt":
                    value_1 = filtered_df_1[variable].mode().iloc[0] if not filtered_df_1[variable].mode().empty else "N/A"
                    value_2 = filtered_df_2[variable].mode().iloc[0] if not filtered_df_2[variable].mode().empty else "N/A"
                else:
                    # 평균값 계산 (숫자형 변수)
                    value_1 = round(filtered_df_1[variable].mean(), 2)
                    value_2 = round(filtered_df_2[variable].mean(), 2)

                # 결과 저장
                comparison_results.append({
                    "변수": variable,
                    "기간 1 평균": value_1,
                    "기간 2 평균": value_2,
                    "차이": abs(value_1 - value_2) if variable != "Tilt" else "N/A"
                })

            # 결과를 데이터프레임으로 표시
            comparison_df = pd.DataFrame(comparison_results)
            st.subheader("기간 간 변수 비교 결과")
            st.dataframe(comparison_df)

            # 여러 변수 시각화
            for variable in selected_variables:
                if variable == "Tilt":
                    st.warning(f"{variable} 변수는 시각화에 적합하지 않습니다.")
                    continue

                # 데이터프레임 생성
                combined_df = pd.DataFrame({
                    "기간": ["기간 1", "기간 2"],
                    "평균값": [
                        comparison_df.loc[comparison_df["변수"] == variable, "기간 1 평균"].values[0],
                        comparison_df.loc[comparison_df["변수"] == variable, "기간 2 평균"].values[0]
                    ]
                })

                # 변수별 막대그래프 생성
                fig = px.bar(
                    combined_df,
                    x="기간",
                    y="평균값",
                    title=f"{variable} 기간 간 비교 ({pitcher_name})",
                    labels={"평균값": variable},
                    color="평균값",  # 값에 따라 색상 변화
                    color_continuous_scale="Viridis"  # 색상 스케일 적용
                )

                # y축 범위 조정
                fig.update_layout(
                    yaxis=dict(
                        range=[
                            min(combined_df["평균값"]) - 10, 
                            max(combined_df["평균값"]) + 10
                        ],
                        title=variable
                    ),
                    xaxis=dict(title="기간"),
                    title_font=dict(size=20),  # 제목 폰트 크기 조정
                    width=800,  # 그래프 넓이
                    height=600  # 그래프 높이
                )
                st.plotly_chart(fig)

            # 구종별 수평/수직 무브먼트 시각화
            st.subheader("구종별 수평/수직 무브먼트")
            grouped_df_1 = (
                filtered_df_1.groupby("구종")[["HorzBreak", "InducedVertBreak"]]
                .mean()
                .reset_index()
                .assign(기간="기간 1")
            )
            grouped_df_2 = (
                filtered_df_2.groupby("구종")[["HorzBreak", "InducedVertBreak"]]
                .mean()
                .reset_index()
                .assign(기간="기간 2")
            )

            # 데이터 결합
            movement_data = pd.concat([grouped_df_1, grouped_df_2])

            # 산점도 생성
            fig3 = px.scatter(
                movement_data,
                x="HorzBreak",
                y="InducedVertBreak",
                color="기간",
                symbol="구종",
                title=f"{pitcher_name} 구종별 수평/수직 무브먼트 비교",
                hover_data=["구종"],
                labels={"HorzBreak": "수평 무브 (cm)", "InducedVertBreak": "수직 무브 (cm)"},
                color_discrete_map={"기간 1": "red", "기간 2": "blue"}
            )

            # 축 및 레이아웃 설정
            fig3.update_traces(marker=dict(size=12))
            fig3.update_layout(
                width=800,
                height=750,
                xaxis=dict(range=[-70, 70], linecolor="black"),
                yaxis=dict(range=[-70, 70], linecolor="black"),
            )
            fig3.add_shape(type="line", x0=0, y0=-70, x1=0, y1=70, line=dict(color="black", width=2))
            fig3.add_shape(type="line", x0=-70, y0=0, x1=70, y1=0, line=dict(color="black", width=2))

            # 산점도 출력
            st.plotly_chart(fig3)