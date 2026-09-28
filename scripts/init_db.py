from app.db import get_connection


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS incidents (
    incident_id SERIAL PRIMARY KEY,
    incident_date DATE NOT NULL,
    category VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    department VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    root_cause VARCHAR(200),
    financial_impact NUMERIC(12, 2),
    resolution_time_hours NUMERIC(8, 2)
);
"""


with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)

print("Incidents table is ready.")