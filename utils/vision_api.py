import base64
import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GOOGLE_VISION_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")

# ── Google Cloud Vision OCR ─────────────────────────────────────

def _ocr_with_google_vision(b64: str) -> str:
    """Google Cloud Vision DOCUMENT_TEXT_DETECTION으로 책등 텍스트 추출."""
    url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_KEY}"
    payload = {
        "requests": [{
            "image": {"content": b64},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
            "imageContext": {
                "languageHints": ["ko", "en"],
                # 세로·가로·역방향 글자 모두 인식
                "textDetectionParams": {"enableTextDetectionConfidenceScore": True}
            }
        }]
    }
    res = requests.post(url, json=payload, timeout=15)
    res.raise_for_status()
    data = res.json()

    full = data["responses"][0].get("fullTextAnnotation", {})
    if not full:
        return ""

    # 각 블록의 텍스트와 X 위치를 추출 → 왼쪽→오른쪽 순 정렬
    blocks = []
    for page in full.get("pages", []):
        for block in page.get("blocks", []):
            verts = block.get("boundingBox", {}).get("vertices", [])
            x = verts[0].get("x", 0) if verts else 0
            text_parts = []
            for para in block.get("paragraphs", []):
                for word in para.get("words", []):
                    symbols = "".join(s.get("text", "") for s in word.get("symbols", []))
                    text_parts.append(symbols)
            block_text = " ".join(text_parts).strip()
            if block_text:
                blocks.append((x, block_text))

    blocks.sort(key=lambda b: b[0])
    return "\n".join(t for _, t in blocks)


# ── GPT-4o mini 파싱 ────────────────────────────────────────────

def _parse_with_gpt_mini(ocr_text: str) -> list:
    """OCR로 뽑은 텍스트를 GPT-4o mini가 책 목록으로 구조화."""
    prompt = f"""아래는 책장 사진에서 OCR로 추출한 텍스트야.
책등에 있는 글자들이 왼쪽→오른쪽 순서로 줄바꿈으로 구분되어 있어.
각 줄(또는 연속된 줄)이 하나의 책에 해당해.

【작업】
1. 각 책의 제목, 저자, 출판사를 파악해.
2. 한국어 책은 한국어로, 외국어 책은 원래 언어로.
3. 저자와 출판사가 섞여 있으면 문맥으로 구분해 (예: "지음", "옮김", "저", "역" 같은 조사 참고).
4. 확신이 없으면 confidence를 low로 표시하되 반드시 포함시켜.

【절대 규칙】
- OCR 텍스트에 없는 책은 절대 만들어내지 마.
- 글자가 깨지거나 부족해도 있는 것만 기반으로 판단해.

OCR 텍스트:
---
{ocr_text}
---

반환 형식 (JSON만, 다른 설명 없이):
[{{"title":"책제목","author":"저자 또는 빈문자열","publisher":"출판사 또는 빈문자열","confidence":"high/medium/low","reason":"판단근거 한줄"}}]"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    return _parse_json(res.choices[0].message.content)


# ── GPT-4o Vision (폴백) ────────────────────────────────────────

PROMPT_VISION_FALLBACK = """너는 도서관 사서이자 출판업계 전문가야. 이 책장 사진에서 실제로 보이는 책만 식별해줘.

【절대 규칙】사진에서 실제로 확인할 수 있는 책만 포함. 추측으로 채워 넣지 마.
【순서】왼쪽 끝 → 오른쪽 끝으로 책등을 하나씩 확인해.

【글자 방향】위→아래, 아래→위, 90도 회전 등 모든 방향 인식.

【출판사 — 책등 아래쪽 집중】
로고 모양·서체·색상으로 식별:
민음사(빨간 띠), 문학동네(초록), 창비(파랑), 열린책들(흰 바탕 검정 로고),
김영사, 한길사, 사계절, 다산북스, 위즈덤하우스 등

반환 형식 (JSON만):
[{"title":"책제목","author":"저자 또는 빈문자열","publisher":"출판사 또는 빈문자열","confidence":"high/medium/low","reason":"추론근거 한줄"}]

confidence 기준:
- high: 명확히 읽힘
- medium: 일부 글자 + 시각 단서로 추론
- low: 시각 단서로만 추정"""

PROMPT_VISION_PASS2 = """이 책장 사진에서 처음 스캔에서 놓쳤을 책만 추가로 찾아줘.
【절대 규칙】없는 책 만들어내지 마. 없으면 [] 반환.
집중 대상: 얇은 책 / 가장자리 책 / 색이 비슷해 경계가 불분명한 책
반환 형식 (JSON만):
[{"title":"책제목","author":"저자 또는 빈문자열","publisher":"출판사 또는 빈문자열","confidence":"high/medium/low","reason":"추론근거 한줄"}]"""


def _call_vision_gpt4o(b64: str, prompt: str) -> list:
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        ]}],
        max_tokens=3000,
    )
    return _parse_json(res.choices[0].message.content)


# ── 공통 유틸 ───────────────────────────────────────────────────

def _parse_json(raw: str) -> list:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []


def _deduplicate(books: list) -> tuple:
    """신뢰도 기준으로 확인/불확실 분리 후 중복 제거."""
    seen_confirmed, seen_uncertain = {}, {}
    confirmed, uncertain = [], []

    for book in books:
        key = book.get("title", "").strip().lower().replace(" ", "")
        if not key:
            continue
        conf = book.get("confidence", "low")
        if conf in ("high", "medium"):
            if key not in seen_confirmed:
                seen_confirmed[key] = True
                confirmed.append(book)
        else:
            if key not in seen_confirmed and key not in seen_uncertain:
                seen_uncertain[key] = True
                book["_uncertain"] = True
                uncertain.append(book)

    return confirmed, uncertain


# ── 메인 진입점 ─────────────────────────────────────────────────

def extract_books_from_image(image_file) -> tuple:
    """
    책장 사진에서 책 목록 추출.
    Google Vision 키가 있으면 OCR+GPT-mini, 없으면 GPT-4o Vision 사용.
    반환: (confirmed_list, uncertain_list, method_used)
    """
    b64 = base64.b64encode(image_file.read()).decode("utf-8")

    if GOOGLE_VISION_KEY:
        # ── OCR + GPT-4o mini 파이프라인 ──
        try:
            ocr_text = _ocr_with_google_vision(b64)
            if ocr_text.strip():
                raw_books = _parse_with_gpt_mini(ocr_text)
                confirmed, uncertain = _deduplicate(raw_books)
                return confirmed, uncertain, "ocr+gpt-mini"
        except Exception as e:
            pass  # Vision API 실패 시 폴백

    # ── GPT-4o Vision 폴백 (2회 스캔) ──
    pass1 = _call_vision_gpt4o(b64, PROMPT_VISION_FALLBACK)
    pass2 = [b for b in _call_vision_gpt4o(b64, PROMPT_VISION_PASS2)
             if b.get("confidence") in ("high", "medium")]
    all_books = pass1 + pass2
    confirmed, uncertain = _deduplicate(all_books)
    return confirmed, uncertain, "gpt4o-vision"
