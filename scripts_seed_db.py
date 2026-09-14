import random
from datetime import date, timedelta

from app.db import get_connection


random.seed(42)

categories = [
    "Access Control",
    "Data Leakage",
    "Cloud Security",
    "Application Security",
    "System Availability",
    "Privacy",
]

severities = ["Low", "Medium", "High", "Critical"]

departments = [
    "Finance",
    "HR",
    "Technology",
    "Operations",
    "Sales",
]

statuses = [
    "Open",
    "Investigating",
    "Resolved",
    "Closed",
]

root_causes = [
    "Configuration Error",
    "Human Error",
    "Software Defect",
    "Unauthorized Access",
    "Process Failure",
]


start_date = date(2026, 1, 1)

rows = []

for _ in range(1000):
    incident_date = start_date + timedelta(
        days=random.randint(0, 273)
    )

    severity = random.choice(severities)

    financial_impact = round(
        random.uniform(500, 50000),
        2,
    )

    resolution_time = round(
        random.uniform(1, 72),
        2,
    )

    rows.append(
        (
            incident_date,
            random.choice(categories),
            severity,
            random.choice(departments),
            random.choice(statuses),
            random.choice(root_causes),
            financial_impact,
            resolution_time,
        )
    )


insert_sql = """
INSERT INTO incidents (
    incident_date,
    category,
    severity,
    department,
    status,
    root_cause,
    financial_impact,
    resolution_time_hours
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s
);
"""


with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.executemany(insert_sql, rows)

print(f"Inserted {len(rows)} synthetic incidents.")