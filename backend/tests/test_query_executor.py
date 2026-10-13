from unittest.mock import MagicMock, patch
from types import SimpleNamespace

import pytest

from services.query_executor import (
    execute_query,
    QueryExecutionError,
    MAX_ROWS,
)


@pytest.fixture
def mock_database():
    with patch(
        "services.query_executor.analyst_pool"
    ) as pool:
        connection = MagicMock()
        cursor = MagicMock()

        pool.connection.return_value.__enter__.return_value = connection
        connection.cursor.return_value.__enter__.return_value = cursor

        cursor.description = [
            SimpleNamespace(name="id"),
            SimpleNamespace(name="country")
        ]
        
        yield pool, cursor


def test_execute_query_returns_rows(mock_database):
    _, cursor = mock_database

    cursor.fetchmany.return_value = [
        (1, "India"),
        (2, "Japan"),
    ]

    result = execute_query(
        "SELECT id, country FROM analytics.customers LIMIT 100"
    )

    assert result == [
        {"id": 1, "country": "India"},
        {"id": 2, "country": "Japan"},
    ]


def test_execute_query_fetches_at_most_max_rows_plus_one(
    mock_database,
):
    _, cursor = mock_database
    cursor.fetchmany.return_value = [(i, "India") for i in range(MAX_ROWS + 1)]

    with pytest.raises(QueryExecutionError, match="maximum"):
        execute_query(
            "SELECT id, country FROM analytics.customers LIMIT 500"
        )

    cursor.fetchmany.assert_called_once_with(MAX_ROWS + 1)


def test_execute_query_sets_statement_timeout(mock_database):
    _, cursor = mock_database
    cursor.fetchmany.return_value = [(1, "India")]

    execute_query(
        "SELECT id, country FROM analytics.customers LIMIT 100"
    )

    first_call = cursor.execute.call_args_list[0]

    assert "statement_timeout" in first_call.args[0]


def test_execute_query_wraps_database_errors(mock_database):
    _, cursor = mock_database
    cursor.execute.side_effect = RuntimeError("internal database detail")

    with pytest.raises(
        QueryExecutionError,
        match="Check server logs",
    ):
        execute_query(
            "SELECT id, country FROM analytics.customers LIMIT 100"
        )