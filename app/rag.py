from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


DOCUMENT_DIR = Path("data/documents")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_documents():
    documents = []

    for file_path in DOCUMENT_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]

        for paragraph in paragraphs:
            documents.append(
                {
                    "source": file_path.name,
                    "text": paragraph,
                }
            )

    return documents


def build_index(documents):
    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [document["text"] for document in documents]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return model, index


def search(query, model, index, documents, top_k=3):
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    )

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for score, index_id in zip(scores[0], indices[0]):
        if index_id == -1:
            continue

        result = documents[index_id].copy()
        result["score"] = float(score)
        results.append(result)

    return results