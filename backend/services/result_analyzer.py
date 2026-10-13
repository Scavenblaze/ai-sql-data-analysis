from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def is_numeric(value) -> bool:
    if isinstance(value, bool) or value is None:
        return False

    if isinstance(value, (int, float, Decimal)):
        return True

    if isinstance(value, str):
        try:
            number = Decimal(value)
            return number.is_finite()
        except (InvalidOperation, ValueError):
            return False

    return False


def is_datetime(value) -> bool:
    return isinstance(value, (date, datetime))


def is_identifier_column(column: str) -> bool:
    return column.lower() == "id" or column.lower().endswith("_id")


def generate_chart_spec(rows: list[dict]) -> dict | None:
    if len(rows) < 2:
        return None

    columns = list(rows[0].keys())

    #identify columns by their actual values
    numeric_columns = []
    datetime_columns = []
    categorical_columns = []

    for column in columns:
        if is_identifier_column(column):
            continue

        values = [
            row.get(column)
            for row in rows
            if row.get(column) is not None
        ]

        if not values:
            continue

        if all(is_numeric(value) for value in values):
            numeric_columns.append(column)
        elif all(is_datetime(value) for value in values):
            datetime_columns.append(column)
        else:
            categorical_columns.append(column)

    #time-series: date/time on X, numeric measure on Y
    if datetime_columns and numeric_columns:
        x_column = datetime_columns[0]
        y_column = numeric_columns[0]

        return {
            "type": "line",
            "x": x_column,
            "y": y_column,
            "title": f"{y_column} over time",
        }

    #relationship between two numeric measures
    if len(numeric_columns) >= 2:
        x_column, y_column = numeric_columns[:2]

        return {
            "type": "scatter",
            "x": x_column,
            "y": y_column,
            "title": f"{y_column} vs {x_column}",
        }

    #compare a numeric measure across categories
    if numeric_columns and categorical_columns:
        x_column = categorical_columns[0]
        y_column = numeric_columns[0]

        return {
            "type": "bar",
            "x": x_column,
            "y": y_column,
            "title": f"{y_column} by {x_column}",
        }

    return None


def analyze_result(question: str, rows: list[dict]) -> dict:
    if not rows:
        return {
            "answer": "No results found.",
            "chart": None,
        }

    return {
        "answer": None,
        "chart": generate_chart_spec(rows),
    }