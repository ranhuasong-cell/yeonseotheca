import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from components.styles import apply_global_styles, sidebar_logo, page_header
from utils.database import get_stats, get_all_books, init_db

st.set_page_config(page_title="통계 | 연서테카", page_icon="📊", layout="wide")
init_db()
apply_global_styles()
sidebar_logo()

NAVY = "#0A1628"
NAVY2 = "#0F2040"
GOLD = "#C9A84C"
GOLD_LIGHT = "#E8C96A"
TEXT = "#E8E0D0"
MUTED = "#8A9BB5"

page_header("서재 통계", "나의 서재 현황을 한눈에 확인합니다")

stats = get_stats()
books = get_all_books()

if not books:
    st.markdown('<div style="color:#8A9BB5; text-align:center; padding:4rem;">아직 등록된 책이 없습니다.<br>📸 책 추가 메뉴에서 책을 등록해보세요!</div>', unsafe_allow_html=True)
    st.stop()

# 상단 요약 수치
c1, c2, c3, c4 = st.columns(4)
authors = set(b["author"] for b in books if b.get("author"))
publishers = set(b["publisher"] for b in books if b.get("publisher"))
with c1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total"]}</div><div class="stat-label">전체 도서</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{len(authors)}</div><div class="stat-label">저자 수</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{len(publishers)}</div><div class="stat-label">출판사 수</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{len(stats["by_location"])}</div><div class="stat-label">서재 위치</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

# 위치별 도서 수 + 출판사별 차트
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div style="color:#C9A84C; font-weight:600; margin-bottom:0.8rem;">📍 위치별 도서 수</div>', unsafe_allow_html=True)
    if stats["by_location"]:
        df_loc = pd.DataFrame(stats["by_location"])
        fig = px.bar(
            df_loc, x="cnt", y="location", orientation="h",
            color_discrete_sequence=[GOLD],
            labels={"cnt": "권 수", "location": "위치"},
        )
        fig.update_layout(
            paper_bgcolor=NAVY2, plot_bgcolor=NAVY2,
            font_color=TEXT, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor="#1A3355", tickfont=dict(color=MUTED)),
            yaxis=dict(tickfont=dict(color=TEXT)),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("위치 정보가 없습니다")

with col_right:
    st.markdown('<div style="color:#C9A84C; font-weight:600; margin-bottom:0.8rem;">🏢 출판사별 도서 수 (상위 10)</div>', unsafe_allow_html=True)
    if stats["by_publisher"]:
        df_pub = pd.DataFrame(stats["by_publisher"])
        fig2 = px.pie(
            df_pub, values="cnt", names="publisher",
            color_discrete_sequence=px.colors.sequential.YlOrBr_r,
            hole=0.4,
        )
        fig2.update_layout(
            paper_bgcolor=NAVY2, plot_bgcolor=NAVY2,
            font_color=TEXT, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color=MUTED), bgcolor=NAVY2),
            height=300,
        )
        fig2.update_traces(textfont_color=TEXT)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.caption("출판사 정보가 없습니다")

st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

# 월별 추가 추이
st.markdown('<div style="color:#C9A84C; font-weight:600; margin-bottom:0.8rem;">📅 월별 도서 추가 추이</div>', unsafe_allow_html=True)
df = pd.DataFrame(books)
df["added_at"] = pd.to_datetime(df["added_at"])
df["month"] = df["added_at"].dt.to_period("M").astype(str)
monthly = df.groupby("month").size().reset_index(name="cnt")

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=monthly["month"], y=monthly["cnt"],
    mode="lines+markers",
    line=dict(color=GOLD, width=2),
    marker=dict(color=GOLD, size=8),
    fill="tozeroy",
    fillcolor="rgba(201,168,76,0.1)",
))
fig3.update_layout(
    paper_bgcolor=NAVY2, plot_bgcolor=NAVY2,
    font_color=TEXT, margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(gridcolor="#1A3355", tickfont=dict(color=MUTED)),
    yaxis=dict(gridcolor="#1A3355", tickfont=dict(color=MUTED)),
    height=250,
)
st.plotly_chart(fig3, use_container_width=True)

# 전체 도서 목록 테이블
st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
st.markdown('<div style="color:#C9A84C; font-weight:600; margin-bottom:0.8rem;">📋 전체 도서 목록</div>', unsafe_allow_html=True)
df_show = df[["title", "author", "translator", "publisher", "location", "isbn", "added_at"]].copy()
df_show.columns = ["제목", "저자", "번역가", "출판사", "위치", "ISBN", "추가일"]
df_show["추가일"] = df_show["추가일"].dt.strftime("%Y-%m-%d")
st.dataframe(df_show, use_container_width=True, hide_index=True)
