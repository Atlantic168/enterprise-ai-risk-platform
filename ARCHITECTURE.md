# Architecture — Enterprise AI Risk Analytics Platform

## 1. System Purpose

The platform is a lightweight enterprise AI prototype designed to demonstrate how an AI application can combine:

- unstructured enterprise policy knowledge,
- structured technology-risk data,
- LLM inference,
- backend APIs,
- database access,
- containerized deployment, and
- measurable evaluation.

The architecture deliberately separates retrieval, LLM inference, database access, and the API layer so that each component can be developed and evaluated independently.

## 2. Current Architecture

```text
                                  +----------------------+
                                  |      API Client      |
                                  |  Browser / curl / UI |
                                  +----------+-----------+
                                             |
                                             v
                                  +----------------------+
                                  |    FastAPI Backend   |
                                  |                      |
                                  |  /health             |
                                  |  /search             |
                                  |  /ask                |
                                  |  /analytics/incidents|
                                  +----+-------------+---+
                                       |             |
                         +-------------+             +----------------+
                         |                                              |
                         v                                              v
              +----------------------+                       +----------------------+
              |   RAG Retrieval      |                       |      SQL Tool        |
              |                      |                       |                      |
              | document loading     |                       | controlled function  |
              | chunking              |                       | parameterized SQL    |
              | embeddings            |                       +----------+-----------+
              | FAISS similarity      |                                  |
              +----------+-----------+                                  v
                         |                                    +----------------------+
                         v                                    |     PostgreSQL       |
              +----------------------+                         |   incidents table   |
              | Policy Documents     |                         +----------------------+
              |                      |
              | AI governance        |
              | Data governance      |
              | Access control       |
              | Incident response    |
              | Model risk management|
              +----------+-----------+
                         |
                         | retrieved context
                         v
              +----------------------+
              |   HKUST GenAI API    |
              |   LLM inference      |
              +----------+-----------+
                         |
                         v
              +----------------------+
              | Answer + Sources     |
              +----------------------+
```

## 3. Component Responsibilities

### 3.1 FastAPI

`app/main.py` is the application entry point.

Responsibilities:

- expose HTTP endpoints;
- validate request input with Pydantic;
- call retrieval and database components;
- return structured JSON responses;
- provide health checks;
- log requests and processing latency;
- handle application-level errors.

### 3.2 RAG Layer

`app/rag.py` handles unstructured policy knowledge.

Pipeline:

```text
Policy documents
      |
      v
Paragraph / chunk extraction
      |
      v
Sentence Transformer embeddings
      |
      v
FAISS vector index
      |
      v
Query embedding
      |
      v
Top-k similarity search
      |
      v
Relevant policy chunks
```

The retrieval layer does not generate the final answer. It supplies evidence for the LLM layer.

### 3.3 LLM Layer

`app/llm.py` encapsulates calls to the HKUST GenAI API using the OpenAI Python SDK.

Responsibilities:

- load the API credential from the environment;
- connect to the HKUST OpenAI-compatible endpoint;
- send system instructions and user/context information;
- return the generated response text.

### 3.4 SQL Tool

`app/sql_tool.py` provides a controlled interface for structured analytics.

Example flow:

```text
Request parameters
      |
      v
count_incidents(...)
      |
      v
Parameterized SQL query
      |
      v
PostgreSQL
      |
      v
Structured result
```

The current implementation intentionally avoids unrestricted user-supplied SQL.

### 3.5 PostgreSQL

The database stores synthetic technology-risk incident records, including:

- incident date,
- category,
- severity,
- department,
- status,
- root cause,
- financial impact, and
- resolution time.

### 3.6 Docker Compose

`docker-compose.yml` defines two services:

```text
Docker Compose
|
+-- api      -> FastAPI application
|
+-- postgres -> PostgreSQL database
```

The services communicate over the Compose network. The API connects to PostgreSQL using the service name `postgres`, rather than `localhost`.

A named PostgreSQL volume preserves database data across normal container recreation.

## 4. Operational Controls

The current prototype includes several basic production-oriented controls.

### Health checks

`GET /health` verifies application availability and database connectivity.

### Request logging

The FastAPI middleware records method, path, status code, and elapsed processing time.

### Latency tracking

The API measures request processing time and exposes it through an `X-Process-Time` response header.

### Input validation

Pydantic models enforce request types and limits such as `top_k` between 1 and 10.

### Error handling

User-facing responses avoid exposing raw Python stack traces, while server logs retain exception information for debugging.

### Secret management

API credentials are stored in `.env` and excluded from Git and Docker build context.

## 5. Current API Flow: `/ask`

```text
User question
      |
      v
FastAPI /ask
      |
      v
RAG retrieval
      |
      +---- retrieve top-k policy chunks
      |
      v
Context + question
      |
      v
HKUST GenAI API
      |
      v
Generated answer
      |
      +---- sources
      |
      v
JSON response
```

The current `/ask` implementation performs retrieval first and then sends the retrieved context to the LLM.

## 6. Current API Flow: `/analytics/incidents`

```text
Structured request
      |
      v
FastAPI validation
      |
      v
Controlled SQL tool
      |
      v
Parameterized SQL
      |
      v
PostgreSQL
      |
      v
Incident count
      |
      v
JSON response
```

## 7. Evaluation Architecture

The evaluation layer is intentionally separate from the application code.

```text
                 +---------------------------+
                 |      Evaluation Suite     |
                 +-------------+-------------+
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
 Retrieval               API Latency             SQL Accuracy
 Hit@3                   Avg / Median / P95      Tool vs Direct SQL
        |
        +----------------------+----------------------+
                               |
                               v
                     Abstention Evaluation
                     Unsupported Questions
```

Current results:

| Metric | Result |
|---|---:|
| Retrieval Hit@3 | 15/15 (100.00%) |
| Average latency | 2.611 s |
| Median latency | 2.465 s |
| P95 latency | 3.583 s |
| SQL accuracy | 10/10 (100.00%) |
| Unsupported-question abstention | 5/5 (100.00%) |

These measurements are prototype-level results from small, curated datasets.

## 8. Future Architecture: LLM Tool Calling

A natural next step is to allow the LLM to decide whether a question requires unstructured retrieval, structured analytics, or both.

```text
                          User Question
                                |
                                v
                           LLM Orchestrator
                           /              \
                          /                \
                         v                  v
                      RAG Tool           SQL Tool
                         |                  |
                   Policy Docs        PostgreSQL
                         \                  /
                          \                /
                           v              v
                              Tool Results
                                   |
                                   v
                              Final LLM Answer
```

This is a planned extension, not part of the current implemented MVP.

## 9. Design Principles

### Separation of concerns

Retrieval, LLM inference, database access, and API handling are kept in separate modules.

### Controlled data access

Database access is exposed through parameterized functions rather than arbitrary SQL execution.

### Grounded generation

The RAG workflow supplies retrieved evidence to the LLM and includes source passages in the response.

### Reproducibility

Synthetic data, evaluation questions, scripts, Docker configuration, and environment setup are kept in the repository so that the project can be recreated locally.

### Measurable behavior

The project reports explicit metrics instead of relying only on qualitative claims about model performance.
