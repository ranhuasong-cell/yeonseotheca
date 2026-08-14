import streamlit as st
from components.styles import apply_global_styles, sidebar_logo, page_header
from utils.database import get_book_by_id, update_book, delete_book, init_db

st.set_page_config(page_title="책 상세 | 연서테카", page_icon="📖", layout="wide")
init_db()
apply_global_styles()
sidebar_logo()

# session_state에서 book_id를 받는 방식 (검색 페이지에서 switch_page로 넘어올 때)
if "detail_book_id" in st.session_state:
    raw_id = st.session_state["detail_book_id"]
else:
    raw_id = st.query_params.get("book_id")

if not raw_id:
    page_header("책 상세")
    st.info("표시할 책이 없습니다. 검색 페이지에서 '📖 상세' 버튼을 눌러 주세요.")
    st.stop()

try:
    book_id = int(raw_id)
except (ValueError, TypeError):
    page_header("책 상세")
    st.error("유효하지 않은 book_id입니다.")
    st.stop()

book = get_book_by_id(book_id)
if book is None:
    page_header("책 상세")
    st.error("해당 책을 찾을 수 없습니다.")
    st.stop()

page_header(book["title"], "책 상세 정보")

# ── 상단: 표지 + 메타데이터 ────────────────────────────────────────────────
col_cover, col_meta = st.columns([1, 3])

with col_cover:
    if book.get("cover_url"):
        st.image(book["cover_url"], width=160)
    else:
        st.markdown(
            '<div style="width:160px;height:220px;background:#152B50;border-radius:8px;'
            'display:flex;align-items:center;justify-content:center;'
            'color:#C9A84C;font-size:3rem;border:1px solid rgba(201,168,76,0.25);">📖</div>',
            unsafe_allow_html=True,
        )

with col_meta:
    status = book.get("status") or "읽고싶음"
    status_color = {"읽음": "#4CAF7D", "읽는중": "#C9A84C", "읽고싶음": "#4A7ABF"}.get(status, "#4A7ABF")
    status_badge = (
        f'<span style="background:{status_color}22;color:{status_color};'
        f'border:1px solid {status_color}66;border-radius:12px;'
        f'padding:0.2rem 0.8rem;font-size:0.82rem;font-family:\'Noto Sans KR\',sans-serif;">'
        f'{status}</span>'
    )

    rating = book.get("rating")
    if rating:
        stars = "★" * int(rating) + "☆" * (5 - int(rating))
        rating_html = f'<span style="color:#C9A84C;font-size:1rem;margin-left:0.8rem;">{stars}</span>'
    else:
        rating_html = '<span style="color:#4A5A70;font-size:0.82rem;margin-left:0.8rem;">미평가</span>'

    st.markdown(
        f'<div style="margin-bottom:0.8rem;">{status_badge}{rating_html}</div>',
        unsafe_allow_html=True,
    )

    def meta_row(label, value):
        if not value:
            return ""
        return (
            f'<div style="margin-bottom:0.4rem;">'
            f'<span style="color:#4A5A70;font-size:0.78rem;font-family:\'Noto Sans KR\',sans-serif;">{label}</span>'
            f'<span style="color:#D4C9B0;font-size:0.9rem;font-family:\'Noto Sans KR\',sans-serif;margin-left:0.6rem;">{value}</span>'
            f'</div>'
        )

    st.markdown(
        meta_row("저자", book.get("author") or "—")
        + meta_row("번역가", book.get("translator") or "")
        + meta_row("출판사", book.get("publisher") or "")
        + meta_row("ISBN", book.get("isbn") or "")
        + meta_row("위치", book.get("location") or ""),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

# ── 한줄 리뷰 ────────────────────────────────────────────────────────────────
if book.get("review"):
    st.markdown(
        f'<div style="background:rgba(15,32,64,0.6);border-left:3px solid #C9A84C;'
        f'border-radius:0 8px 8px 0;padding:0.8rem 1.2rem;margin-bottom:1rem;">'
        f'<span style="color:#7A8FA8;font-size:0.78rem;font-family:\'Noto Sans KR\',sans-serif;">한줄 리뷰</span><br>'
        f'<span style="color:#F5F0E8;font-style:italic;">&ldquo;{book["review"]}&rdquo;</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── 키워드 태그 ───────────────────────────────────────────────────────────────
if book.get("keywords"):
    tags = [k.strip() for k in book["keywords"].split(",") if k.strip()]
    if tags:
        tags_html = " ".join(
            f'<span style="background:#1A3355;color:#8A9BB5;border:1px solid rgba(138,155,181,0.3);'
            f'border-radius:4px;padding:0.2rem 0.6rem;font-size:0.78rem;'
            f'font-family:\'Noto Sans KR\',sans-serif;margin-right:0.4rem;">{t}</span>'
            for t in tags
        )
        st.markdown(
            f'<div style="margin-bottom:1rem;">'
            f'<span style="color:#4A5A70;font-size:0.78rem;font-family:\'Noto Sans KR\',sans-serif;">키워드&nbsp;&nbsp;</span>'
            f'{tags_html}</div>',
            unsafe_allow_html=True,
        )

# ── 메모 ──────────────────────────────────────────────────────────────────────
if book.get("memo"):
    st.markdown(
        '<span style="color:#7A8FA8;font-size:0.82rem;font-family:\'Noto Sans KR\',sans-serif;">메모</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="background:rgba(8,15,28,0.5);border:1px solid rgba(201,168,76,0.2);'
        f'border-radius:8px;padding:0.9rem 1.1rem;color:#D4C9B0;'
        f'font-size:0.88rem;font-family:\'Noto Sans KR\',sans-serif;line-height:1.7;">'
        f'{book["memo"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

# ── 추가일 / 수정일 ──────────────────────────────────────────────────────────
st.markdown(
    f'<div style="color:#4A5A70;font-size:0.75rem;font-family:\'Noto Sans KR\',sans-serif;margin-bottom:1.5rem;">'
    f'추가일: {book.get("added_at", "—")}&nbsp;&nbsp;|&nbsp;&nbsp;'
    f'수정일: {book.get("updated_at", "—")}'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

# ── 인라인 수정 폼 ───────────────────────────────────────────────────────────
with st.expander("✏️ 정보 수정"):
    with st.form(key=f"detail_edit_form_{book_id}"):
        ec1, ec2 = st.columns(2)
        with ec1:
            new_title = st.text_input("제목", value=book.get("title", ""))
            new_author = st.text_input("저자", value=book.get("author") or "")
            new_translator = st.text_input("번역가", value=book.get("translator") or "")
            new_isbn = st.text_input("ISBN", value=book.get("isbn") or "")
        with ec2:
            new_publisher = st.text_input("출판사", value=book.get("publisher") or "")
            new_location = st.text_input("위치", value=book.get("location") or "")
            new_keywords = st.text_input("키워드 (쉼표 구분)", value=book.get("keywords") or "")
            new_cover_url = st.text_input("표지 이미지 URL", value=book.get("cover_url") or "")

        new_memo = st.text_area("메모", value=book.get("memo") or "", height=100)

        er1, er2, er3 = st.columns(3)
        with er1:
            status_options = ["읽고싶음", "읽는중", "읽음"]
            current_status = book.get("status") or "읽고싶음"
            status_idx = status_options.index(current_status) if current_status in status_options else 0
            new_status = st.selectbox("독서 상태", status_options, index=status_idx)
        with er2:
            rating_options = [None, 1, 2, 3, 4, 5]
            rating_labels = ["미평가", "★ 1", "★★ 2", "★★★ 3", "★★★★ 4", "★★★★★ 5"]
            current_rating = book.get("rating")
            rating_idx = rating_options.index(current_rating) if current_rating in rating_options else 0
            new_rating_label = st.selectbox("별점", rating_labels, index=rating_idx)
            new_rating = rating_options[rating_labels.index(new_rating_label)]
        with er3:
            new_review = st.text_area("한줄 리뷰", value=book.get("review") or "", height=80)

        save_col, _ = st.columns([1, 3])
        with save_col:
            submitted = st.form_submit_button("💾 저장")

        if submitted:
            update_book(
                book_id,
                title=new_title,
                author=new_author,
                translator=new_translator,
                publisher=new_publisher,
                isbn=new_isbn,
                cover_url=new_cover_url,
                location=new_location,
                keywords=new_keywords,
                memo=new_memo,
                status=new_status,
                rating=new_rating,
                review=new_review,
            )
            st.success("수정이 완료됐습니다.")
            st.rerun()

# ── 삭제 ──────────────────────────────────────────────────────────────────────
st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

if st.button("🗑️ 이 책 삭제"):
    st.session_state["confirm_delete_detail"] = True

if st.session_state.get("confirm_delete_detail"):
    st.warning(f"'{book['title']}' 을(를) 정말 삭제할까요? 이 작업은 되돌릴 수 없습니다.")
    dc1, dc2 = st.columns([1, 5])
    with dc1:
        if st.button("예, 삭제합니다"):
            delete_book(book_id)
            st.session_state.pop("confirm_delete_detail", None)
            st.session_state.pop("detail_book_id", None)
            st.success("삭제됐습니다. 검색 페이지로 이동해 주세요.")
            st.switch_page("pages/2_🔍_검색.py")
    with dc2:
        if st.button("취소"):
            st.session_state["confirm_delete_detail"] = False
            st.rerun()
