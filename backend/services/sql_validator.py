from sqlglot import exp, parse
from sqlglot.errors import ParseError


ALLOWED_SCHEMA = "analytics"
MAX_ROWS = 500


class SQLValidationError(Exception):
    pass


def validate_sql(sql: str, schema: dict) -> str:
    if not sql or not sql.strip():
        raise SQLValidationError("SQL query is empty")

    try:
        statements = parse(sql, read="postgres")
    except ParseError as e:
        raise SQLValidationError(f"Invalid PostgreSQL SQL: {e}") from e

    if len(statements) != 1:
        raise SQLValidationError("Only one SQL statement is allowed")

    expression = statements[0]

    if not isinstance(expression, exp.Select):
        raise SQLValidationError("Only SELECT queries are allowed")

    _validate_forbidden_operations(expression)
    _validate_tables(expression, schema)
    _validate_columns(expression, schema)
    _validate_limit(expression)

    return sql.strip()


def _validate_forbidden_operations(expression):
    forbidden = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Create,
        exp.Drop,
        exp.Alter,
        exp.Merge,
    )

    for node in expression.walk():
        if isinstance(node, forbidden):
            raise SQLValidationError(f"Forbidden SQL operation: {node.key}")


def _validate_tables(expression, schema):
    allowed_tables = set(schema["tables"].keys())

    tables = list(expression.find_all(exp.Table))

    if not tables:
        raise SQLValidationError("Query does not reference a table")

    for table in tables:
        table_schema = table.db
        table_name = table.name

        if table_schema != ALLOWED_SCHEMA:
            raise SQLValidationError(f"Only the '{ALLOWED_SCHEMA}' schema is allowed")

        if table_name not in allowed_tables:
            raise SQLValidationError(f"Unknown table: {table_name}")


def _validate_columns(expression, schema):
    table_columns = {
        table_name: {
            column["name"]
            for column in table_info["columns"]
        }
        for table_name, table_info in schema["tables"].items()
    }

    tables = list(expression.find_all(exp.Table))

    aliases = {}

    for table in tables:
        if table.alias:
            aliases[table.alias] = table.name

    available_columns = set()

    for table in tables:
        available_columns.update(table_columns[table.name])

    select_aliases = set()

    for select_expression in expression.expressions:
        alias = select_expression.alias

        if alias:
            select_aliases.add(alias)

    for column in expression.find_all(exp.Column):

        column_name = column.name
        table_name = column.table

        # SELECT *
        # SELECT p.*
        if column_name == "*":
            continue

        # Qualified column:
        # p.name
        if table_name:

            actual_table = aliases.get(table_name, table_name)

            if actual_table not in table_columns:
                raise SQLValidationError(f"Unknown table: {table_name}")

            if column_name not in table_columns[actual_table]:
                raise SQLValidationError("Unknown column: " f"{actual_table}.{column_name}")

        # Unqualified column:
        # country
        else:

            #allow SELECT aliases such as:
            #
            # SELECT COUNT(*) AS total
            # ORDER BY total
            if column_name in select_aliases:
                continue

            if column_name not in available_columns:
                raise SQLValidationError(f"Unknown column: {column_name}")
                
def _validate_limit(expression: exp.Select) -> None:
    limit = expression.args.get("limit")

    if limit is None:
        raise SQLValidationError(f"Every query must include LIMIT {MAX_ROWS} or less")

    limit_expression = limit.expression

    if not isinstance(limit_expression, exp.Literal):
        raise SQLValidationError("LIMIT must use a constant integer")

    if not limit_expression.is_int:
        raise SQLValidationError("LIMIT must be an integer")

    limit_value = int(limit_expression.this)

    if not 1 <= limit_value <= MAX_ROWS:
        raise SQLValidationError(f"LIMIT must be between 1 and {MAX_ROWS}")     