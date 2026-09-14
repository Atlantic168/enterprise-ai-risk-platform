from datetime import date

from app.sql_tool import count_incidents


result = count_incidents(
    department="Finance",
    severity="High",
    start_date=date(2026, 1, 1),
    end_date=date(2026, 3, 31),
)

print("Finance Q1 2026 high-severity incidents:", result)