from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import open_pool, close_pool, check_database_connection

from services.result_analyzer import analyze_result
from services.llm_service import generate_sql
from services.sql_validator import validate_sql, SQLValidationError
from services.schema_service import get_database_schema
from services.query_executor import execute_query, QueryExecutionError
from services.result_summarizer import summarize_result
from models.analysis import AnalysisRequest, AnalysisResponse


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        open_pool()
        yield
    finally:
        close_pool()


app = FastAPI(
    title="AI SQL DATA ANALYSIS",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health_check():
    try:
        database_ok = check_database_connection()
    except Exception as e:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}",
        )

    if not database_ok:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database health check failed",
        )

    return {
        "status": "ok",
        "database": "connected",
    }


@app.get("/schema")
def database_schema():
    return get_database_schema()

    
@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    question = request.question
    try:
        #get current database schema
        schema = get_database_schema()

        #generate SQL
        sql = generate_sql(
            question=question,
            schema=schema
        )

        #validate the generated SQL
        validated_sql = validate_sql(
            sql=sql,
            schema=schema
        )

        #execute SQL
        rows = execute_query(validated_sql)

        #analyze results
        analysis = analyze_result(
            question=question,
            rows=rows
        )

        #summarize the results
        answer = summarize_result(
            question=question,
            rows=rows
        )

        return {
            "question": question,
            "sql": validated_sql,
            "rows": rows,
            "row_count": len(rows),
            "answer": answer,
            "chart": analysis["chart"],
        }

    except SQLValidationError as e:
        logger.exception(f"SQL Validation failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"SQL validation failed",
        )

    except QueryExecutionError as e:
        logger.exception(f"Query execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed. Please try a different question.",
        )

    except Exception as e:
        logger.exception(f"Error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during analysis.",
        )