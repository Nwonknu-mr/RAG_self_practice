"""RAG系统的主命令行界面。

此脚本提供了运行索引流水线、启动交互式聊天界面
和启动FastAPI服务器的入口点。
"""

import argparse
import time

import uvicorn

from src.config import setup_logging, get_logger
from src.indexing import run_indexing
from src.rag_pipeline import get_rag_response

# 设置统一的日志配置
setup_logging()

# 获取模块专用的logger
logger = get_logger(__name__)


def run_chat_interface():
    """
    启动交互式命令行界面用于提问。
    """
    logger.info("--- 启动RAG聊天界面 ---")
    print("\n欢迎使用RAG问答系统！输入'exit'退出。")

    while True:
        query = input("\n请输入您的问题: ")
        if query.lower() == "exit":
            print("退出聊天。再见！")
            break

        if not query.strip():
            print("请输入有效的问题。")
            continue

        start_time = time.time()
        response = get_rag_response(query)
        end_time = time.time()

        print("\n--- 回答 ---")
        print(response["llm_answer"])
        print(f"\n(响应时间 {end_time - start_time:.2f}s)")

        # # print("\n--- 检索到的上下文 ---")
        # for i, item in enumerate(response["retrieved_context"]):
        #     print(
        #         f"  [{i+1}] 来源: {item['metadata'].get('source', 'N/A')}, "
        #         f"相似度分数: {item['score']:.4f}"
        #     )


def main():
    """
    解析命令行参数并运行选定模式的主函数。
    """
    parser = argparse.ArgumentParser(description="基础RAG系统命令行界面。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 索引子命令
    parser_index = subparsers.add_parser(
        "index",
        help="运行索引流水线来处理和存储文档。",
    )
    parser_index.add_argument(
        "--reindex",
        action="store_true",
        help="如果设置，在开始前删除现有索引。",
    )

    def index_func(args):
        """调用run_indexing的辅助函数。"""
        run_indexing(reindex=args.reindex)

    parser_index.set_defaults(func=index_func)

    # 问答子命令
    parser_ask = subparsers.add_parser(
        "ask", help="启动交互式聊天界面来提问。"
    )

    def ask_func(args):
        """调用run_chat_interface的辅助函数。"""
        run_chat_interface()

    parser_ask.set_defaults(func=ask_func)

    # API服务子命令
    parser_serve = subparsers.add_parser(
        "serve", help="启动FastAPI服务器。"
    )

    def run_server(args):
        """启动Uvicorn服务器。"""
        logger.info("在 http://127.0.0.1:8000 启动FastAPI服务器")
        uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)

    parser_serve.set_defaults(func=run_server)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
