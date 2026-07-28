"""
Lets an agent look up claim/customer/policy data without giving it write
access. Every query goes through execution_guard.enforce_read_only first.
"""
from crewai.tools import tool
from sqlalchemy import text

from app.core.database import SessionLocal
from guardrails.execution_guard import enforce_read_only


@tool("database_lookup")
def database_lookup(sql_query: str) -> str:
    """Runs a read-only SELECT query against the insurance database and
    returns the rows as text. Only SELECT statements are allowed."""
    enforce_read_only(sql_query)

    db = SessionLocal()
    try:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        return str([dict(row._mapping) for row in rows])
    finally:
        db.close()
