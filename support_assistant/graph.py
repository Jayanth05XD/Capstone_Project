import os
from pathlib import Path
from typing import List, Literal, TypedDict

import chromadb
from langgraph.graph import END, StateGraph
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "zepto_policy"


class AgentState(TypedDict, total=False):
    query: str
    intent: Literal["policy_question", "general_question"]
    retrieved_chunks: List[str]
    sources: List[str]
    answer: str
    confidence: float


# Embedding model
model = SentenceTransformer(MODEL_NAME)

# Persistent ChromaDB
client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


def classify_intent(state: AgentState) -> AgentState:
    """Classify the query using the required keyword heuristic."""

    query = state["query"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "cancel",
        "gift card",
        "support hours",
    ]

    if any(keyword in query for keyword in policy_keywords):
        state["intent"] = "policy_question"
    else:
        state["intent"] = "general_question"

    return state


def retrieve_and_answer(state: AgentState) -> AgentState:
    """Retrieve the top 3 relevant chunks and generate a mock answer."""

    query = state["query"]

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    sources = list(
        dict.fromkeys(
            metadata["source"]
            for metadata in metadatas
        )
    )

    state["retrieved_chunks"] = retrieved_chunks
    state["sources"] = sources

    # Graded baseline: deterministic mock response.
    mock_llm = os.getenv("MOCK_LLM", "1")

    if mock_llm != "0":
        if retrieved_chunks:
            top_chunk = retrieved_chunks[0]

            state["answer"] = (
                "Based on the retrieved context: "
                + top_chunk
            )
        else:
            state["answer"] = (
                "Based on the retrieved context: "
                "No relevant policy information was found."
            )

        state["confidence"] = 1.0

    else:
        # Real LLM integration can be added here later.
        # Keep the project functional without an API key.
        if retrieved_chunks:
            state["answer"] = (
                "Based on the retrieved context: "
                + retrieved_chunks[0]
            )
        else:
            state["answer"] = (
                "Based on the retrieved context: "
                "No relevant policy information was found."
            )

        state["confidence"] = 1.0

    return state


def direct_answer(state: AgentState) -> AgentState:
    """Return the required mock response for general questions."""

    state["answer"] = (
        "I can only answer questions about Zepto policies right now."
    )

    state["sources"] = []
    state["retrieved_chunks"] = []
    state["confidence"] = 1.0

    return state


def route_by_intent(state: AgentState) -> str:
    """Choose the next node based on the classified intent."""

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


# Build LangGraph
workflow = StateGraph(AgentState)

workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_and_answer", retrieve_and_answer)
workflow.add_node("direct_answer", direct_answer)

workflow.set_entry_point("classify_intent")

# Conditional routing
workflow.add_conditional_edges(
    "classify_intent",
    route_by_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer",
    },
)

workflow.add_edge("retrieve_and_answer", END)
workflow.add_edge("direct_answer", END)

app = workflow.compile()