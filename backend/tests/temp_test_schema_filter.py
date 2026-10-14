from database import open_pool, close_pool
from services.schema_service import get_database_schema
from services.llm_service import filter_schema


def main():
    open_pool()

    try:
        schema = get_database_schema()

        questions = [
            "Which country has the most customers?",
            "Which product was ordered the most?",
            "Show payment methods and payment status",
        ]

        for question in questions:
            filtered = filter_schema(question, schema)

            print(f"\nQuestion: {question}")
            print("Tables:", list(filtered["tables"].keys()))

    finally:
        close_pool()


if __name__ == "__main__":
    main()