import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from io import BytesIO

st.set_page_config(page_title="도시 침수 예경보 모델", layout="wide")
st.title("🌊 도시 침수 예경보 모델")

# 🔽 1. 예제 엑셀 다운로드 버튼
st.markdown("#### 1️⃣ 예제 엑셀 파일 다운로드")
example_df = pd.DataFrame({
    "날짜": ["2022-08-08", "2022-08-08"],
    "작성자 ID": ["user1", "user2"],
    "내용": ["강남역 물이 너무 많이 찼어요", "도로가 침수돼서 차가 못 지나감"],
    "감성결과": ["부정", "부정"],
    "위도": [37.4979, 37.4985],
    "경도": [127.0276, 127.0268]
})
buffer = BytesIO()
example_df.to_excel(buffer, index=False, engine='openpyxl')
st.download_button(
    label="📥 예제 엑셀 파일 다운로드",
    data=buffer.getvalue(),
    file_name="gangnam_flood_example.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 🔼 2. 엑셀 업로드
st.markdown("#### 2️⃣ 엑셀 파일 업로드")
uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        df.columns = df.columns.str.strip()  # 공백 제거

        required_cols = ['위도', '경도', '내용']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"❌ 다음 필수 컬럼이 누락되었습니다: {missing_cols}")
        else:
            st.success("✅ 엑셀 파일이 성공적으로 업로드되었습니다!")

            # 지도 생성
            m = folium.Map(location=[df['위도'].mean(), df['경도'].mean()], zoom_start=13)

            for _, row in df.dropna(subset=['위도', '경도']).iterrows():
                popup_text = f"<b>📝 내용:</b> {row['내용'][:60]}..."
                folium.CircleMarker(
                    location=[row['위도'], row['경도']],
                    radius=6,
                    color='blue',
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=f"위도: {row['위도']}, 경도: {row['경도']}"
                ).add_to(m)

            st.markdown("#### 3️⃣ 침수 내용 지도 시각화")
            st_folium(m, width=700, height=500)
    except Exception as e:
        st.error(f"❌ 파일 처리 중 오류가 발생했습니다: {e}")
else:
    st.info("📌 예제 파일을 다운로드하고, 편집 후 업로드하세요.")
