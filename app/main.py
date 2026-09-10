from fastapi import FastAPI

app = FastAPI(
    title="Enterprise AI Risk Analytics Platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Enterprise AI Risk Analytics Platform is running."
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }