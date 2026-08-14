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


model = SentenceTransformer(MODEL_NAME)

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


def classify_intent(state: AgentState) -> AgentState:
    query = state["query"].lower()

    keywords = [
        "delivery", "deliver", "return", "refund",
        "membership", "track", "tracking", "cancel",
        "gift card", "support hours"
    ]

    state["intent"] = (
        "policy_question"
        if any(word in query for word in keywords)
        else "general_question"
    )

    return state


def retrieve_and_answer(state: AgentState) -> AgentState:
    query = state["query"]

    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    state["retrieved_chunks"] = chunks
    state["sources"] = list(
        dict.fromkeys(
            metadata["source"]
            for metadata in metadatas
        )
    )

    if not chunks:
        state["answer"] = (
            "Based on the retrieved context: "
            "No relevant policy information was found."
        )
        state["confidence"] = 0.0
        return state

    state["answer"] = (
        "Based on the retrieved context: "
        + chunks[0]
    )

    state["confidence"] = round(
        max(0.0, min(1.0, 1.0 - distances[0])),
        2
    )

    return state


def direct_answer(state: AgentState) -> AgentState:
    state["answer"] = (
        "I can only answer questions about Zepto policies right now."
    )
    state["sources"] = []
    state["retrieved_chunks"] = []
    state["confidence"] = 1.0

    return state


def route_by_intent(state: AgentState) -> str:
    return (
        "retrieve_and_answer"
        if state["intent"] == "policy_question"
        else "direct_answer"
    )


workflow = StateGraph(AgentState)

workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_and_answer", retrieve_and_answer)
workflow.add_node("direct_answer", direct_answer)

workflow.set_entry_point("classify_intent")

workflow.add_conditional_edges(
    "classify_intent",
    route_by_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)

workflow.add_edge("retrieve_and_answer", END)
workflow.add_edge("direct_answer", END)

app = workflow.compile()