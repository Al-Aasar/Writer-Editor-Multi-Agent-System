import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
from typing import Literal
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from backend import app as workflow
except ImportError:
    from writer_editor.backend import app as workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("article_api")

app = FastAPI(title="Article Writer API")


class ArticleRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)


class ArticleResponse(BaseModel):
    status: Literal["ok", "blocked"]
    content: str
    llm_calls: int


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Article Writer API is running",
        "features": ["input_guardrail", "writer_editor_loop", "web_search"],
    }


@app.post("/article", response_model=ArticleResponse)
async def create_article(req: ArticleRequest):
    try:
        result = await workflow.ainvoke(
            {"user_query": req.query, "iteration": 0, "llm_calls": 0},
            config={"recursion_limit": 25},
        )
    except Exception:
        logger.exception("Workflow failed")
        raise HTTPException(status_code=500, detail="Something went wrong.")

    if result.get("error"):
        logger.error("Agent error: %s", result["error"])
        raise HTTPException(status_code=502, detail="The article could not be generated.")

    blocked = not result.get("guardrail_allowed", False)
    content = result.get("final_response") or result.get("draft", "")
    return ArticleResponse(
        status="blocked" if blocked else "ok",
        content=content,
        llm_calls=result.get("llm_calls", 0),
    )


def run():
    uvicorn.run("writer_editor.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
