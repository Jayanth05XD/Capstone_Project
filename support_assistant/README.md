# Zepto Support Assistant

## Architecture Overview

This project implements a Retrieval-Augmented Generation (RAG) pipeline for answering questions about Zepto's policies and services.

### Pipeline Stages

1. **Ingestion → Embedding** (`embed_documents.py`)
   - Reads 8 policy documents from `docs/`
   - Splits text into chunks (~200 characters each)
   - Generates embeddings using `all-MiniLM-L6-v2`
   - Stores in ChromaDB collection `zepto_policy`

2. **Retrieval** (`retrieve_and_answer` node)
   - Embeds user query
   - Retrieves top-3 most similar chunks via cosine similarity
   - Always runs in both mock and real LLM modes

3. **Generation** (`retrieve_and_answer` / `direct_answer` nodes)
   - **Policy questions**: Uses structured prompt template with retrieved context
   - **General questions**: Returns fixed canned response

### MOCK_LLM Toggle

- **Default (MOCK_LLM=1 or unset)**: Uses keyword heuristic for intent classification and canned answers
- **Optional (MOCK_LLM=0)**: Calls real LLM for classification and answer generation

### Example API Calls

**Policy Question (retrieval triggered):**
```bash
curl -X POST http://localhost:7860/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"What is Zepto\'s delivery policy?"}'
