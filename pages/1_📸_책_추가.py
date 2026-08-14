import streamlit as st
from components.styles import apply_global_styles, sidebar_logo, page_header
from utils.vision_api import extract_books_from_image
from utils.book_api import lookup_book
from utils.database import add_book, init_db

st.set_page_config(page_title="책 추가 | 연서테카", page_icon="📸", layout="wide")
init_db()
apply_global_styles()
sidebar_logo()

page_header("책 추가", "책장 사진을 업로드하면 AI가 자동으로 인식합니다")

tab1, tab2 = st.tabs(["📷 사진으로 추가", "✏️ 직접 입력"])

# ── 탭1: 사진 업로드 ──────────────────────────────────────────────
with tab1:
    uploaded = st.file_uploader(
        "책장 사진을 업로드하세요 (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        help="책 등이 잘 보이는 사진일수록 인식률이 높아요"
    )

    if uploaded:
        # 새 사진이 업로드되면 이전 인식 결과 초기화
        file_id = f"{uploaded.name}_{uploaded.size}"
        if st.session_state.get("_last_file_id") != file_id:
            st.session_state["_last_file_id"] = file_id
            st.session_state["detected_books"] = []
            st.session_state["enriched_books"] = []

        st.image(uploaded, caption="업로드된 사진", use_container_width=True)
        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

        if st.button("🔍 AI로 책 자동 인식", use_container_width=True):
            import os
            has_vision = bool(os.getenv("GOOGLE_VISION_API_KEY", "").strip())
            spinner_msg = ("📷 OCR 텍스트 추출 중... (Google Vision + GPT-mini)"
                           if has_vision else "🤖 AI가 책을 스캔하는 중... (20~40초 소요)")
            with st.spinner(spinner_msg):
                uploaded.seek(0)
                confirmed, uncertain, method = extract_books_from_image(uploaded)

            total = len(confirmed) + len(uncertain)
            if total == 0:
                st.error("책을 인식하지 못했어요. 책 등이 더 잘 보이는 사진으로 다시 시도해보세요.")
            else:
                method_label = {"ocr+gpt-mini": "📷 OCR + GPT", "gpt4o-vision": "🤖 GPT-4o Vision"}.get(method, method)
                msg = f"✅ {len(confirmed)}권 인식 완료"
                if uncertain:
                    msg += f" · 불확실 {len(uncertain)}권"
                msg += f"  —  {method_label}"
                st.success(msg)
                st.session_state["detected_books"] = confirmed + [dict(b, _uncertain=True) for b in uncertain]
                st.session_state["enriched_books"] = []

        if st.session_state.get("detected_books"):
            detected = st.session_state["detected_books"]

            if not st.session_state.get("enriched_books"):
                with st.spinner("네이버에서 책 정보를 조회하는 중..."):
                    enriched = []
                    for b in detected:
                        info = lookup_book(b.get("title", ""), b.get("author", ""), b.get("publisher", ""))
                        info["_original_title"] = b.get("title", "")
                        info["_original_author"] = b.get("author", "")
                        info["confidence"] = b.get("confidence", "")
                        info["reason"] = b.get("reason", "")
                        # 네이버에서 못 찾은 경우 AI가 인식한 출판사를 대신 사용
                        if not info.get("publisher") and b.get("publisher"):
                            info["publisher"] = b.get("publisher", "")
                        enriched.append(info)
                    st.session_state["enriched_books"] = enriched

            enriched = st.session_state["enriched_books"]

            confirmed = [b for b in enriched if not b.get("_uncertain")]
            uncertain = [b for b in enriched if b.get("_uncertain")]

            st.markdown(f"### 인식된 책 목록 — 확인됨 {len(confirmed)}권" +
                        (f" · 불확실 {len(uncertain)}권" if uncertain else ""))

            # 일괄 위치 설정
            st.markdown('<div style="background:#0F2040;border:1px solid #C9A84C66;border-radius:10px;padding:1rem 1.2rem 0.5rem;margin-bottom:1.2rem;">', unsafe_allow_html=True)
            bulk_col1, bulk_col2 = st.columns([3, 1])
            with bulk_col1:
                bulk_location = st.text_input(
                    "📍 이 사진의 책 위치 일괄 설정",
                    placeholder="예: 라운지-1-3   (입력하면 아래 모든 책에 자동 적용)",
                    key="bulk_location"
                )
            with bulk_col2:
                st.markdown("<div style='margin-top:1.8rem;'>", unsafe_allow_html=True)
                if st.button("전체 저장 💾", use_container_width=True):
                    saved, skipped = 0, 0
                    for i, book in enumerate(confirmed):
                        title_val = st.session_state.get(f"title_{i}", book.get("title", ""))
                        if not title_val:
                            skipped += 1
                            continue
                        add_book(
                            title=title_val,
                            author=st.session_state.get(f"author_{i}", book.get("author", "")),
                            translator=st.session_state.get(f"trans_{i}", ""),
                            publisher=st.session_state.get(f"pub_{i}", book.get("publisher", "")),
                            isbn=st.session_state.get(f"isbn_{i}", book.get("isbn", "")),
                            cover_url=book.get("cover_url", ""),
                            location=st.session_state.get(f"loc_{i}", "") or bulk_location,
                            keywords=st.session_state.get(f"kw_{i}", ""),
                            memo=st.session_state.get(f"memo_{i}", ""),
                        )
                        saved += 1
                    st.success(f"✅ {saved}권 저장 완료!" + (f" ({skipped}권 제목 없어 건너뜀)" if skipped else ""))
                    st.session_state["detected_books"] = []
                    st.session_state["enriched_books"] = []
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.caption("위치를 개별 변경하려면 각 책 칸에서 직접 입력하세요. 비워두면 위의 일괄 위치가 적용됩니다.")

            # 불확실한 책 섹션
            if uncertain:
                st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
                with st.expander(f"⚠️ 불확실한 책 {len(uncertain)}권 — AI가 확신하지 못한 결과 (클릭해서 확인/제거)"):
                    st.caption("아래 책들은 AI 신뢰도가 낮습니다. 맞는 책만 직접 확인 후 개별 저장하고, 나머지는 제거하세요. 전체 저장에는 포함되지 않습니다.")
                    for j, book in enumerate(uncertain):
                        i = len(confirmed) + j
                        ucol1, ucol2 = st.columns([5, 1])
                        with ucol1:
                            reason = book.get("reason", "")
                            st.markdown(f'<div style="background:#1A1A2E;border:1px solid #FF6B6B44;border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.5rem;">'
                                        f'<span style="color:#FF9999;font-weight:600;">🔴 {book.get("title","제목 불명")}</span>'
                                        f'<span style="color:#8A9BB5;font-size:0.82rem;"> · {book.get("author","")}</span>'
                                        + (f'<br><span style="color:#666;font-size:0.78rem;">💡 {reason}</span>' if reason else "") +
                                        '</div>', unsafe_allow_html=True)
                        with ucol2:
                            if st.button("🗑️", key=f"rm_u_{i}"):
                                st.session_state["enriched_books"].pop(i)
                                st.rerun()
                            if st.button("💾", key=f"sv_u_{i}", help="이 책만 저장"):
                                add_book(title=book.get("title",""), author=book.get("author",""),
                                         publisher=book.get("publisher",""),
                                         cover_url=book.get("cover_url",""),
                                         location=st.session_state.get("bulk_location",""))
                                st.success(f"저장됨: {book.get('title','')}")

            if confirmed:
                st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

            for i, book in enumerate(confirmed):
                with st.expander(f"📖 {book.get('title', '제목 없음')}", expanded=True):
                    col_cover, col_info, col_del = st.columns([1, 4, 1])
                    with col_del:
                        st.markdown("<div style='margin-top:0.3rem;'>", unsafe_allow_html=True)
                        if st.button("🗑️ 제거", key=f"remove_{i}", help="목록에서 제거 (저장되지 않음)"):
                            st.session_state["enriched_books"].pop(i)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    with col_cover:
                        if book.get("cover_url"):
                            st.image(book["cover_url"], width=90)
                        else:
                            st.markdown('<div style="width:90px;height:120px;background:#152B50;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#C9A84C;font-size:2rem;">📖</div>', unsafe_allow_html=True)
                        conf = book.get("confidence", "")
                        conf_label = {"high": "🟢 선명", "medium": "🟡 흐릿", "low": "🔴 불분명"}.get(conf, "")
                        if conf_label:
                            st.caption(f"사진: {conf_label}")
                        source_label = {"naver": "📗 네이버", "google": "📘 구글", "none": "❌ 미조회"}.get(book.get("source", "none"), "")
                        st.caption(f"조회: {source_label}")
                        if book.get("reason"):
                            st.caption(f"💡 {book['reason']}")

                    with col_info:
                        r1c1, r1c2 = st.columns(2)
                        with r1c1:
                            title = st.text_input("제목", value=book.get("title", ""), key=f"title_{i}")
                        with r1c2:
                            author = st.text_input("저자", value=book.get("author", ""), key=f"author_{i}")
                        r2c1, r2c2 = st.columns(2)
                        with r2c1:
                            translator = st.text_input("번역가", value=book.get("translator", ""), key=f"trans_{i}")
                        with r2c2:
                            publisher = st.text_input("출판사", value=book.get("publisher", ""), key=f"pub_{i}")
                        r3c1, r3c2 = st.columns(2)
                        with r3c1:
                            isbn = st.text_input("ISBN", value=book.get("isbn", ""), key=f"isbn_{i}")
                        with r3c2:
                            location = st.text_input("위치 개별 설정", value="", key=f"loc_{i}", placeholder="비워두면 일괄 위치 적용")
                        keywords = st.text_input("키워드 (쉼표로 구분)", value="", key=f"kw_{i}", placeholder="소설, 한국문학, 부커상")
                        memo = st.text_area("메모", value="", key=f"memo_{i}", height=80)

                        if st.button(f"💾 이 책만 저장", key=f"save_{i}"):
                            add_book(
                                title=title, author=author, translator=translator,
                                publisher=publisher, isbn=isbn,
                                cover_url=book.get("cover_url", ""),
                                location=location or bulk_location,
                                keywords=keywords, memo=memo
                            )
                            st.success(f"✅ '{title}' 저장 완료!")

# ── 탭2: 직접 입력 ───────────────────────────────────────────────
with tab2:
    st.markdown("#### 책 정보 직접 입력")

    c1, c2 = st.columns(2)
    with c1:
        m_title = st.text_input("제목 *", placeholder="책 제목을 입력하세요")
    with c2:
        m_author = st.text_input("저자", placeholder="저자명")

    if m_title and st.button("🔍 네이버에서 정보 자동 조회"):
        with st.spinner("조회 중..."):
            info = lookup_book(m_title, m_author)
        if info.get("source") != "none":
            st.success(f"✅ 정보를 찾았습니다! ({info.get('source','').upper()})")
            st.session_state["manual_info"] = info
        else:
            st.warning("자동 조회 결과가 없습니다. 직접 입력해주세요.")
            st.session_state["manual_info"] = {"title": m_title, "author": m_author}

    info = st.session_state.get("manual_info", {})

    c3, c4 = st.columns(2)
    with c3:
        m_translator = st.text_input("번역가", value=info.get("translator", ""))
        m_isbn = st.text_input("ISBN", value=info.get("isbn", ""))
        m_location = st.text_input("위치 *", placeholder="라운지-1-3")
    with c4:
        m_publisher = st.text_input("출판사", value=info.get("publisher", ""))
        m_cover = st.text_input("표지 이미지 URL", value=info.get("cover_url", ""))
        m_keywords = st.text_input("키워드 (쉼표 구분)", placeholder="소설, 추천")

    m_memo = st.text_area("메모", height=80)

    if info.get("cover_url"):
        st.image(info["cover_url"], width=80)

    if st.button("💾 책 저장", use_container_width=True):
        if not m_title:
            st.error("제목은 필수입니다.")
        else:
            add_book(
                title=m_title, author=m_author, translator=m_translator,
                publisher=m_publisher, isbn=m_isbn,
                cover_url=m_cover, location=m_location,
                keywords=m_keywords, memo=m_memo
            )
            st.success(f"✅ '{m_title}' 저장 완료!")
            st.session_state["manual_info"] = {}
