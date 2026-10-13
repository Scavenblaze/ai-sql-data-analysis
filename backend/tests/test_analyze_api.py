import pytest
from fastapi.testclient import TestClient

import main
from services.sql_validator import SQLValidationError
from services.query_executor import QueryExecutionError


client = TestClient(main.app)


@pytest.fixture
def mock_analysis(monkeypatch):
    schema = {
        "schema": "analytics",
        "tables": {
            "customers": {
                "columns": [
                    {"name": "country", "type": "text"}
                ]
            }
        },
    }

    rows = [
        {"country": "India", "customer_count": 120},
        {"country": "USA", "customer_count": 100},
    ]

    monkeypatch.setattr(
        main, "get_database_schema", lambda: schema
    )
    monkeypatch.setattr(
        main,
        "generate_sql",
        lambda question, schema: (
            "SELECT country, COUNT(*) AS customer_count "
            "FROM analytics.customers "
            "GROUP BY country LIMIT 100"
        ),
    )
    monkeypatch.setattr(
        main,
        "validate_sql",
        lambda sql, schema: sql,
    )
    monkeypatch.setattr(
        main, "execute_query", lambda sql: rows
    )
    monkeypatch.setattr(
        main,
        "analyze_result",
        lambda question, rows: {"chart": None},
    )
    monkeypatch.setattr(
        main,
        "summarize_result",
        lambda question, rows: (
            "India has 120 customers, while the USA has 100."
        ),
    )


def test_analyze_success(mock_analysis):
    response = client.post(
        "/analyze",
        json={
            "question": "Which country has the most customers?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "Which country has the most customers?"
    )
    assert data["answer"] == (
        "India has 120 customers, while the USA has 100."
    )
    assert data["row_count"] == 2
    assert len(data["rows"]) == 2
    assert data["chart"] is None
    assert "SELECT" in data["sql"].upper()


def test_analyze_rejects_invalid_sql(
    mock_analysis, monkeypatch
):
    def reject_sql(sql, schema):
        raise SQLValidationError("Only SELECT queries are allowed")

    monkeypatch.setattr(main, "validate_sql", reject_sql)

    response = client.post(
        "/analyze",
        json={"question": "Delete all customers"},
    )

    assert response.status_code == 400
    assert "SQL validation failed" in response.json()["detail"]


def test_analyze_handles_execution_error(
    mock_analysis, monkeypatch
):
    def fail_execution(sql):
        raise QueryExecutionError("Query execution failed")

    monkeypatch.setattr(main, "execute_query", fail_execution)

    response = client.post(
        "/analyze",
        json={"question": "Which country has the most customers?"},
    )

    assert response.status_code == 500
    assert "Query execution failed" in response.json()["detail"]


def test_analyze_requires_question():
    response = client.post("/analyze", json={})

    assert response.status_code == 422