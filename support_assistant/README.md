# Zepto Support Assistant

A containerized **RAG-based support assistant** that answers questions about Zepto policies using local policy documents, semantic search, ChromaDB, and LangGraph.

## Architecture

The application follows this pipeline:

**Policy Documents → Chunking → Embeddings → ChromaDB → Query Embedding → Retrieval → Answer**

### 1. Ingestion and Embedding

`embed_documents.py`

* Reads the 8 policy documents from `docs/`
* Splits documents into chunks of approximately 200 characters
* Generates embeddings using `all-MiniLM-L6-v2`
* Stores the embeddings and metadata in ChromaDB
* Uses the `zepto_policy` collection

### 2. Intent Classification

`graph.py`

User queries are classified using a keyword-based heuristic.

Policy-related keywords include:

* delivery
* return
* refund
* membership
* tracking
* cancel
* gift card
* support hours

Policy questions continue to the retrieval stage.

Other questions receive:

> I can only answer questions about Zepto policies right now.

### 3. Retrieval

For policy questions:

* The query is converted into an embedding.
* ChromaDB searches for the **top 3 most similar chunks**.
* Cosine distance is used for similarity.
* The retrieved document sources are included in the API response.

### 4. Answer Generation

The application currently uses a deterministic answer based on the best retrieved context.

Example:

```text
Based on the retrieved context: Orders can be cancelled free of cost any time before the order status changes to 'Packed'...
```

The confidence score is calculated from the ChromaDB distance.

## Project Structure

```text
support_assistant/
│
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
│
├── chroma_db/
│
├── embed_documents.py
├── graph.py
├── main.py
├── models.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

## Technologies Used

* Python 3.11
* FastAPI
* Uvicorn
* LangGraph
* ChromaDB
* Sentence Transformers
* PyTorch
* Docker

## Running Locally

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Generate the ChromaDB embeddings:

```powershell
python embed_documents.py
```

Start the API:

```powershell
uvicorn main:app --host 0.0.0.0 --port 7860
```

The API will be available at:

```text
http://localhost:7860
```

Interactive API documentation:

```text
http://localhost:7860/docs
```

## Docker

Build the image from the project root:

```powershell
docker build -t zepto-support ./support_assistant
```

Run the container:

```powershell
docker run --rm -p 7860:7860 zepto-support
```

If port `7860` is already in use, stop the existing container first:

```powershell
docker ps
docker stop <container_id>
```

Then run the container again.

## API

### Endpoint

```text
POST /ask
```

### Request

```json
{
  "query": "How can I cancel my order?"
}
```

### Response

```json
{
  "answer": "Based on the retrieved context: Orders can be cancelled free of cost any time before the order status changes to 'Packed'...",
  "sources": [
    "doc_05.txt",
    "doc_03.txt"
  ],
  "confidence": 0.52
}
```

## Testing with PowerShell

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:7860/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query":"How can I cancel my order?"}' |
  ConvertTo-Json
```

### Example Questions

```text
How can I cancel my order?
```

```text
How long does a refund take?
```

```text
What should I do if my delivery is delayed?
```

```text
How do I track my order?
```

```text
Can I cancel my membership?
```

General questions outside Zepto policies are rejected by the intent-routing stage.

Example:

```text
What is the capital of India?
```

Response:

```text
I can only answer questions about Zepto policies right now.
```

## RAG Workflow

```text
                    User Query
                        │
                        ▼
               Intent Classification
                   │          │
          Policy Question   General Question
                   │          │
                   ▼          ▼
            Query Embedding  Direct Answer
                   │
                   ▼
                ChromaDB
                   │
                   ▼
             Top 3 Chunks
                   │
                   ▼
            Best Context
                   │
                   ▼
               Response
```

## Important Notes

* The embedding model is downloaded when the application starts if it is not already available in the environment.
* ChromaDB stores the generated embeddings persistently in `chroma_db/`.
* The policy documents are the knowledge source for the assistant.
* The application does not answer general-purpose questions.
* The current answer generation is deterministic and does not require an external LLM API key.
* `MOCK_LLM` is retained as a configuration option for extending the project with a real LLM later.

## Docker Image

The application is packaged as:

```text
zepto-support
```

The container exposes port:

```text
7860
```

The application starts using Uvicorn:

```text
uvicorn main:app --host 0.0.0.0 --port 7860
```