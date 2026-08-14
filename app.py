import streamlit as st
from utils.database import init_db
from components.styles import apply_global_styles, sidebar_logo, page_header

st.set_page_config(
    page_title="연서테카",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
apply_global_styles()
sidebar_logo()

page_header("연서테카", "왼쪽 메뉴에서 원하는 기능을 선택하세요")

from utils.database import get_stats, get_all_books
import pandas as pd

stats = get_stats()
books = get_all_books()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{stats['total']}</div>
        <div class="stat-label">전체 도서</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(stats['by_location'])}</div>
        <div class="stat-label">서재 위치</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(stats['by_publisher'])}</div>
        <div class="stat-label">출판사</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

# 읽는 중인 책 섹션 — 책이 있을 때만 표시
reading_books = [b for b in books if b.get("status") == "읽는중"]
if reading_books:
    st.markdown('<div style="color:#C9A84C; font-family:\'Noto Serif KR\',serif; font-size:1.1rem; font-weight:600; margin-bottom:1rem;">읽는 중인 책</div>', unsafe_allow_html=True)
    r_cols = st.columns(3)
    for i, book in enumerate(reading_books):
        with r_cols[i % 3]:
            cover = book.get("cover_url", "")
            cover_html = f'<img src="{cover}" style="width:60px;height:80px;object-fit:cover;border-radius:4px;margin-right:0.8rem;float:left;">' if cover else '<div style="width:60px;height:80px;background:#152B50;border-radius:4px;margin-right:0.8rem;float:left;display:flex;align-items:center;justify-content:center;color:#C9A84C;font-size:1.5rem;">📖</div>'
            location_html = f'<span class="book-location">📍 {book["location"]}</span>' if book.get("location") else ""
            st.markdown(f"""
            <div class="book-card" style="overflow:hidden;">
                {cover_html}
                <div class="book-title" style="margin-left:68px;">{book['title']} <span style="color:#C9A84C;font-size:0.8rem;">🟡 읽는중</span></div>
                <div class="book-meta" style="margin-left:68px;">
                    {book.get('author','저자 미상')}<br>
                    {book.get('publisher','')}
                </div>
                {location_html}
                <div style="clear:both;"></div>
            </div>""", unsafe_allow_html=True)
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

st.markdown('<div style="color:#C9A84C; font-family:\'Noto Serif KR\',serif; font-size:1.1rem; font-weight:600; margin-bottom:1rem;">최근 추가된 책</div>', unsafe_allow_html=True)

recent = books[:6]
if not recent:
    st.markdown('<div style="color:#8A9BB5; text-align:center; padding:2rem;">아직 등록된 책이 없습니다.<br>왼쪽 메뉴의 📸 책 추가에서 책장 사진을 업로드해보세요!</div>', unsafe_allow_html=True)
else:
    cols = st.columns(3)
    for i, book in enumerate(recent):
        with cols[i % 3]:
            cover = book.get("cover_url", "")
            cover_html = f'<img src="{cover}" style="width:60px;height:80px;object-fit:cover;border-radius:4px;margin-right:0.8rem;float:left;">' if cover else '<div style="width:60px;height:80px;background:#152B50;border-radius:4px;margin-right:0.8rem;float:left;display:flex;align-items:center;justify-content:center;color:#C9A84C;font-size:1.5rem;">📖</div>'
            location_html = f'<span class="book-location">📍 {book["location"]}</span>' if book.get("location") else ""
            st.markdown(f"""
            <div class="book-card" style="overflow:hidden;">
                {cover_html}
                <div class="book-title" style="margin-left:68px;">{book['title']}</div>
                <div class="book-meta" style="margin-left:68px;">
                    {book.get('author','저자 미상')}<br>
                    {book.get('publisher','')}
                </div>
                {location_html}
                <div style="clear:both;"></div>
            </div>""", unsafe_allow_html=True)
