"""文档索引流水线模块。

此模块包含处理文档并将其索引到向量存储中的核心逻辑。
它可以从命令行或API调用。
"""
import time

from src.config import DATA_DIR, LANCEDB_TABLE_NAME, get_logger
from src.document_loader import load_documents
from src.text_splitter import split_documents
from src.vector_store import add_documents_to_store, get_db_connection

# 获取模块专用的logger
logger = get_logger(__name__)


def run_indexing(reindex: bool = False):
    """
    运行完整的索引流水线：加载、分割、编码和存储。

    此函数编排从数据目录读取文档、将其分割成可管理的块，
    然后将它们添加到LanceDB向量存储的过程。

    Args:
        reindex (bool): 如果为True，在索引新文档前删除现有的LanceDB表。
                       默认为False。

    Returns:
        dict: 包含索引操作状态、描述性消息和总持续时间（秒）的字典。
    """
    logger.info("--- 开始索引流水线 ---")
    start_time = time.time()

    db_conn = get_db_connection()
    if db_conn is None:
        return {
            "status": "error",
            "message": "连接数据库失败。",
            "duration_seconds": time.time() - start_time,
        }

    if reindex and LANCEDB_TABLE_NAME in db_conn.table_names():
        logger.info(f"正在删除现有表: {LANCEDB_TABLE_NAME}")
        db_conn.drop_table(LANCEDB_TABLE_NAME)

    docs = load_documents(DATA_DIR)
    if not docs:
        logger.warning("在数据目录中未找到文档。")
        duration = time.time() - start_time
        return {
            "status": "warning",
            "message": "未找到要索引的文档。",
            "duration_seconds": duration,
        }

    chunks = split_documents(docs)
    success = add_documents_to_store(chunks, db_conn, LANCEDB_TABLE_NAME)

    duration = time.time() - start_time
    if success:
        message = (
            f"索引完成。处理了 {len(docs)} 个文档，"
            f"生成了 {len(chunks)} 个文本块。"
        )
        logger.info(f"--- 索引流水线在 {duration:.2f}s 内完成 ---")
        return {
            "status": "success",
            "message": message,
            "duration_seconds": duration,
        }
    else:
        logger.error(f"--- 索引流水线在 {duration:.2f}s 内失败 ---")
        return {
            "status": "error",
            "message": "向向量存储添加文档失败。",
            "duration_seconds": duration,
        }