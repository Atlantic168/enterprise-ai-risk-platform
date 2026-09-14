from datetime import date

from app.db import get_connection


def count_incidents(
    department: str,
    severity: str,
    start_date: date,
    end_date: date,
) -> int:
    query = """
        SELECT COUNT(*)
        FROM incidents
        WHERE department = %s
          AND severity = %s
          AND incident_date BETWEEN %s AND %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    department,
                    severity,
                    start_date,
                    end_date,
                ),
            )

            result = cursor.fetchone()

    return result[0]