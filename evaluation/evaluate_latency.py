import json
import math
import statistics
import time
import urllib.request
from pathlib import Path


API_URL = "http://127.0.0.1:8000/ask"


QUESTIONS = [
    "What must happen before a high-impact AI system is deployed?",
    "How should production AI systems be monitored?",
    "When is human oversight required?",
    "What qualities should critical business data have?",
    "How should access to sensitive data be controlled?",
    "What does least privilege mean?",
    "How should technology incidents be reported?",
    "How is incident severity assessed?",
    "What validation is required before model deployment?",
    "What should ongoing model review identify?"
]


def post_json(payload):
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    start = time.perf_counter()

    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(
            response.read().decode("utf-8")
        )

    elapsed = time.perf_counter() - start

    return elapsed, body


def percentile(values, p):
    values = sorted(values)

    index = (len(values) - 1) * p

    lower = math.floor(index)
    upper = math.ceil(index)

    if lower == upper:
        return values[lower]

    return (
        values[lower]
        + (values[upper] - values[lower])
        * (index - lower)
    )


print("Running warm-up request...")

post_json(
    {
        "question": QUESTIONS[0],
        "top_k": 3
    }
)

print("Warm-up complete.\n")


latencies = []

for i, question in enumerate(QUESTIONS, start=1):

    elapsed, response = post_json(
        {
            "question": question,
            "top_k": 3
        }
    )

    if "answer" not in response:
        raise RuntimeError(
            f"Unexpected response: {response}"
        )

    latencies.append(elapsed)

    print(f"{i:02d}. {elapsed:.3f}s")


average = statistics.mean(latencies)
median = statistics.median(latencies)
p95 = percentile(latencies, 0.95)


summary = {
    "num_requests": len(latencies),
    "average_latency_seconds": average,
    "median_latency_seconds": median,
    "p95_latency_seconds": p95
}


Path(
    "evaluation/latency_results.json"
).write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)


print("\n" + "=" * 60)
print(f"Average latency: {average:.3f}s")
print(f"Median latency:  {median:.3f}s")
print(f"P95 latency:     {p95:.3f}s")
print(f"Requests:        {len(latencies)}")
print("=" * 60)