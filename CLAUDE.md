# 연서테카

책장 사진을 찍으면 Vision API로 책을 인식해서 등록하고, 검색·통계까지 관리하는 개인 서재 관리 앱입니다.

- 스택: Python + Streamlit, SQLite(`data/yeonseotheca.db`), OpenAI Vision API, 책 정보 조회(네이버/구글북스 API)
- 페이지 구조: `pages/1_📸_책_추가.py`(사진 업로드·인식·등록), `pages/2_🔍_검색.py`, `pages/3_📊_통계.py`
- 핵심 로직: `utils/database.py`(DB), `utils/vision_api.py`(책장 사진 인식), `utils/book_api.py`(책 메타데이터 조회)
- **토플앱(도담도담)과는 완전히 별개의 독립 프로젝트입니다.** 코드/DB/배포 어떤 것도 공유하지 않습니다.

## 에이전트 오케스트레이션

`.claude/agents/`에 pm, coder, qa 3개 서브에이전트가 있습니다. 프로젝트 규모가 작아서 토플앱처럼 dba/ux/debug/research까지 나누지 않았습니다.

- 여러 단계가 필요한 기능 추가/수정: `pm`에게 위임 → pm이 coder → qa 순서로 실제 호출.
- 단순 질문/조회: 필요한 에이전트를 바로 지목해서 사용.
- 무조건 위임이 능사는 아니니, 간단한 수정(오타, 스타일 한 줄)은 인라인으로 바로 처리해도 됩니다.

## 작업 규칙

- API 키(OpenAI/네이버/구글북스/구글비전)는 `.env`에서만 불러옵니다. Bash 명령어나 코드에 직접 하드코딩 금지.
- `.claude/settings.local.json`에 시크릿이 담긴 채로 커밋되려는 상황이 보이면 사용자에게 먼저 알립니다.
- `venv/`, `data/*.db`, `assets/images/uploads/`는 커밋 대상이 아닙니다(`.gitignore` 처리됨).
- 커밋 전에는 항상 `git status`로 실제 스테이징된 파일을 확인하고, 의도치 않은 파일(특히 venv, DB, 업로드 이미지)이 포함되지 않았는지 확인합니다.
