"""RAG系统的FastAPI应用程序。

此模块定义了与RAG流水线交互的API端点，
包括提问和触发索引过程。它使用FastAPI
创建Web服务器，使用Pydantic进行数据验证。
"""
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import get_logger
from src.indexing import run_indexing
from src.rag_pipeline import get_rag_response

# 获取模块专用的logger
logger = get_logger(__name__)

# 初始化FastAPI应用
app = FastAPI(
    title="RAG系统API",
    description="用于索引文档和提问的API。",
    version="1.0.0",
)


# --- 用于请求/响应的Pydantic模型 ---


class QueryRequest(BaseModel):
    """用于/ask端点的请求模型。"""

    query: str


class ContextItem(BaseModel):
    """单个检索上下文项的响应模型。"""

    text: str
    metadata: Dict[str, Any]
    score: float


class AskResponse(BaseModel):
    """用于/ask端点的响应模型。"""

    llm_answer: str
    retrieved_context: List[ContextItem]


class IndexResponse(BaseModel):
    """用于/index端点的响应模型。"""

    status: str
    message: str
    duration_seconds: Optional[float] = None


# --- API端点 ---


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: QueryRequest):
    """
    接收问题，检索相关上下文，并返回答案。
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=400, detail="查询不能为空。"
        )

    logger.info(f"API /ask端点被调用，查询: '{request.query}'")
    try:
        response_data = get_rag_response(request.query)
        return response_data
    except Exception as e:
        logger.error(f"RAG流水线错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="RAG流水线内部服务器错误。"
        ) from e


@app.post("/index", response_model=IndexResponse)
async def trigger_indexing(reindex: bool = False):
    """
    触发文档索引流水线。

    Args:
        reindex (bool): 如果为True，将在处理文档前删除现有索引。默认为False。
    """
    logger.info(f"API /index端点被调用，reindex={reindex}")
    try:
        # 注意：这是同步运行的，会阻塞服务器。
        # 在生产环境中，这应该是一个后台任务
        # （例如，使用Celery）。
        result = run_indexing(reindex=reindex)
        return result
    except Exception as e:
        logger.error(f"索引过程中的错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"索引过程中的内部服务器错误: {e}",
        ) from e
