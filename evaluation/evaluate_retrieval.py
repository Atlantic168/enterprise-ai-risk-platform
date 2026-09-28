import json
from pathlib import Path

from app.rag import build_index, load_documents, search


QUESTION_FILE = Path("evaluation/retrieval_questions.json")
RESULT_FILE = Path("evaluation/retrieval_results.json")


questions = json.loads(
    QUESTION_FILE.read_text(encoding="utf-8")
)

documents = load_documents()
model, index = build_index(documents)

results = []

for item in questions:
    retrieved = search(
        item["question"],
        model,
        index,
        documents,
        top_k=3,
    )

    sources = [result["source"] for result in retrieved]

    hit = item["expected_source"] in sources

    results.append(
        {
            "question": item["question"],
            "expected_source": item["expected_source"],
            "retrieved_sources": sources,
            "hit_at_3": hit,
        }
    )

    print(
        f"[{'PASS' if hit else 'FAIL'}] {item['question']}"
    )
    print(f"  Expected:  {item['expected_source']}")
    print(f"  Retrieved: {sources}")


hit_count = sum(
    result["hit_at_3"]
    for result in results
)

total = len(results)
hit_at_3 = hit_count / total

summary = {
    "hit_at_3": hit_at_3,
    "hit_count": hit_count,
    "total": total,
}

RESULT_FILE.write_text(
    json.dumps(
        {
            "summary": summary,
            "results": results,
        },
        indent=2,
    ),
    encoding="utf-8",
)

print("\n" + "=" * 60)
print(f"Retrieval Hit@3: {hit_count}/{total}")
print(f"Retrieval Hit@3 rate: {hit_at_3:.2%}")
print("=" * 60)