import chromadb
import json



client = chromadb.PersistentClient(path="./vector_db")

collection = client.get_or_create_collection(
    name="codebase"
)

with open("D:\\untitled\\Rag\\JSON\\chunks.json", "r") as f:
    chunks = json.load(f)


# collection.add(
#     ids=[c["id"] for c in chunks],
#     documents=[c["document"] for c in chunks],
#     metadatas=[c["metadata"] for c in chunks],
# )  

results = collection.query(
    query_texts=[
    "def main() -> int:"
    ],
    include=["documents", "metadatas"],
    n_results=10
)

print(results)