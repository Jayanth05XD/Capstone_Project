from fastapi import FastAPI
from pydantic import BaseModel

from graph import app as langgraph_app
from models import AnswerResponse


app = FastAPI(title="Zepto Support Assistant")


class QueryRequest(BaseModel):
    query: str


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QueryRequest):
    """Handle user queries using the LangGraph pipeline."""

    result = langgraph_app.invoke({
        "query": request.query
    })

    response = AnswerResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"]
    )

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860
    )