from fastapi import FastAPI
from pydantic import BaseModel

from app.rag import build_index, load_documents, search
from app.llm import generate_answer

app = FastAPI(
    title="Enterprise AI Risk Analytics Platform",
    version="0.2.0",
)


documents = load_documents()
model, index = build_index(documents)


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class AskRequest(BaseModel):
    question: str
    top_k: int = 3

@app.get("/")
def root():
    return {
        "message": "Enterprise AI Risk Analytics Platform is running."
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "documents_loaded": len(documents),
    }


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

@app.post("/ask")
def ask_question(request: AskRequest):

    results = search(
        request.question,
        model,
        index,
        documents,
        top_k=request.top_k
    )

    answer = generate_answer(
        question=request.question,
        context=results
    )

    return {
        "question": request.question,
        "answer": answer,
        "sources": results
    }