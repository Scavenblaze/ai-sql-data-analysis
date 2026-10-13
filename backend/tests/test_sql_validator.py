import pytest

from services.sql_validator import (
    validate_sql,
    SQLValidationError,
)


@pytest.fixture
def schema():
    return {
        "schema": "analytics",
        "tables": {
            "customers": {
                "columns": [
                    {"name": "id", "type": "bigint"},
                    {"name": "name", "type": "text"},
                    {"name": "country", "type": "text"},
                ]
            }
        },
    }


def test_accepts_valid_select(schema):
    sql = """
        SELECT country
        FROM analytics.customers
        LIMIT 100;
    """

    result = validate_sql(sql, schema)

    assert "SELECT" in result.upper()


def test_accepts_maximum_limit(schema):
    sql = """
        SELECT *
        FROM analytics.customers
        LIMIT 500;
    """

    validate_sql(sql, schema)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM analytics.customers LIMIT 501;",
        "SELECT * FROM analytics.customers;",
        "SELECT * FROM public.customers LIMIT 10;",
        "SELECT nonexistent FROM analytics.customers LIMIT 10;",
        "DELETE FROM analytics.customers;",
        "SELECT * FROM analytics.customers LIMIT -1;",
        """
        SELECT * FROM analytics.customers LIMIT 10;
        SELECT * FROM analytics.customers LIMIT 10;
        """,
    ],
)
def test_rejects_invalid_sql(sql, schema):
    with pytest.raises(SQLValidationError):
        validate_sql(sql, schema)