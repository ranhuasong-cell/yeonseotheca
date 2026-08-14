import streamlit as st
from components.styles import apply_global_styles, sidebar_logo, page_header
from utils.database import search_books, get_all_books, update_book, delete_book, init_db

st.set_page_config(page_title="검색 | 연서테카", page_icon="🔍", layout="wide")
init_db()
apply_global_styles()
sidebar_logo()

page_header("도서 검색", "제목 · 저자 · 번역가 · 출판사 · 키워드 · 메모 통합 검색")

# 검색 바
col_q, col_loc = st.columns([3, 1])
with col_q:
    query = st.text_input("검색어", placeholder="책 제목, 저자, 키워드 등 무엇이든 입력하세요", label_visibility="collapsed")
with col_loc:
    all_books = get_all_books()
    locations = sorted(set(b["location"] for b in all_books if b.get("location")))
    loc_options = ["전체 위치"] + locations
    loc_filter = st.selectbox("위치 필터", loc_options, label_visibility="collapsed")

selected_location = "" if loc_filter == "전체 위치" else loc_filter
results = search_books(query, selected_location)

st.markdown(f'<div style="color:#8A9BB5; font-size:0.85rem; margin-bottom:1rem;">검색 결과: <span style="color:#C9A84C; font-weight:600;">{len(results)}권</span></div>', unsafe_allow_html=True)

if not results:
    st.markdown('<div style="color:#8A9BB5; text-align:center; padding:3rem;">검색 결과가 없습니다.</div>', unsafe_allow_html=True)
else:
    for book in results:
        with st.container():
            col_cover, col_info, col_actions = st.columns([1, 6, 2])

            with col_cover:
                if book.get("cover_url"):
                    st.image(book["cover_url"], width=70)
                else:
                    st.markdown('<div style="width:70px;height:95px;background:#152B50;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#C9A84C;font-size:1.8rem;">📖</div>', unsafe_allow_html=True)

            with col_info:
                loc_html = f'<span class="book-location">📍 {book["location"]}</span>' if book.get("location") else ""
                kw_html = ""
                if book.get("keywords"):
                    tags = [f'<span style="background:#1A3355;color:#8A9BB5;border-radius:4px;padding:0.1rem 0.4rem;font-size:0.75rem;margin-right:0.3rem;">{k.strip()}</span>' for k in book["keywords"].split(",") if k.strip()]
                    kw_html = " ".join(tags)

                st.markdown(f"""
                <div class="book-card">
                    <div class="book-title">{book['title']}</div>
                    <div class="book-meta">
                        저자: {book.get('author') or '—'} &nbsp;|&nbsp;
                        번역: {book.get('translator') or '—'} &nbsp;|&nbsp;
                        출판사: {book.get('publisher') or '—'}
                        {f"<br>ISBN: {book['isbn']}" if book.get('isbn') else ""}
                        {f"<br>메모: {book['memo']}" if book.get('memo') else ""}
                    </div>
                    <div style="margin-top:0.5rem;">{loc_html} &nbsp; {kw_html}</div>
                </div>""", unsafe_allow_html=True)

            with col_actions:
                st.markdown("<div style='padding-top:0.5rem;'>", unsafe_allow_html=True)

                if st.button("✏️ 수정", key=f"edit_{book['id']}"):
                    st.session_state[f"editing_{book['id']}"] = True

                if st.button("🗑️ 삭제", key=f"del_{book['id']}"):
                    st.session_state[f"confirm_del_{book['id']}"] = True

                if st.session_state.get(f"confirm_del_{book['id']}"):
                    st.warning("정말 삭제할까요?")
                    if st.button("예, 삭제", key=f"yes_del_{book['id']}"):
                        delete_book(book["id"])
                        st.success("삭제됐습니다.")
                        st.session_state[f"confirm_del_{book['id']}"] = False
                        st.rerun()
                    if st.button("취소", key=f"no_del_{book['id']}"):
                        st.session_state[f"confirm_del_{book['id']}"] = False

                st.markdown("</div>", unsafe_allow_html=True)

        # 수정 폼
        if st.session_state.get(f"editing_{book['id']}"):
            with st.form(key=f"form_{book['id']}"):
                st.markdown(f"**'{book['title']}' 정보 수정**")
                fc1, fc2 = st.columns(2)
                with fc1:
                    new_title = st.text_input("제목", value=book.get("title", ""))
                    new_author = st.text_input("저자", value=book.get("author", ""))
                    new_translator = st.text_input("번역가", value=book.get("translator", ""))
                with fc2:
                    new_publisher = st.text_input("출판사", value=book.get("publisher", ""))
                    new_location = st.text_input("위치", value=book.get("location", ""))
                    new_keywords = st.text_input("키워드", value=book.get("keywords", ""))
                new_memo = st.text_area("메모", value=book.get("memo", ""))

                save_col, cancel_col = st.columns(2)
                with save_col:
                    submitted = st.form_submit_button("💾 저장")
                with cancel_col:
                    cancelled = st.form_submit_button("취소")

                if submitted:
                    update_book(book["id"], title=new_title, author=new_author,
                                translator=new_translator, publisher=new_publisher,
                                location=new_location, keywords=new_keywords, memo=new_memo)
                    st.session_state[f"editing_{book['id']}"] = False
                    st.success("수정 완료!")
                    st.rerun()
                if cancelled:
                    st.session_state[f"editing_{book['id']}"] = False
                    st.rerun()

        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
