from fastapi import FastAPI
from pydantic import BaseModel

from app.rag import build_index, load_documents, search


app = FastAPI(
    title="Enterprise AI Risk Analytics Platform",
    version="0.2.0",
)


documents = load_documents()
model, index = build_index(documents)


class SearchRequest(BaseModel):
    query: str
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