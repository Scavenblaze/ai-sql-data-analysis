import os

from dotenv import load_dotenv
from psycopg_pool import ConnectionPool


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
ANALYST_DATABASE_URL = os.getenv("ANALYST_DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

if not ANALYST_DATABASE_URL:
    raise RuntimeError("ANALYST_DATABASE_URL is not set")


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    open=False,
)


analyst_pool = ConnectionPool(
    conninfo=ANALYST_DATABASE_URL,
    min_size=1,
    max_size=5,
    open=False,
)


def open_pool() -> None:
    pool.open(wait=True)
    analyst_pool.open(wait=True)


def close_pool() -> None:
    analyst_pool.close()
    pool.close()


def check_database_connection() -> bool:
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()

    return result == (1,)