"""LangSmith 평가용 데이터셋 생성 스크립트.

RAG_DOCS_DIR의 마크다운 문서 내용을 기반으로
질문-정답 쌍을 LangSmith 데이터셋에 등록한다.
"""

import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

DATASET_NAME = "yuta-rag-eval"
DATASET_DESCRIPTION = "Yuta TIL 마크다운 문서 기반 RAG 평가 데이터셋"

# 문서 내용 기반 질문-정답 쌍
QA_PAIRS = [
    # Python 기초 (2026_05_14.md)
    {
        "inputs": {"question": "Python 리스트에서 요소를 추가하는 메서드는 무엇인가요?"},
        "outputs": {"answer": "append() 메서드를 사용하여 리스트 끝에 요소를 추가할 수 있습니다."},
    },
    {
        "inputs": {"question": "Python에서 함수를 정의하는 키워드는 무엇인가요?"},
        "outputs": {"answer": "def 키워드를 사용하여 함수를 정의합니다."},
    },
    # CLI, 모듈, 패키지 (2026_05_15.md)
    {
        "inputs": {"question": "Python에서 CLI를 만들 때 사용하는 표준 라이브러리는 무엇인가요?"},
        "outputs": {"answer": "argparse 모듈을 사용하여 CLI(Command Line Interface)를 만들 수 있습니다."},
    },
    {
        "inputs": {"question": "PyPI란 무엇인가요?"},
        "outputs": {"answer": "PyPI(Python Package Index)는 Python 패키지를 공유하고 배포하는 저장소입니다."},
    },
    {
        "inputs": {"question": "__init__.py 파일의 역할은 무엇인가요?"},
        "outputs": {"answer": "디렉토리를 Python 패키지로 인식시키는 역할을 합니다."},
    },
    # OOP, 동시성 (2026_05_16.md)
    {
        "inputs": {"question": "Python에서 데코레이터란 무엇인가요?"},
        "outputs": {"answer": "데코레이터(@)는 함수나 클래스를 수정하지 않고 기능을 추가할 수 있는 문법입니다."},
    },
    {
        "inputs": {"question": "GIL(Global Interpreter Lock)이란 무엇인가요?"},
        "outputs": {"answer": "GIL은 Python 인터프리터가 한 번에 하나의 스레드만 Python 바이트코드를 실행하도록 제한하는 잠금 메커니즘입니다."},
    },
    {
        "inputs": {"question": "I/O-bound 작업과 CPU-bound 작업의 차이는 무엇인가요?"},
        "outputs": {"answer": "I/O-bound 작업은 네트워크나 파일 입출력 대기 시간이 주요 병목이고, CPU-bound 작업은 연산 처리 자체가 병목입니다. I/O-bound는 멀티스레딩이나 비동기 처리가, CPU-bound는 멀티프로세싱이 적합합니다."},
    },
    # HTTP (http 내용정리.md, 2026_05_18.md, 2026_05_21.md)
    {
        "inputs": {"question": "HTTP 상태코드 404는 무엇을 의미하나요?"},
        "outputs": {"answer": "404는 Not Found로, 요청한 리소스를 서버에서 찾을 수 없음을 의미합니다."},
    },
    {
        "inputs": {"question": "HTTP GET과 POST 메서드의 차이는 무엇인가요?"},
        "outputs": {"answer": "GET은 리소스를 조회(읽기)할 때 사용하고, POST는 서버에 데이터를 제출하여 리소스를 생성할 때 사용합니다."},
    },
    {
        "inputs": {"question": "URL의 구성 요소에는 어떤 것들이 있나요?"},
        "outputs": {"answer": "URL은 스킴(scheme), 도메인(domain), 포트(port), 경로(path), 쿼리 파라미터(parameters)로 구성됩니다."},
    },
    {
        "inputs": {"question": "HTTP 상태코드 500은 무엇을 의미하나요?"},
        "outputs": {"answer": "500은 Internal Server Error로, 서버 내부에서 오류가 발생했음을 의미합니다."},
    },
    # 웹서버 vs 앱서버 (2026_05_20.md)
    {
        "inputs": {"question": "웹서버와 앱서버의 차이는 무엇인가요?"},
        "outputs": {"answer": "웹서버는 정적 콘텐츠(HTML, CSS, JS)를 제공하고, 앱서버는 동적 콘텐츠를 처리하며 비즈니스 로직을 실행합니다. FastAPI 같은 프레임워크는 앱서버 역할을 합니다."},
    },
    # 수학 (2026_05_23.md)
    {
        "inputs": {"question": "벡터 공간이란 무엇인가요?"},
        "outputs": {"answer": "벡터 공간은 벡터의 덧셈과 스칼라 곱셈이 정의된 수학적 구조로, 유클리드 공간이 대표적인 예입니다."},
    },
    {
        "inputs": {"question": "수학의 집합 개념은 CS의 어떤 자료구조와 대응되나요?"},
        "outputs": {"answer": "수학의 집합은 CS의 set 자료구조와 대응되며, 리스트(list), 튜플(tuple), 딕셔너리(dictionary) 등도 수학적 구조와 연관됩니다."},
    },
    # numpy, pytorch (2026_05_26.md, pytorch.md)
    {
        "inputs": {"question": "NumPy란 무엇인가요?"},
        "outputs": {"answer": "NumPy는 고성능 수학 연산과 다차원 배열(ndarray) 처리를 제공하는 Python 라이브러리입니다."},
    },
    {
        "inputs": {"question": "퍼셉트론이란 무엇인가요?"},
        "outputs": {"answer": "퍼셉트론은 인공 신경망(ANN)의 기본 단위로, 입력에 가중치를 곱하고 합산하여 이진 분류를 수행하는 모델입니다."},
    },
    # AI 에이전트 (2026_06_03.md)
    {
        "inputs": {"question": "AutoResearch란 무엇인가요?"},
        "outputs": {"answer": "AutoResearch는 자율적으로 코드를 개선하는 에이전트 루프 방법론으로, Program.md 문서로 행동 규칙을 정의하고 Git과 JSONL로 메모리를 관리합니다."},
    },
    {
        "inputs": {"question": "LLM DevOps Agent의 주요 구성 요소는 무엇인가요?"},
        "outputs": {"answer": "Preprocessor(알람 처리), IC Agent(메인 오케스트레이터), Subagent들(nx, prs, seer, env 에이전트), Summarizer(리포트 분석)로 구성됩니다."},
    },
    # 딥러닝 (2026_06_08.md)
    {
        "inputs": {"question": "BPTT(Backpropagation Through Time)란 무엇인가요?"},
        "outputs": {"answer": "BPTT는 RNN에서 시간 축을 따라 역전파를 수행하는 학습 알고리즘입니다."},
    },
    {
        "inputs": {"question": "LSTM이 기존 RNN의 어떤 문제를 해결하나요?"},
        "outputs": {"answer": "LSTM(Long Short-Term Memory)은 RNN의 장기 의존성 문제(기울기 소실)를 셀 상태와 게이트 메커니즘으로 해결합니다."},
    },
    # RAG (2026_06_15.md)
    {
        "inputs": {"question": "RAG란 무엇인가요?"},
        "outputs": {"answer": "RAG(Retrieve Augment Generate)는 외부 데이터 저장소에서 관련 문서를 검색하여 LLM 프롬프트에 삽입하고, 근거 기반 답변을 생성하는 기법입니다."},
    },
]


def main():
    client = Client()
    # 기존 데이터셋 삭제 후 재생성 (이중 중첩 데이터 정리)
    for d in client.list_datasets(dataset_name=DATASET_NAME):
        print(f"기존 데이터셋 삭제: {d.id}")
        client.delete_dataset(dataset_id=d.id)

    print(f"데이터셋 '{DATASET_NAME}' 생성 중...")
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=DATASET_DESCRIPTION,
    )

    # pair["inputs"]는 이미 {"question": "..."} 형태이므로 그대로 전달
    # pair["outputs"]는 이미 {"answer": "..."} 형태이므로 그대로 전달
    print(f"질문-정답 쌍 {len(QA_PAIRS)}개 등록 중...")
    client.create_examples(
        inputs=[pair["inputs"] for pair in QA_PAIRS],
        outputs=[pair["outputs"] for pair in QA_PAIRS],
        dataset_id=dataset.id,
    )

    print(f"완료! 데이터셋 ID: {dataset.id}")
    print(f"등록된 예시 수: {len(QA_PAIRS)}")
    print("LangSmith 대시보드에서 확인: https://smith.langchain.com")


if __name__ == "__main__":
    main()
