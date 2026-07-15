import bm25s.high_level as bm25

# Load a file (csv, json, jsonl, txt)
# For csv/jsonl, you can specify the column/key to use as document text
corpus = bm25.load("./Rag/JSON/chunks.json", document_column="document")
# Index the corpus
retriever = bm25.index(corpus)

# Search
results = retriever.search(["def main () -> int : base = app_dir()"], k=5)
for result in results[0]:
    print(result)