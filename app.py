import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

st.set_page_config(page_title="도시 침수 예경보 모델", layout="wide")

st.title("🏙️ 도시 침수 예경보 모델")
st.markdown("실시간 SNS 기반 도시 침수 위험도를 시각화합니다.")

uploaded_file = st.file_uploader("📂 침수 관련 데이터 파일을 업로드하세요 (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # 결측치 제거
    df = df.dropna(subset=["위도", "경도", "결합감성점수", "총위험도"])

    # 지도 표시
    st.subheader("🗺️ 침수 위험 지역 지도")
    m = folium.Map(location=[df["위도"].mean(), df["경도"].mean()], zoom_start=13)

    for _, row in df.iterrows():
        risk = row["총위험도"]
        color = "red" if risk >= 3 else "orange" if risk == 2 else "blue"

        popup_text = (
            f"<b>장소:</b> {row['장소']}<br>"
            f"<b>위험 점수:</b> {row['총위험도']}<br>"
            f"<b>감성 점수:</b> {row['결합감성점수']}<br>"
            f"<b>내용:</b> {row['내용'][:100]}..."
        )

        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=5 + risk * 1.5,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=popup_text,
        ).add_to(m)

    st_data = st_folium(m, width=1000, height=600)

    # 위험도 통계
    st.subheader("📊 침수 위험도 분포")
    fig, ax = plt.subplots()
    df["총위험도"].value_counts().sort_index().plot(
        kind="bar", color=["blue", "orange", "red"], ax=ax
    )
    ax.set_xlabel("총위험도")
    ax.set_ylabel("게시글 수")
    ax.set_title("위험도 등급별 게시글 수")
    st.pyplot(fig)

    # 데이터 테이블
    with st.expander("📋 원본 데이터 보기"):
        st.dataframe(df)

else:
    st.info("먼저 침수 트윗 데이터를 업로드해주세요 (.xlsx)")
