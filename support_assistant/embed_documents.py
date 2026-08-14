import os

import chromadb
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "zepto_policy"


def chunk_text(text, chunk_size=500):
    """Split text into sentence-aware chunks."""

    sentences = text.replace("\n", " ").split(". ")

    chunks = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if len(current) + len(sentence) + 2 <= chunk_size:
            current += sentence + ". "
        else:
            if current:
                chunks.append(current.strip())

            current = sentence + ". "

    if current:
        chunks.append(current.strip())

    return chunks


def embed_documents():
    """Process all policy documents and store embeddings in ChromaDB."""

    docs_dir = os.path.join(os.path.dirname(__file__), "docs")
    chroma_dir = os.path.join(os.path.dirname(__file__), "chroma_db")

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=chroma_dir)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        }
    )

    ids = []
    documents = []
    metadatas = []

    for filename in sorted(os.listdir(docs_dir)):
        if filename.startswith("doc_") and filename.endswith(".txt"):
            filepath = os.path.join(docs_dir, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()

            chunks = chunk_text(content)

            for i, chunk in enumerate(chunks):
                ids.append(f"{filename}_{i}")
                documents.append(chunk)
                metadatas.append({
                    "source": filename,
                    "chunk_index": i
                })

    print(f"Created {len(documents)} chunks.")

    print("Generating embeddings...")
    embeddings = model.encode(documents).tolist()

    print("Storing embeddings in ChromaDB...")

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Embedded {collection.count()} chunks into ChromaDB.")


if __name__ == "__main__":
    embed_documents()