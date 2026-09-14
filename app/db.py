import psycopg


DATABASE_URL = "postgresql://localhost/enterprise_risk"


def get_connection():
    return psycopg.connect(DATABASE_URL)