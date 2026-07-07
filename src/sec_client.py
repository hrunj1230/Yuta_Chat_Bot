import requests
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
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
        companies =[]
        for row in rows:
            item = dict(zip(fields, row))
            companies.append({
                "ticker": item["ticker"],
                "company_name": item["name"],
                "cik": str(item["cik"]).zfill(10), ##
                "exchange": item.get("exchange"),
                "source": "SEC",
            })

        return companies

if __name__ == "__main__":
    client = SecClient()
    tickers = client.fetch_company_tickers()
    print(f"총 {len(tickers)}개의 회사 정보를 가져왔습니다.")
    if tickers:
        print("첫 번째 회사 정보:", tickers[0])

def companies_embeddings():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    if len(vectorstore.get(limit=1)["ids"]) >0:
        print(f"chromadb use {persist_directory}")
    