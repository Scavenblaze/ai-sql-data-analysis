import os
import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set")


client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


MODEL = "dots-studio/dots-3-note-preview:free"


SYSTEM_PROMPT = """
You are a PostgreSQL SQL generator.

Your job is to convert a user's natural-language data question
into a single PostgreSQL SELECT query.

Rules:

1. Generate only read-only SQL.
2. Only use tables and columns provided in the database schema.
3. Every table reference MUST use the fully qualified form:
   analytics.<table_name>
4. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, REVOKE, or other data/schema modification statements.
5. Do not use information outside the provided schema.
6. Use explicit JOIN conditions.
7. Do not guess column names.
8. Return exactly one SQL query.
9. Do not wrap the SQL in markdown code fences.
10. Do not include explanations.
11. Every query must include a LIMIT clause.
12. The LIMIT must be a positive integer no greater than 500.
"""

# removes markdown code if the llm generates markdown anyways
def clean_sql(sql: str) -> str:
    sql = sql.strip()

    if sql.startswith("```sql"):
        sql = sql[len("```sql"):].strip()

    elif sql.startswith("```"):
        sql = sql[len("```"):].strip()

    if sql.endswith("```"):
        sql = sql[:-3].strip()

    return sql

def filter_schema(question: str, schema: dict) -> dict:
    question_words = set(question.lower().replace("-", " ").split())

    #literal keywords, if no match then defaults to all... improve this later
    keywords = {
        "customers": {
            "customer", "customers", "country", "countries",
        },
        "orders": {
            "order", "orders", "monthly", "revenue",
        },
        "order_items": {
            "quantity", "ordered", "items",
        },
        "products": {
            "product", "products", "price", "category",
        },
        "payments": {
            "payment", "payments", "paid", "revenue",
        },
    }

    relevant_tables = {
        table_name for table_name, terms in keywords.items()
        if question_words & terms and table_name in schema["tables"]
    }

    #if the question is ambiguous or no keywords match, retain the full schema for correctness.
    if not relevant_tables:
        return schema

    #include direct dependencies only when needed by the selected tables.
    for table_name in list(relevant_tables):
        for column in schema["tables"][table_name]["columns"]:
            foreign_key = column.get("foreign_key")

            if not foreign_key:
                continue

            referenced_table = foreign_key["table"]

            #add the referenced table only if the question indicates that it is relevant.
            if (referenced_table in schema["tables"] and question_words & keywords.get(referenced_table, set())):
                relevant_tables.add(referenced_table)

    return {
        "schema": schema["schema"],
        "tables": {
            table_name: schema["tables"][table_name]
            for table_name in sorted(relevant_tables)
        },
    }


def generate_sql(question: str, schema: dict) -> str:
    relevant_schema = filter_schema(question, schema)

    schema_text = json.dumps(relevant_schema, separators=(",", ":"),)

    user_prompt = f"""
        Database schema:

        {schema_text}

        User question:

        {question}

        Generate the PostgreSQL query.
        """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content

    if not sql:
        raise RuntimeError("LLM returned an empty response")

    return clean_sql(sql)