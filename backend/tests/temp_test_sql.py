from services.sql_validator import (
    validate_sql,
    SQLValidationError,
)

# Minimal schema for testing the validator
schema = {
    "tables": {
        "customers": {
            "columns": [
                {"name": "id"},
                {"name": "name"},
                {"name": "country"},
            ]
        }
    }
}

test_queries = [
    (
        "Valid query",
        "SELECT * FROM analytics.customers LIMIT 100;",
    ),
    (
        "Maximum allowed limit",
        "SELECT * FROM analytics.customers LIMIT 500;",
    ),
    (
        "Limit too high",
        "SELECT * FROM analytics.customers LIMIT 501;",
    ),
    (
        "Missing limit",
        "SELECT * FROM analytics.customers;",
    ),
    (
        "Unknown table",
        "SELECT * FROM analytics.orders LIMIT 10;",
    ),
    (
        "Wrong schema",
        "SELECT * FROM public.customers LIMIT 10;",
    ),
    (
        "DELETE statement",
        "DELETE FROM analytics.customers;",
    ),
    (
        "Unknown column",
        "SELECT nonexistent FROM analytics.customers LIMIT 10;",
    ),
]

for name, sql in test_queries:
    try:
        validate_sql(sql, schema)
        print(f"[PASS] {name}: Accepted")
    except SQLValidationError as error:
        print(f"[PASS] {name}: Rejected - {error}")
    except Exception as error:
        print(f"[ERROR] {name}: Unexpected error - {error}")