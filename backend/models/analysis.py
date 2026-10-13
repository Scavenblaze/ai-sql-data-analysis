from typing import Any

from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    question: str


class ChartSpec(BaseModel):
    type: str
    x: str
    y: str
    title: str


class AnalysisResponse(BaseModel):
    question: str
    answer: str
    sql: str
    rows: list[dict[str, Any]]
    row_count: int
    chart: ChartSpec | None