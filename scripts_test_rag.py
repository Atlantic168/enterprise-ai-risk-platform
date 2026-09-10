from app.rag import build_index, load_documents, search


documents = load_documents()

print(f"Loaded documents: {len(documents)}")

model, index = build_index(documents)

query = "What are the requirements for monitoring AI models after deployment?"

results = search(
    query,
    model,
    index,
    documents,
    top_k=3,
)

print("\nTop results:\n")

for result in results:
    print("=" * 80)
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']:.4f}")
    print(result["text"])