import streamlit as st


def apply_global_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;500&display=swap');

    /* ── 전역 기본 ── */
    html, body, [class*="css"], .stApp {
        font-family: 'Noto Serif KR', serif;
        background-color: #0F1829 !important;
        color: #F5F0E8;
    }

    /* ── 메인 컨텐츠 영역 ── */
    .main .block-container {
        padding: 2.5rem 3rem 3rem;
        max-width: 1100px;
    }

    /* ── 사이드바 ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080F1C 0%, #0F1829 60%, #0A1220 100%) !important;
        border-right: 1px solid rgba(201,168,76,0.2);
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] li {
        color: #D4C9B0 !important;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.9rem;
    }
    section[data-testid="stSidebar"] a:hover {
        color: #C9A84C !important;
    }

    /* ── 페이지 제목 ── */
    .page-header {
        border-left: 3px solid #C9A84C;
        padding-left: 1rem;
        margin-bottom: 0.3rem;
    }
    .gold-title {
        font-family: 'Noto Serif KR', serif;
        color: #C9A84C;
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        line-height: 1.2;
        margin: 0;
    }
    .gold-subtitle {
        color: #7A8FA8;
        font-size: 0.85rem;
        font-family: 'Noto Sans KR', sans-serif;
        margin-top: 0.4rem;
        margin-bottom: 2rem;
        letter-spacing: 0.02em;
    }

    /* ── 구분선 ── */
    .gold-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent);
        margin: 1.8rem 0;
    }

    /* ── 카드 (책) ── */
    .book-card {
        background: rgba(15, 32, 64, 0.6);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(201,168,76,0.25);
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.9rem;
        transition: border-color 0.25s, box-shadow 0.25s;
    }
    .book-card:hover {
        border-color: rgba(201,168,76,0.6);
        box-shadow: 0 4px 24px rgba(201,168,76,0.08);
    }
    .book-title {
        font-family: 'Noto Serif KR', serif;
        color: #F5F0E8;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
        letter-spacing: 0.02em;
    }
    .book-meta {
        color: #7A8FA8;
        font-size: 0.8rem;
        font-family: 'Noto Sans KR', sans-serif;
        line-height: 1.7;
    }
    .book-location {
        display: inline-block;
        background: rgba(201,168,76,0.1);
        border: 1px solid rgba(201,168,76,0.35);
        color: #C9A84C;
        border-radius: 4px;
        padding: 0.15rem 0.6rem;
        font-size: 0.75rem;
        font-family: 'Noto Sans KR', sans-serif;
        letter-spacing: 0.03em;
        margin-top: 0.5rem;
    }

    /* ── 통계 카드 ── */
    .stat-card {
        background: rgba(15, 32, 64, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(201,168,76,0.25);
        border-radius: 12px;
        padding: 1.8rem 1.2rem;
        text-align: center;
        transition: border-color 0.25s, box-shadow 0.25s;
    }
    .stat-card:hover {
        border-color: rgba(201,168,76,0.5);
        box-shadow: 0 4px 20px rgba(201,168,76,0.07);
    }
    .stat-number {
        font-family: 'Noto Serif KR', serif;
        color: #C9A84C;
        font-size: 2.8rem;
        font-weight: 700;
        line-height: 1;
        letter-spacing: -0.01em;
    }
    .stat-label {
        color: #7A8FA8;
        font-size: 0.8rem;
        font-family: 'Noto Sans KR', sans-serif;
        margin-top: 0.6rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* ── 버튼 — 골드 아웃라인, 호버 시 채움 ── */
    .stButton > button {
        background: transparent !important;
        color: #C9A84C !important;
        border: 1px solid rgba(201,168,76,0.6) !important;
        border-radius: 6px !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 1.4rem !important;
        letter-spacing: 0.04em;
        transition: background 0.2s, color 0.2s, box-shadow 0.2s !important;
    }
    .stButton > button:hover {
        background: #C9A84C !important;
        color: #0F1829 !important;
        border-color: #C9A84C !important;
        box-shadow: 0 0 16px rgba(201,168,76,0.3) !important;
    }
    .stButton > button:active {
        background: #A8873D !important;
        color: #0F1829 !important;
    }

    /* ── 입력창 ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(8, 15, 28, 0.8) !important;
        border: 1px solid rgba(201,168,76,0.25) !important;
        border-radius: 6px !important;
        color: #F5F0E8 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        font-size: 0.88rem !important;
        transition: border-color 0.2s !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(201,168,76,0.6) !important;
        box-shadow: 0 0 0 2px rgba(201,168,76,0.1) !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #4A5A70 !important;
    }

    /* ── 셀렉트박스 ── */
    .stSelectbox > div > div {
        background-color: rgba(8, 15, 28, 0.8) !important;
        border: 1px solid rgba(201,168,76,0.25) !important;
        border-radius: 6px !important;
        color: #F5F0E8 !important;
    }

    /* ── 탭 ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid rgba(201,168,76,0.2);
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #7A8FA8 !important;
        border: none !important;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.88rem;
        padding: 0.6rem 1.4rem;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #C9A84C !important;
        border-bottom: 2px solid #C9A84C !important;
        font-weight: 600 !important;
    }

    /* ── 파일 업로더 ── */
    [data-testid="stFileUploader"] {
        background: rgba(8,15,28,0.5);
        border: 1.5px dashed rgba(201,168,76,0.3);
        border-radius: 10px;
        padding: 1.5rem;
        transition: border-color 0.2s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(201,168,76,0.6);
    }
    [data-testid="stFileUploader"] * {
        color: #7A8FA8 !important;
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* ── 익스팬더 ── */
    [data-testid="stExpander"] {
        background: rgba(15,32,64,0.4) !important;
        border: 1px solid rgba(201,168,76,0.2) !important;
        border-radius: 8px !important;
        margin-bottom: 0.6rem;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(201,168,76,0.4) !important;
    }
    [data-testid="stExpander"] summary {
        color: #D4C9B0 !important;
        font-family: 'Noto Serif KR', serif;
        font-size: 0.95rem;
    }

    /* ── 성공/에러/경고 알림 ── */
    [data-testid="stAlert"] {
        border-radius: 8px;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.88rem;
    }
    div[data-testid="stAlert"][kind="success"],
    .stSuccess {
        background: rgba(201,168,76,0.08) !important;
        border-left: 3px solid #C9A84C !important;
        color: #D4C9B0 !important;
    }
    div[data-testid="stAlert"][kind="error"] {
        background: rgba(180,60,60,0.12) !important;
        border-left: 3px solid #B44040 !important;
    }
    div[data-testid="stAlert"][kind="warning"] {
        background: rgba(180,130,40,0.12) !important;
        border-left: 3px solid #B48228 !important;
    }
    div[data-testid="stAlert"][kind="info"] {
        background: rgba(40,80,150,0.2) !important;
        border-left: 3px solid #4A7ABF !important;
    }

    /* ── 데이터테이블 ── */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(201,168,76,0.2);
        border-radius: 8px;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] th {
        background: rgba(201,168,76,0.1) !important;
        color: #C9A84C !important;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
    }
    [data-testid="stDataFrame"] td {
        color: #D4C9B0 !important;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.82rem;
    }

    /* ── 스피너 ── */
    .stSpinner > div {
        border-top-color: #C9A84C !important;
    }

    /* ── 캡션/라벨 ── */
    .stCaption, [data-testid="stCaptionContainer"] p {
        color: #4A5A70 !important;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.78rem;
    }
    label, .stTextInput label, .stTextArea label,
    .stSelectbox label, .stFileUploader label {
        color: #7A8FA8 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.02em;
    }

    /* ── 스크롤바 ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0F1829; }
    ::-webkit-scrollbar-thumb { background: rgba(201,168,76,0.3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(201,168,76,0.6); }

    /* ── 폼 ── */
    [data-testid="stForm"] {
        background: rgba(8,15,28,0.4);
        border: 1px solid rgba(201,168,76,0.2);
        border-radius: 10px;
        padding: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)


def sidebar_logo():
    st.sidebar.markdown("""
    <div style="padding: 2rem 1rem 1.2rem; text-align:center;">
        <div style="
            font-family:'Noto Serif KR',serif;
            color:#C9A84C;
            font-size:1.5rem;
            font-weight:700;
            letter-spacing:0.15em;
            line-height:1.3;
        ">연서테카</div>
        <div style="
            color:rgba(201,168,76,0.4);
            font-size:0.65rem;
            font-family:'Noto Sans KR',sans-serif;
            letter-spacing:0.2em;
            margin-top:0.3rem;
            text-transform:uppercase;
        ">Smart Home Library</div>
    </div>
    <div style="
        height:1px;
        background:linear-gradient(90deg,transparent,rgba(201,168,76,0.35),transparent);
        margin: 0 1rem 1rem;
    "></div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="page-header">
        <div class="gold-title">{title}</div>
    </div>
    {"" if not subtitle else f'<div class="gold-subtitle">{subtitle}</div>'}
    """, unsafe_allow_html=True)
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
