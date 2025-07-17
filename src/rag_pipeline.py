import requests
from typing import Any, Dict, List

from src.config import (
    LANCEDB_TABLE_NAME, TOP_K, get_logger,
    DEEPSEEK_API_BASE, DEEPSEEK_CHAT_MODEL
)
from src.vector_store import get_db_connection, search_vector_store
from datetime import datetime
import os

# 获取模块专用的logger
logger = get_logger(__name__)

# 相关度阈值配置
RELEVANCE_THRESHOLD = 50000  # 相似度分数阈值，低于此值认为不相关
KNOWLEDGE_BASE_FILE = "data/generated_qa.txt"  # 存储生成的问答对


def call_deepseek_api(prompt: str, system_message: str = None) -> str:
    """
    调用DeepSeek预测API。

    Args:
        prompt (str): 用户提示
        system_message (str, optional): 系统消息

    Returns:
        str: API响应或错误消息
    """
    try:
        # 构建完整的输入文本
        full_input = prompt
        if system_message:
            full_input = f"{system_message}\n\n{prompt}"

        logger.info(f"发送请求到DeepSeek聊天API，输入长度: {len(full_input)}")

        # 发送请求到聊天端点
        chat_url = f"{DEEPSEEK_API_BASE}/chat/completions"

        # 重新构建为聊天格式
        chat_request = {
            "model": DEEPSEEK_CHAT_MODEL,
            "messages": [
                {"role": "user", "content": full_input}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(
            chat_url,
            json=chat_request,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        response.raise_for_status()
        response_data = response.json()

        # 提取聊天回答
        if "choices" in response_data and len(response_data["choices"]) > 0:
            answer = response_data["choices"][0]["message"]["content"]
            logger.info(f"成功获取DeepSeek聊天回答，长度: {len(answer)}")
            return answer.strip()
        else:
            logger.warning(f"聊天API响应中没有找到choices字段: {response_data}")
            return f"抱歉，API返回了意外的响应格式: {response_data}"

    except requests.exceptions.Timeout:
        logger.error("DeepSeek预测API请求超时")
        return "抱歉，请求超时。请稍后再试。"
    except requests.exceptions.RequestException as e:
        logger.error(f"DeepSeek预测API请求失败: {e}")
        return f"抱歉，API请求失败: {str(e)}"
    except Exception as e:
        logger.error(f"调用DeepSeek预测API时发生未知错误: {e}")
        return f"抱歉，发生了未知错误: {str(e)}"


def save_qa_to_knowledge_base(question: str, answer: str):
    """
    将问答对保存到知识库文件中。

    Args:
        question (str): 用户问题
        answer (str): AI回答
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(KNOWLEDGE_BASE_FILE), exist_ok=True)

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 格式化问答对
        qa_content = f"""
=== 问答记录 ===
时间: {timestamp}
问题: {question}
回答: {answer}

"""

        # 追加到文件
        with open(KNOWLEDGE_BASE_FILE, 'a', encoding='utf-8') as f:
            f.write(qa_content)

        logger.info(f"已将问答对保存到知识库: {KNOWLEDGE_BASE_FILE}")

    except Exception as e:
        logger.error(f"保存问答对到知识库失败: {e}")


def check_relevance(retrieved_context: list) -> bool:
    """
    检查检索到的上下文是否相关。

    Args:
        retrieved_context (list): 检索到的上下文列表

    Returns:
        bool: True表示相关，False表示不相关
    """
    if not retrieved_context:
        return False

    # 检查最高相似度分数
    max_score = max(item.get('score', 0) for item in retrieved_context)

    logger.info(f"最高相似度分数: {max_score}, 阈值: {RELEVANCE_THRESHOLD}")

    return max_score >= RELEVANCE_THRESHOLD


def build_prompt(query: str, context: List[Dict[str, Any]]) -> str:
    """
    为LLM构建提示，结合用户查询和检索到的上下文。
    """
    if not context:
        return (
            "你是一个有用的AI助手。请回答以下问题。"
            "注意，你无法从知识库中检索到任何相关上下文。\n\n"
            f"问题: {query}"
        )

    context_str = "\n\n---\n\n".join(
        [
            f"来源: {item['metadata'].get('source', 'N/A')}\n"
            f"内容: {item['text']}"
            for item in context
        ]
    )

    prompt = (
        "你是一个有用的AI助手。请根据以下来自知识库的上下文回答用户的问题。"
        "如果上下文中不包含答案，请说明你在提供的文档中找不到答案。\n\n"
        f"--- 上下文 ---\n"
        f"{context_str}\n\n"
        f"--- 问题 ---\n"
        f"{query}\n\n"
        f"--- 回答 ---\n"
    )
    return prompt


def call_llm_api(prompt: str) -> str:
    """
    调用DeepSeek LLM API生成回答。

    Args:
        prompt (str): 包含上下文和问题的完整提示

    Returns:
        str: LLM生成的回答
    """
    logger.info("--- 向DeepSeek LLM发送提示 ---")
    logger.debug(f"提示内容: {prompt[:200]}...")  # 只记录前200个字符

    # 直接调用DeepSeek API
    return call_deepseek_api(prompt)


def get_rag_response(query: str) -> Dict[str, Any]:
    """
    编排RAG流水线：搜索 -> 构建提示 -> 获取LLM响应。

    Args:
        query (str): 用户查询

    Returns:
        Dict[str, Any]: 包含LLM回答和检索上下文的字典
    """
    logger.info(f"收到查询: {query}")

    try:
        # 1. 连接数据库
        db_conn = get_db_connection()
        if db_conn is None:
            logger.error("无法连接到数据库")
            return {
                "llm_answer": "抱歉，系统暂时无法访问知识库。请稍后再试。",
                "retrieved_context": [],
            }

        # 2. 检索相关上下文
        retrieved_context = search_vector_store(
            query, db_conn, LANCEDB_TABLE_NAME, top_k=TOP_K
        )

        logger.info(f"检索到 {len(retrieved_context)} 个相关文档片段")

        # 3. 检查相关度并生成回答
        is_relevant = check_relevance(retrieved_context)

        if is_relevant:
            # 相关度高，使用检索到的上下文
            context_str = "\n\n".join([
                f"文档 {i+1}:\n来源: {doc.get('metadata', {}).get('source', '未知')}\n内容: {doc.get('text', '')}"
                for i, doc in enumerate(retrieved_context)
            ])

            system_message = (
                "你是一个有用的AI助手。请根据提供的上下文信息回答用户的问题。"
                "请保持回答的准确性和相关性。"
            )

            prompt = f"""基于以下上下文信息回答问题：

上下文信息：
{context_str}

问题：{query}

请根据上述上下文信息回答问题。"""

            llm_answer = call_deepseek_api(prompt, system_message)
            logger.info("使用检索上下文生成回答")

        else:
            # 相关度低，直接使用模型知识回答
            system_message = (
                "你是一个有用的AI助手。请直接基于你的知识回答用户的问题。"
                "请提供准确、有用的信息。"
            )

            prompt = f"""问题：{query}

请基于你的知识直接回答这个问题。"""

            llm_answer = call_deepseek_api(prompt, system_message)
            logger.info("检索上下文相关度低，使用模型直接回答")

            # 将问答对保存到知识库
            save_qa_to_knowledge_base(query, llm_answer)
            logger.info("已将新的问答对保存到知识库，下次查询时可以检索到")

        return {
            "llm_answer": llm_answer,
            "retrieved_context": retrieved_context,
        }

    except Exception as e:
        logger.error(f"RAG流水线执行失败: {e}")
        return {
            "llm_answer": f"抱歉，处理您的查询时遇到了问题: {str(e)}",
            "retrieved_context": [],
        }



