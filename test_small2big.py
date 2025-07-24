#!/usr/bin/env python3
"""
测试Small2Big技术的检索效果
"""

from src.config import LANCEDB_TABLE_NAME
from src.vector_store import get_db_connection, search_vector_store


def test_small2big_retrieval():
    """测试Small2Big检索功能"""
    print("=== Small2Big技术检索测试 ===\n")

    # 连接数据库
    db = get_db_connection()
    if not db:
        print("❌ 数据库连接失败")
        return

    # 测试查询
    test_queries = ["RAG系统的核心组件", "LanceDB的特点", "向量相似度搜索方法"]

    for i, query in enumerate(test_queries, 1):
        print(f"🔍 测试查询 {i}: {query}")
        print("-" * 50)

        # 执行检索
        results = search_vector_store(query, db, LANCEDB_TABLE_NAME, top_k=2)

        if not results:
            print("❌ 没有找到相关结果\n")
            continue

        # 显示结果
        for j, result in enumerate(results, 1):
            print(f"📄 结果 {j} (相似度分数: {result['score']:.2f})")
            print(f"📍 匹配句子: {result['sentence'][:100]}...")

            if result["metadata"].get("has_context", False):
                print(f"📖 段落上下文: {result['paragraph'][:200]}...")
                print("✅ Small2Big上下文已提供")
            else:
                print("⚠️  没有段落上下文")

            print(f"📂 来源: {result['metadata'].get('source', '未知')}")
            print()

        print("=" * 60)
        print()


if __name__ == "__main__":
    test_small2big_retrieval()
