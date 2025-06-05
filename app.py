import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

st.set_page_config(page_title="도시 침수 예경보 모델", layout="wide")
st.title("🌧️ 도시 침수 예경보 모델")

uploaded_file = st.file_uploader("🚨 침수 관련 감성 분석 결과 파일 업로드 (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # 감성점수 → 위험도 변환 함수
    def sentiment_to_risk(score):
        if score <= -0.5:
            return 3  # 매우 부정
        elif score < 0:
            return 2  # 약한 부정
        else:
            return 1  # 중립/긍정

    # 위험도 컬럼 생성
    df["risk_level"] = df["감성점수"].apply(sentiment_to_risk)

    # 📊 위험도 분포 시각화
    st.subheader("📉 위험도 분포")
    risk_counts = df["risk_level"].value_counts().sort_index()
    st.bar_chart(risk_counts.rename({1: "낮음", 2: "중간", 3: "높음"}))

    # 🌐 지도 시각화
    st.subheader("🗺️ 감성 기반 침수 위험 지도")
    m = folium.Map(location=[37.4979, 127.0276], zoom_start=13)

    for _, row in df.dropna(subset=["위도", "경도"]).iterrows():
        popup_text = (
            f"<b>📍 위치:</b> {row.get('place_name', '정보 없음')}<br>"
            f"<b>⚠️ 위험도:</b> {row['risk_level']}단계<br>"
            f"<b>🧠 감성:</b> {row['감성분류']}<br>"
            f"<b>📝 내용:</b> {row['내용'][:100]}"
        )
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=6,
            color="red" if row["risk_level"] == 3 else "orange" if row["risk_level"] == 2 else "blue",
            fill=True,
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)

    st_data = st_folium(m, width=1200, height=600)

    # 🧾 테이블 보기
    st.subheader("📄 업로드된 데이터 미리 보기")
    st.dataframe(df[["내용", "감성분류", "감성점수", "risk_level"]].head(10))
else:
    st.info("분석된 엑셀 파일을 업로드하세요.")
