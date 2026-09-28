# Enterprise AI Risk Analytics Platform

A production-oriented enterprise AI prototype combining retrieval-augmented generation (RAG), LLM-powered question answering, structured technology-risk analytics, and a Docker Compose multi-service backend.

## Overview

This project explores how an enterprise AI assistant can work with both unstructured and structured information.

The platform supports two main information sources:

1. **Unstructured enterprise policy documents** for knowledge retrieval and grounded question answering.
2. **Structured technology-risk incident data** stored in PostgreSQL for analytical queries.

For document-based questions, the system uses Sentence Transformers to create text embeddings and FAISS to retrieve the most relevant policy chunks. The retrieved context is then passed to the HKUST GenAI API through the OpenAI Python SDK to generate a grounded response.

For structured questions, the platform exposes a controlled, parameterized SQL tool for querying incident data in PostgreSQL.

The application is exposed through FastAPI and can be run as a multi-service Docker Compose stack.

> **Scope:** This is a portfolio-scale, production-oriented prototype rather than a production enterprise deployment. The evaluation datasets are intentionally small and curated.

## Architecture

```text
                         User / API Client
                                |
                                v
                         FastAPI Backend
                                |
              +-----------------+-----------------+
              |                                   |
              v                                   v
          POST /ask                      /analytics/incidents
              |                                   |
              v                                   v
        RAG Retrieval                       SQL Tool
              |                                   |
        Sentence Transformers                PostgreSQL
              |                                   |
            FAISS                          Incident Data
              |
              v
       Relevant Policy Context
              |
              v
        HKUST GenAI API
              |
              v
      Grounded Answer + Sources
```

### Main components

- **FastAPI** — HTTP API layer and application entry point.
- **RAG pipeline** — loads policy documents, chunks text, generates embeddings, and performs semantic retrieval with FAISS.
- **HKUST GenAI API** — provides LLM inference through an OpenAI-compatible Python client interface.
- **PostgreSQL** — stores structured synthetic technology-risk incident data.
- **SQL tool** — performs controlled, parameterized queries instead of unrestricted SQL execution.
- **Docker Compose** — runs the API and PostgreSQL as separate services.
- **Evaluation suite** — measures retrieval quality, end-to-end latency, SQL result agreement, and unsupported-question handling.

## API Endpoints

### Health check

```text
GET /health
```

Example response:

```json
{
  "status": "ok",
  "documents_loaded": 30,
  "database": "ok"
}
```

### RAG + LLM question answering

```text
POST /ask
```

Example request:

```json
{
  "question": "How should AI systems be monitored after deployment?",
  "top_k": 3
}
```

The response contains the generated answer together with the retrieved source passages.

### Document retrieval

```text
POST /search
```

Example request:

```json
{
  "query": "What are the requirements for model monitoring?",
  "top_k": 3
}
```

### Structured incident analytics

```text
POST /analytics/incidents
```

Example request:

```json
{
  "department": "Finance",
  "severity": "High",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31"
}
```

## Evaluation Results

| Metric | Result |
|---|---:|
| Retrieval Hit@3 | **15/15 (100.00%)** |
| Average `/ask` latency | **2.611 s** |
| Median `/ask` latency | **2.465 s** |
| P95 `/ask` latency | **3.583 s** |
| SQL accuracy / agreement | **10/10 (100.00%)** |
| Unsupported-question abstention | **5/5 (100.00%)** |

### Evaluation setup

**Retrieval quality:** 15 curated questions with known expected source documents. A query counts as a hit when the expected source appears in the top three retrieved results.

**Latency:** 10 end-to-end `/ask` requests through the Dockerized FastAPI service, including retrieval and HKUST GenAI API inference.

**SQL accuracy:** 10 validation cases comparing the controlled SQL tool result with an independently executed PostgreSQL query.

**Unsupported-question handling:** 5 questions whose answers are not contained in the provided policy knowledge base. Responses were manually reviewed for correct abstention rather than unsupported factual claims.

### Interpretation

These are **prototype-level validation results**, not production-scale benchmarks. The test sets are small and curated, so the metrics should be interpreted as evidence that the implemented components behave as expected on the designed test cases.

## Project Structure

```text
enterprise-ai-risk-platform/
|
+- app/
|  +- __init__.py
|  +- db.py
|  +- llm.py
|  +- main.py
|  +- rag.py
|  +- sql_tool.py
|
+- data/
|  +- documents/
|     +- access_control_policy.txt
|     +- ai_governance_policy.txt
|     +- data_governance_policy.txt
|     +- incident_response_policy.txt
|     +- model_risk_management_policy.txt
|
+- scripts/
|  +- init_db.py
|  +- seed_db.py
|  +- test_db_connection.py
|  +- test_llm_api.py
|  +- test_llm_module.py
|  +- test_rag_retrieval.py
|  +- test_sql_tool.py
|
+- evaluation/
|  +- evaluate_abstention.py
|  +- evaluate_latency.py
|  +- evaluate_retrieval.py
|  +- evaluate_sql.py
|  +- retrieval_questions.json
|  +- retrieval_results.json
|  +- latency_results.json
|  +- sql_results.json
|  +- abstention_results.json
|  +- RESULTS.md
|
+- .dockerignore
+- .env
+- .gitignore
+- Dockerfile
+- docker-compose.yml
+- README.md
+- requirements.txt
```

> `.env` is local-only and must never be committed.

## Local Development

### Python environment

The project was developed with Python 3.14 in a project-specific virtual environment.

```bash
cd ~/Projects/enterprise-ai-risk-platform
source .venv/bin/activate
```

### Run with Docker Compose

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

Expected services:

```text
enterprise-risk-api        Up
enterprise-risk-postgres  Up (healthy)
```

Check the API:

```bash
curl http://127.0.0.1:8000/health
```

Open interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Stop services:

```bash
docker compose down
```

## Environment Variables

Create a local `.env` file containing the required credentials and database settings.

```text
HKUST_API_KEY=your_key_here
POSTGRES_USER=risk_app
POSTGRES_PASSWORD=local_dev_password
POSTGRES_DB=enterprise_risk
DATABASE_URL=postgresql://risk_app:local_dev_password@localhost:5433/enterprise_risk
```

The `.env` file is excluded by both `.gitignore` and `.dockerignore`.

## Data and Security Notes

- Incident data is synthetic and intended only for demonstration and evaluation.
- The SQL layer uses parameterized queries and a controlled function interface rather than unrestricted raw SQL execution.
- API credentials are loaded from environment variables rather than hard-coded in application source files.
- The project does not include production client data or confidential enterprise information.

## Current Limitations and Future Work

The current prototype does **not** implement automatic LLM-driven tool selection between RAG and SQL. The RAG endpoint and SQL analytics endpoint are implemented separately.

Potential extensions include:

- LLM function/tool calling for automatic RAG vs. SQL routing
- automated regression tests and CI/CD
- larger and less curated evaluation datasets
- richer observability and alerting
- production cloud deployment
- authentication and role-based access control

## Resume Summary

A concise description of the project for a resume or interview:

> Built a production-oriented enterprise AI risk analytics platform combining RAG-based policy retrieval, LLM-powered question answering, PostgreSQL-backed technology-risk analytics, FastAPI, and Docker Compose; implemented evaluation for retrieval quality, latency, SQL correctness, and unsupported-question handling.
