# Yuta Chat Bot

LangChain + RAG 기반의 문서 질의응답 API 서버.
로컬 마크다운 문서를 벡터화하여 사용자의 질문에 근거 기반으로 답변한다.

## 기술 스택

| 분류 | 기술 |
|------|------|
| 웹 프레임워크 | FastAPI |
| LLM | Google Gemini (`gemini-2.5-flash`) |
| 임베딩 | Google `gemini-embedding-001` |
| 벡터스토어 | ChromaDB (로컬 영속 저장) |
| 체인 구성 | LangChain LCEL |
| 패키지 관리 | uv |

## 프로젝트 구조

```
Yuta_Chat_Bot/
├── main.py                  # FastAPI 앱 진입점
├── src/
│   ├── rag_controller.py    # RAG 체인 (문서 로딩 → 임베딩 → 검색 → 답변)
│   ├── rag_router.py        # POST /rag 엔드포인트
│   └── langchain_client.py  # 단순 LLM 체인 (비RAG, 독립 실행용)
├── .chroma_db/              # 벡터 인덱스 저장 디렉토리 (자동 생성)
└── pyproject.toml           # 의존성 정의
```

## 설치

```bash
# 의존성 설치
uv sync
```

| 변수 | 필수 | 설명 |
|------|------|------|
| `GOOGLE_API_KEY` | O | Google Gemini API 키 |
| `RAG_DOCS_DIR` | O | RAG 대상 마크다운 문서 폴더 경로 |
| `CHROMA_PERSIST_DIR` | X | 벡터 인덱스 저장 경로 (기본: `.chroma_db/`) |
| `GOOGLE_MODEL` | X | LLM 모델명 (기본: `gemini-2.5-flash`) |

## 서버 실행

```bash
uvicorn main:app --reload
```

## 동작 원리

```
사용자 질문
  │
  ▼
질문을 벡터로 변환 (gemini-embedding-001)
  │
  ▼
ChromaDB에서 유사한 문서 청크 3개 검색
  │
  ▼
검색된 문서 + 질문을 프롬프트에 조립
  │
  ▼
Gemini LLM이 근거 기반 답변 생성
  │
  ▼
JSON 응답 반환
```
