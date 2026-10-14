from datetime import date, datetime
from decimal import Decimal


def is_numeric(value) -> bool:
    if isinstance(value, (int, float, Decimal)):
        return True

    if isinstance(value, str):
        try:
            Decimal(value)
            return True
        except Exception:
            return False

    return False


def is_datetime(value) -> bool:
    return isinstance(value, (date, datetime))

def is_identifier_column(column: str) -> bool:
    return column == "id" or column.endswith("_id")


def generate_chart_spec(rows: list[dict]) -> dict | None:
    if len(rows) < 2:
        return None

    columns = list(rows[0].keys())

    numeric_columns = []

    for column in columns:
        if is_identifier_column(column):
            continue
        
        values = [row[column] for row in rows if row[column] is not None]

        if values and all(is_numeric(value) for value in values):
            numeric_columns.append(column)

    #two or more numeric columns → scatter chart
    if len(numeric_columns) >= 2:
        return {
            "type": "scatter",
            "x": numeric_columns[0],
            "y": numeric_columns[1],
            "title": f"{numeric_columns[1]} vs {numeric_columns[0]}",
        }

    #one categorical column + one numeric column
    if len(numeric_columns) == 1:
        numeric_column = numeric_columns[0]

        categorical_columns = [
            column
            for column in columns
            if column != numeric_column
            and not all(
                is_numeric(row[column])
                for row in rows
                if row[column] is not None
            )
        ]

        if categorical_columns:
            return {
                "type": "bar",
                "x": categorical_columns[0],
                "y": numeric_column,
                "title": f"{numeric_column} by {categorical_columns[0]}",
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