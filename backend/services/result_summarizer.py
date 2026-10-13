import json
import os

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
You are a data analysis assistant.

Your job is to answer a user's data question using the database results provided to you.

Rules:

1. Use only the provided results.
2. Do not invent or assume any values.
3. Do not generate SQL.
4. Do not mention SQL, databases, schemas, or internal processing.
5. Answer the user's question directly.
6. Be concise.
7. If multiple rows contain the same value, summarize the pattern instead of unnecessarily listing every row.
8. If the results are empty, clearly say that no matching data was found.
"""


def summarize_result(question: str, rows: list[dict]) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "results": rows,
                    },
                    default=str,
                ),
            },
        ],
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("LLM returned an empty answer")

    return answer.strip()