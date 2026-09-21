import logging
import time
from datetime import date

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.db import get_connection
from app.llm import generate_answer
from app.rag import build_index, load_documents, search
from app.sql_tool import count_incidents


# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("enterprise_ai")


# -------------------------------------------------------------------
# Application setup
# -------------------------------------------------------------------

app = FastAPI(
    title="Enterprise AI Risk Analytics Platform",
    version="0.4.0",
)


documents = load_documents()
model, index = build_index(documents)


# -------------------------------------------------------------------
# Request models
# -------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=10)


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=3, ge=1, le=10)


class IncidentAnalyticsRequest(BaseModel):
    department: str
    severity: str
    start_date: date
    end_date: date


# -------------------------------------------------------------------
# Request logging middleware
# -------------------------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        elapsed = time.perf_counter() - start_time

        logger.exception(
            "Unhandled error | %s %s | %.3fs",
            request.method,
            request.url.path,
            elapsed,
        )

        raise

    elapsed = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{elapsed:.4f}"

    logger.info(
        "%s %s | %s | %.3fs",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )

    return response


# -------------------------------------------------------------------
# Basic endpoints
# -------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Enterprise AI Risk Analytics Platform is running."
    }


@app.get("/health")
def health():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        return {
            "status": "ok",
            "documents_loaded": len(documents),
            "database": "ok",
        }

    except Exception:
        logger.exception("Health check failed")

        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "documents_loaded": len(documents),
                "database": "unavailable",
            },
        )


# -------------------------------------------------------------------
# RAG retrieval endpoint
# -------------------------------------------------------------------

@app.post("/search")
def search_documents(request: SearchRequest):
    results = search(
        request.query,
        model,
        index,
        documents,
        top_k=request.top_k,
    )

    return {
        "query": request.query,
        "results": results,
    }


# -------------------------------------------------------------------
# RAG + LLM question answering endpoint
# -------------------------------------------------------------------

@app.post("/ask")
def ask_question(request: AskRequest):

    try:
        results = search(
            request.question,
            model,
            index,
            documents,
            top_k=request.top_k,
        )

        answer = generate_answer(
            question=request.question,
            context=results,
        )

        return {
            "question": request.question,
            "answer": answer,
            "sources": results,
        }

    except Exception as exc:
        logger.exception("Question answering failed")

        raise HTTPException(
            status_code=500,
            detail="The AI service could not process the request.",
        ) from exc


# -------------------------------------------------------------------
# Structured incident analytics endpoint
# -------------------------------------------------------------------

@app.post("/analytics/incidents")
def incident_analytics(request: IncidentAnalyticsRequest):

    if request.end_date < request.start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date must be on or after start_date.",
        )

    try:
        count = count_incidents(
            department=request.department,
            severity=request.severity,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        return {
            "department": request.department,
            "severity": request.severity,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "incident_count": count,
        }

    except Exception as exc:
        logger.exception("Incident analytics failed")

        raise HTTPException(
            status_code=500,
            detail="The incident analytics service could not process the request.",
        ) from exc
    