import requests
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_codex_oauth import ChatCodexOAuth

load_dotenv()
SEC_COMPANY_TICKERS_EXCHANGE_URL = (
        "https://www.sec.gov/files/company_tickers_exchange.json"
)
#{"fields":["cik","name","ticker","exchange"],"data":[[1045810,"NVIDIA CORP","NVDA","Nasdaq"],[1652044,"Alphabet Inc.","GOOGL","Nasdaq"]...

class SecClient:
    def __init__(self):
        self.headers = {
            "User-Agent": os.getenv("User-Agent"),
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov",
        }
    def fetch_company_tickers(self) -> list[dict]:
        response = requests.get(
            SEC_COMPANY_TICKERS_EXCHANGE_URL,
            headers=self.headers,
            timeout=15,
        )
        response.raise_for_status() ##
        payload = response.json()
        fields = payload["fields"]
        rows = payload["data"]
        tickers =[]
        
        for row in rows:
            item = dict(zip(fields, row))
            tickers.append({
                "ticker": item["ticker"],
                "company_name": item["name"],
                "cik": str(item["cik"]).zfill(10), ##
                "exchange": item.get("exchange"),
                "source": "SEC",
            })
        file_path = os.getenv("SEC_COMPANY_TICKERS_EXCHANGE_PATH")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tickers, f, ensure_ascii=False, indent=2)
        print(f"[download] {len(tickers)}개 티커 저장 완료 -> {file_path.readlines()}")

SYSTEM_PROMPT = """\
너는 미국 주식 종목의 한국어 별명 사전을 만드는 어시스턴트다.
입력으로 (ticker, 영문 회사명) 목록을 받으면, 각 종목마다 다음 JSON 스키마로만 응답한다.
 
[
  {
    "ticker": "NVDA",
    "korean_name": "엔비디아",
    "aliases": ["엔비디아", "엔비"],
    "confidence": "high"
  },
  ...
]
 
규칙:
- korean_name: 한국에서 통용되는 공식/표준 한글 표기 (없으면 영문명을 한글로 음차)
- aliases: korean_name을 포함해서 한국 투자자 커뮤니티에서 실제로 쓰이는 별명/줄임말들 (모르면 korean_name 하나만)
- confidence: "high" - 대중적으로 잘 알려진 별명이 확실함 / "low" - 잘 모르거나 추측성 음차뿐임
- 절대로 별명을 지어내지 마라. 모르면 confidence를 "low"로 하고 aliases는 korean_name 음차 하나만 넣어라.
- 반드시 입력받은 개수만큼, 순서 그대로 출력해라.
- JSON 배열 외의 다른 텍스트(설명, 마크다운 코드블록 등)는 절대 출력하지 마라.
"""

def _set_call_batch(batch: list[dict]) -> list[dict]:
    user_content = json.dumps(
        [{"ticker":b["ticker"], "title": b["title"]} for b in batch],
        ensure_ascii=False,
    )
    client = ChatCodexOAuth(
        model="gpt-4o",  # ChatGPT 계정에서 지원되는 모델로 변경
        temperature=0.3,
        system_prompt_mode="strict",  # 시스템 프롬프트 drift 방지
    )
    response = client.messages.create(
        model="gpt-4o",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user","content":user_content}],
    )
    # 혹시 모델이 코드블록으로 감싸서 응답하면 제거
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}\n원본 응답: {text[:500]}")
    
    if len(parsed) != len(batch):
        print(f"  [경고] 요청 {len(batch)}건 vs 응답 {len(parsed)}건 - 개수 불일치")
    return parsed

# def generate_aliases(limit: int,resume: bool =True) -> None:
#     tickers = json.loads(TICK)








if __name__ == "__main__":
    client = SecClient()
    client.fetch_company_tickers()