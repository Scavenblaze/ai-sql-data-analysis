import logging

from database import analyst_pool


QUERY_TIMEOUT_MS = 5000
MAX_ROWS = 500

logger = logging.getLogger(__name__)


class QueryExecutionError(Exception):
    pass


def execute_query(sql: str) -> list[dict]:
    try:
        with analyst_pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SET LOCAL statement_timeout = {QUERY_TIMEOUT_MS}")

                cursor.execute(sql)

                #fetch one extra row to detect a result-limit violation
                rows = cursor.fetchmany(MAX_ROWS + 1)

                if len(rows) > MAX_ROWS:
                    raise QueryExecutionError(f"Query exceeded the maximum of {MAX_ROWS} rows")

                columns = [description.name for description in cursor.description]

                return [dict(zip(columns, row)) for row in rows]

    except QueryExecutionError:
        raise

    except Exception as e:
        logger.exception("Query execution failed")

        raise QueryExecutionError("Query execution failed. Check server logs for details.") from e