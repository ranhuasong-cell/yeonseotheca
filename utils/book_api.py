import os
import re
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def _normalize_queries(title: str, author: str = "", publisher: str = "") -> list:
    """GPT로 네이버 검색에 최적화된 쿼리 후보를 생성합니다."""
    prompt = (
        "책 제목과 저자 정보가 아래에 있어. 이 정보는 책 사진에서 AI가 읽은 것이라 "
        "오탈자·공백·잡음이 섞여 있을 수 있어.\n\n"
        f"제목(원본): {title}\n"
        f"저자(원본): {author}\n"
        f"출판사(원본): {publisher}\n\n"
        "네이버 책 검색에서 가장 잘 찾을 수 있도록 검색 쿼리 후보 3개를 만들어줘.\n"
        "전략:\n"
        "1. 핵심 제목만 (오탈자 교정, 불필요한 부제·권호 제거)\n"
        "2. 핵심 제목 + 저자명\n"
        "3. 핵심 제목 + 출판사명 (출판사가 있을 때만)\n\n"
        "규칙:\n"
        "- 한국 책은 한국어 제목으로\n"
        "- 쿼리는 짧고 명확하게 (10자 이내 권장)\n"
        "- JSON 배열로만 반환: [\"쿼리1\", \"쿼리2\", \"쿼리3\"]\n"
        "- 다른 설명 없이"
    )
    try:
        res = _openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        raw = res.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        queries = json.loads(raw.strip())
        if isinstance(queries, list):
            return [q for q in queries if q.strip()]
    except Exception:
        pass

    # GPT 실패 시 단순 규칙으로 후보 생성
    cleaned = re.sub(r"[^\w\s가-힣]", " ", title).strip()
    short = cleaned.split(":")[0].split("—")[0].strip()
    fallbacks = [short]
    if author:
        fallbacks.append(f"{short} {author.split(',')[0].strip()}")
    if publisher:
        fallbacks.append(f"{short} {publisher}")
    return fallbacks


def _search_naver_raw(query: str):
    """네이버 책 검색 API 단일 호출."""
    url = "https://openapi.naver.com/v1/search/book.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    try:
        res = requests.get(url, headers=headers,
                           params={"query": query, "display": 1}, timeout=5)
        res.raise_for_status()
        items = res.json().get("items", [])
        if not items:
            return None
        item = items[0]
        return {
            "title": _clean_html(item.get("title", "")),
            "author": _clean_html(item.get("author", "")),
            "publisher": item.get("publisher", ""),
            "isbn": item.get("isbn", "").split()[-1] if item.get("isbn") else "",
            "cover_url": item.get("image", ""),
            "description": _clean_html(item.get("description", "")),
            "source": "naver",
        }
    except Exception:
        return None


def search_naver_book(title: str, author: str = "", publisher: str = ""):
    """최적화된 쿼리 후보를 순차 시도해 네이버에서 책을 조회합니다."""
    queries = _normalize_queries(title, author, publisher)
    for query in queries:
        result = _search_naver_raw(query)
        if result:
            return result
    return None


def search_google_book(title: str, author: str = ""):
    """Google Books API로 책 정보를 조회합니다 (네이버 실패 시 보완)."""
    query = f"intitle:{title}"
    if author:
        query += f"+inauthor:{author}"
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "maxResults": 1, "key": GOOGLE_BOOKS_API_KEY}

    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        items = res.json().get("items", [])
        if not items:
            return None
        info = items[0].get("volumeInfo", {})
        isbn = ""
        for identifier in info.get("industryIdentifiers", []):
            if identifier.get("type") == "ISBN_13":
                isbn = identifier.get("identifier", "")
                break
        cover = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
        return {
            "title": info.get("title", ""),
            "author": ", ".join(info.get("authors", [])),
            "publisher": info.get("publisher", ""),
            "isbn": isbn,
            "cover_url": cover,
            "description": info.get("description", ""),
            "source": "google",
        }
    except Exception:
        return None


def lookup_book(title: str, author: str = "", publisher: str = "") -> dict:
    """네이버 우선(최적화 쿼리), 실패 시 Google Books로 조회합니다."""
    result = search_naver_book(title, author, publisher)
    if result:
        return result
    result = search_google_book(title, author)
    if result:
        return result
    return {
        "title": title,
        "author": author,
        "publisher": publisher,
        "isbn": "",
        "cover_url": "",
        "description": "",
        "source": "none",
    }
