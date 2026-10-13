from datetime import date

from services.result_analyzer import generate_chart_spec


def test_categorical_data_uses_bar_chart():
    rows = [
        {"country": "India", "customers": 120},
        {"country": "USA", "customers": 100},
    ]

    chart = generate_chart_spec(rows)

    assert chart["type"] == "bar"
    assert chart["x"] == "country"
    assert chart["y"] == "customers"


def test_two_numeric_columns_use_scatter_chart():
    rows = [
        {"price": "100.50", "quantity": 10},
        {"price": "200.00", "quantity": 20},
    ]

    chart = generate_chart_spec(rows)

    assert chart["type"] == "scatter"
    assert chart["x"] == "price"
    assert chart["y"] == "quantity"


def test_datetime_data_uses_line_chart():
    rows = [
        {"month": date(2026, 1, 1), "revenue": 1000},
        {"month": date(2026, 2, 1), "revenue": 1500},
    ]

    chart = generate_chart_spec(rows)

    assert chart["type"] == "line"
    assert chart["x"] == "month"
    assert chart["y"] == "revenue"


def test_identifier_columns_are_ignored():
    rows = [
        {"id": 1, "name": "Laptop", "price": 1000},
        {"id": 2, "name": "Phone", "price": 500},
    ]

    chart = generate_chart_spec(rows)

    assert chart["type"] == "bar"
    assert chart["x"] == "name"
    assert chart["y"] == "price"


def test_single_row_returns_no_chart():
    assert generate_chart_spec([{"country": "India", "count": 10}]) is None


def test_empty_results_return_no_chart():
    assert generate_chart_spec([]) is None