from langsmith.evaluation import evaluate
from rag_controller import build_chain

# === Evaluator 함수 ===
def has_keyword(run, example):
    if not run.outputs or "answer" not in run.outputs:
        return {"key": "has_first_keyword", "score": 0, "comment": "답변 없음 (target 실패)"}
    pred = run.outputs["answer"]
    keyword = example.outputs["answer"].split()[0]
    return {
        "key": "has_first_keyword",
        "score": 1 if keyword in pred else 0,
        "comment": f"기대 첫 단어 '{keyword}' 포함 여부",
    }

# === target: Example의 inputs를 받아 outputs를 돌려주는 함수 ===
def my_pipeline(inputs):
    chain = build_chain()
    return {"answer": chain.invoke(inputs["question"])}
def rag_evaluate():
    # === 평가 실행 ===
    results = evaluate(
        my_pipeline,
        data="yuta-rag-eval",
        evaluators=[has_keyword],
        experiment_prefix="v1-baseline",
    )
    print(results)
    return results


if __name__ == "__main__":
    rag_evaluate()