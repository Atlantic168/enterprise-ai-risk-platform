from datetime import date
import json
from pathlib import Path

from app.db import get_connection
from app.sql_tool import count_incidents


TEST_CASES = [
    {
        "department": "Finance",
        "severity": "High",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 3, 31),
    },
    {
        "department": "Technology",
        "severity": "Medium",
        "start_date": date(2026, 4, 1),
        "end_date": date(2026, 6, 30),
    },
    {
        "department": "HR",
        "severity": "Low",
        "start_date": date(2026, 4, 1),
        "end_date": date(2026, 6, 30),
    },
    {
        "department": "Operations",
        "severity": "Critical",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 3, 31),
    },
    {
        "department": "Sales",
        "severity": "High",
        "start_date": date(2026, 7, 1),
        "end_date": date(2026, 9, 30),
    },
    {
        "department": "Finance",
        "severity": "Medium",
        "start_date": date(2026, 4, 1),
        "end_date": date(2026, 6, 30),
    },
    {
        "department": "Technology",
        "severity": "High",
        "start_date": date(2026, 7, 1),
        "end_date": date(2026, 9, 30),
    },
    {
        "department": "HR",
        "severity": "Critical",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 3, 31),
    },
    {
        "department": "Operations",
        "severity": "Medium",
        "start_date": date(2026, 7, 1),
        "end_date": date(2026, 9, 30),
    },
    {
        "department": "Sales",
        "severity": "Low",
        "start_date": date(2026, 4, 1),
        "end_date": date(2026, 6, 30),
    }
]


DIRECT_SQL = """
SELECT COUNT(*)
FROM incidents
WHERE department = %s
  AND severity = %s
  AND incident_date BETWEEN %s AND %s;
"""


results = []

for i, case in enumerate(TEST_CASES, start=1):

    tool_result = count_incidents(
        department=case["department"],
        severity=case["severity"],
        start_date=case["start_date"],
        end_date=case["end_date"],
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                DIRECT_SQL,
                (
                    case["department"],
                    case["severity"],
                    case["start_date"],
                    case["end_date"],
                ),
            )

            direct_result = cursor.fetchone()[0]

    match = tool_result == direct_result

    results.append(
        {
            "case": i,
            "tool_result": tool_result,
            "direct_sql_result": direct_result,
            "match": match
        }
    )

    print(
        f"[{'PASS' if match else 'FAIL'}] "
        f"Case {i}: "
        f"tool={tool_result}, "
        f"direct_sql={direct_result}"
    )


correct = sum(
    result["match"]
    for result in results
)

total = len(results)
accuracy = correct / total

summary = {
    "accuracy": accuracy,
    "correct": correct,
    "total": total
}


Path(
    "evaluation/sql_results.json"
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
print(f"SQL accuracy: {correct}/{total}")
print(f"SQL accuracy rate: {accuracy:.2%}")
print("=" * 60)