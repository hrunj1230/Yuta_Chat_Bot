import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
#sec company_tickers_exchange data
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

if __name__ == "__main__":
    client = SecClient()
    client.fetch_company_tickers()