import time
from threading import Lock
#import logging

from database import pool


SCHEMA_NAME = "analytics"
SCHEMA_CACHE_TTL_SECONDS = 300

_schema_cache = None
_schema_cache_time = 0.0
_schema_cache_lock = Lock()

#logger = logging.getLogger(__name__) #for testing schema cache 


def get_database_schema():
    global _schema_cache, _schema_cache_time

    with _schema_cache_lock:
        current_time = time.monotonic()

        if (_schema_cache is not None and current_time - _schema_cache_time < SCHEMA_CACHE_TTL_SECONDS):
            #logger.info("Schema Cache HIT") #Retrieved Cached
            return _schema_cache
        
        #logger.info("Schema Cache MISS - fetching from database") #No cache log

        schema = _fetch_database_schema()

        _schema_cache = schema
        _schema_cache_time = time.monotonic()
        
        #logger.info("Schema fetched and cached successfully") #schema has been cached

        return _schema_cache


def _fetch_database_schema():
    columns_query = """
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,

            CASE
                WHEN pk.column_name IS NOT NULL
                THEN TRUE
                ELSE FALSE
            END AS is_primary_key

        FROM information_schema.columns c

        LEFT JOIN (
            SELECT
                kcu.table_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
                AND tc.table_name = kcu.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = %s
        ) pk
            ON c.table_name = pk.table_name
            AND c.column_name = pk.column_name

        WHERE c.table_schema = %s

        ORDER BY c.table_name, c.ordinal_position;
    """

    foreign_keys_query = """
        SELECT
            kcu.table_name,
            kcu.column_name,
            ccu.table_name AS referenced_table,
            ccu.column_name AS referenced_column

        FROM information_schema.table_constraints tc

        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema

        JOIN information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
            AND tc.table_schema = ccu.table_schema

        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = %s;
    """

    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(columns_query, (SCHEMA_NAME, SCHEMA_NAME))
            column_rows = cursor.fetchall()

            cursor.execute(foreign_keys_query,(SCHEMA_NAME,))
            foreign_key_rows = cursor.fetchall()

    schema = {
        "schema": SCHEMA_NAME,
        "tables": {},
    }

    for (table_name, column_name, data_type, is_nullable, is_primary_key) in column_rows:
        if table_name not in schema["tables"]:
            schema["tables"][table_name] = {
                "columns": [],
            }

        schema["tables"][table_name]["columns"].append({
            "name": column_name,
            "type": data_type,
            "nullable": is_nullable == "YES",
            "primary_key": is_primary_key,
        })

    for (table_name, column_name, referenced_table, referenced_column) in foreign_key_rows:
        if table_name not in schema["tables"]:
            continue

        for column in schema["tables"][table_name]["columns"]:
            if column["name"] == column_name:
                column["foreign_key"] = {
                    "table": referenced_table,
                    "column": referenced_column,
                }
                break

    return schema