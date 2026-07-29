import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="데이터 엔지니어링 모니터링 대시보드",
    page_icon="📊",
    layout="wide",
)

st.title("📊 실시간 파이프라인 및 시스템 모니터링")
st.markdown("---")


# 2. 샘플 데이터 생성 (5초 TTL 캐시 지정, Region 데이터 추가)
@st.cache_data(ttl=5)
def load_data():
    regions = ["서울", "경기", "부산", "대구", "인천"]
    data = {
        "Timestamp": pd.date_range(
            start=pd.Timestamp.now() - pd.Timedelta(hours=99), periods=100, freq="h"
        ),
        "Pipeline": ["Ingestion", "Transformation", "Export"] * 33
        + ["Ingestion"],
        "Region": np.random.choice(regions, 100),
        "ExecutionTimeSec": np.random.uniform(5, 45, 100),
        "Status": np.random.choice(
            ["Success", "Failed", "Warning"], 100, p=[0.8, 0.1, 0.1]
        ),
    }
    return pd.DataFrame(data)


initial_df = load_data()

# 3. 세션 상태를 통한 메뉴 관리 (버튼 클릭 형태)
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "전체 분석"

st.sidebar.header("📌 메뉴")

# 라디오 동그라미 버튼 대신 선택 가능한 텍스트 버튼 생성
btn_type_all = "primary" if st.session_state.selected_menu == "전체 분석" else "secondary"
btn_type_region = "primary" if st.session_state.selected_menu == "지역별 분석" else "secondary"

if st.sidebar.button("🌐 전체 분석", type=btn_type_all, use_container_width=True):
    st.session_state.selected_menu = "전체 분석"
    st.rerun()

if st.sidebar.button("🗺 지역별 분석", type=btn_type_region, use_container_width=True):
    st.session_state.selected_menu = "지역별 분석"
    st.rerun()

menu = st.session_state.selected_menu

# 4. 프래그먼트 정의 (전체 분석)
@st.fragment(run_every="5s")
def render_live_dashboard(status_filter):
    df = load_data()
    filtered_df = df[df["Status"].isin(status_filter)]

    st.subheader("🌐 전체 파이프라인 분석")
    st.caption(f"⏱ 실시간 업데이트 중 (마지막 갱신: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')})")

    # 주요 지표 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 실행 횟수", len(filtered_df))
    col2.metric(
        "평균 실행 시간", f"{filtered_df['ExecutionTimeSec'].mean():.2f} 초" if not filtered_df.empty else "0 초"
    )
    col3.metric(
        "실패 건수",
        len(filtered_df[filtered_df["Status"] == "Failed"]),
        delta_color="inverse",
    )

    st.markdown("---")

    # 시각화
    st.subheader("📈 파이프라인별 실행 시간 추이")
    fig = px.line(
        filtered_df,
        x="Timestamp",
        y="ExecutionTimeSec",
        color="Pipeline",
        markers=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 상세 로그 데이터")
    st.dataframe(filtered_df, use_container_width=True)


# 5. 프래그먼트 정의 (지역별 분석)
@st.fragment(run_every="5s")
def render_region_dashboard(region_filter):
    df = load_data()
    filtered_df = df[df["Region"].isin(region_filter)]

    st.subheader("🗺 지역별 실행 분석")
    st.caption(f"⏱ 실시간 업데이트 중 (마지막 갱신: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')})")

    # 지역별 통계 차트
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏙 지역별 실행 건수")
        region_counts = filtered_df["Region"].value_counts().reset_index()
        region_counts.columns = ["Region", "Count"]
        fig_bar = px.bar(region_counts, x="Region", y="Count", color="Region")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("⚡ 지역별 상태 비율")
        fig_pie = px.pie(filtered_df, names="Status", title="전체 상태 분포")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 지역별 상세 로그 데이터")
    st.dataframe(filtered_df, use_container_width=True)


# 6. 메뉴별 조건부 사이드바 필터 및 화면 렌더링
if menu == "전체 분석":
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 필터 옵션")
    selected_status = st.sidebar.multiselect(
        "상태 선택", options=initial_df["Status"].unique(), default=initial_df["Status"].unique()
    )
    render_live_dashboard(selected_status)

elif menu == "지역별 분석":
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 필터 옵션")
    selected_region = st.sidebar.multiselect(
        "지역 선택", options=initial_df["Region"].unique(), default=initial_df["Region"].unique()
    )
    render_region_dashboard(selected_region)