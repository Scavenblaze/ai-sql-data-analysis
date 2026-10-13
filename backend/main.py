from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import open_pool, close_pool, check_database_connection, pool, analyst_pool

from services.result_analyzer import analyze_result
from services.llm_service import generate_sql
from services.sql_validator import validate_sql, SQLValidationError
from services.schema_service import get_database_schema
from services.query_executor import execute_query, QueryExecutionError
from services.result_summarizer import summarize_result
from models.analysis import AnalysisRequest, AnalysisResponse

#import logging
#logging.basicConfig(level=logging.INFO) #setup cache logging

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

#temp allows
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    try:
        database_ok = check_database_connection()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}",
        )

    if not database_ok:
        raise HTTPException(
            status_code=503,
            detail="Database health check failed",
        )

    return {
        "status": "ok",
        "database": "connected",
    }


@app.get("/db-test")
def database_test():
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM analytics.customers;")

                customer_count = cursor.fetchone()[0]

        return {
            "customers": customer_count,
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database query failed: {str(e)}",
        )


@app.get("/schema")
def database_schema():
    return get_database_schema()


@app.get("/generate-sql")
def generate_sql_test(question: str):
    schema = get_database_schema()

    sql = generate_sql(
        question=question,
        schema=schema,
    )

    return {
        "question": question,
        "sql": sql,
    }
    
    
@app.get("/validate-sql")
def validate_sql_test(question: str):

    schema = get_database_schema()

    sql = generate_sql(
        question=question,
        schema=schema,
    )

    try:
        validated_sql = validate_sql(
            sql=sql,
            schema=schema,
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {
        "question": question,
        "sql": validated_sql,
        "valid": True,
    }


@app.get("/execute-sql")
def execute_sql_test(question: str):

    schema = get_database_schema()

    sql = generate_sql(
        question=question,
        schema=schema,
    )

    try:
        validated_sql = validate_sql(
            sql=sql,
            schema=schema,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"SQL validation failed: {e}",
        )

    try:
        rows = execute_query(validated_sql)
    except QueryExecutionError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {
        "question": question,
        "sql": validated_sql,
        "rows": rows,
        "row_count": len(rows),
    }
    
@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    question = request.question
    try:
        #get current database schema
        schema = get_database_schema()

        #generate SQL
        sql = generate_sql(
            question=question,
            schema=schema,
        )

        #validate the generated SQL
        validated_sql = validate_sql(
            sql=sql,
            schema=schema,
        )

        #execute SQL
        rows = execute_query(validated_sql)

        #analyze results
        analysis = analyze_result(
        question=question,
        rows=rows,
        )

        #summarize the results
        answer = summarize_result(
        question=question,
        rows=rows,
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
        raise HTTPException(
            status_code=400,
            detail=f"SQL validation failed: {e}",
        )

    except QueryExecutionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {e}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )