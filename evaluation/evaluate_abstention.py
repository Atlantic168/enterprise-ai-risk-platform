import json
import urllib.request
from pathlib import Path


API_URL = "http://127.0.0.1:8000/ask"


QUESTIONS = [
    "What is the organization's AI budget for 2027?",
    "Who is the current CEO of the organization?",
    "Which cloud provider does the organization use?",
    "How many employees completed AI governance training last year?",
    "What was the total financial impact of incidents in 2025?"
]


def ask(question):

    payload = json.dumps(
        {
            "question": question,
            "top_k": 3
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=60
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


results = []


for i, question in enumerate(QUESTIONS, start=1):

    response = ask(question)

    print("\n" + "=" * 80)
    print(f"Question {i}:")
    print(question)

    print("\nModel answer:")
    print(response["answer"])

    print(
        "\nDid the model correctly abstain "
        "without inventing unsupported information?"
    )

    while True:

        choice = input(
            "Enter y for YES or n for NO: "
        ).strip().lower()

        if choice in {"y", "n"}:
            break

    correctly_abstained = choice == "y"

    results.append(
        {
            "question": question,
            "answer": response["answer"],
            "correctly_abstained": correctly_abstained
        }
    )


correct = sum(
    item["correctly_abstained"]
    for item in results
)

total = len(results)
rate = correct / total


summary = {
    "correct_abstentions": correct,
    "total_questions": total,
    "abstention_rate": rate
}


Path(
    "evaluation/abstention_results.json"
).write_text(
    json.dumps(
        {
            "summary": summary,
            "results": results
        },
        indent=2
    ),
    encoding="utf-8"
)


print("\n" + "=" * 60)
print(
    f"Correct abstentions: {correct}/{total}"
)
print(
    f"Abstention rate: {rate:.2%}"
)
print("=" * 60)