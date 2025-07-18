import json
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import lancedb  # type: ignore
import pyarrow as pa  # type: ignore
from langchain.docstore.document import Document

from src.config import LANCEDB_TABLE_NAME, LANCEDB_URI, get_logger
from src.embedding_model import embedding_model

if TYPE_CHECKING:
    # 仅在类型检查时导入，避免运行时错误
    from lancedb import Table

# 获取模块专用的logger
logger = get_logger(__name__)


def get_db_connection() -> Optional[lancedb.DBConnection]:
    """
    建立与LanceDB数据库的连接。

    Returns:
        Optional[lancedb.DBConnection]: 数据库连接对象，如果连接失败则返回None
    """
    try:
        logger.info(f"正在连接到LanceDB: {LANCEDB_URI}")
        return lancedb.connect(LANCEDB_URI)
    except Exception as e:
        logger.error(f"连接LanceDB失败: {e}")
        return None


def create_or_get_table(
    db: lancedb.DBConnection, table_name: str, embedding_dim: int
) -> Optional["Table"]:
    """
    在LanceDB中创建表（如果不存在）或打开现有表。

    Args:
        db: LanceDB数据库连接
        table_name: 表名
        embedding_dim: 向量维度

    Returns:
        Optional[lancedb.Table]: 表对象，如果操作失败则返回None
    """
    try:
        if table_name in db.table_names():
            logger.info(f"正在打开现有表: {table_name}")
            return db.open_table(table_name)

        logger.info(f"正在创建新表: {table_name}")
        schema = pa.schema(
            [
                pa.field(
                    "vector", pa.list_(pa.float32(), list_size=embedding_dim)
                ),
                pa.field("text", pa.string()),
                pa.field("metadata", pa.string()),  # 将元数据存储为JSON字符串
            ]
        )
        return db.create_table(table_name, schema=schema)
    except Exception as e:
        logger.error(f"创建或获取表 '{table_name}' 失败: {e}")
        return None


def add_documents_to_store(
    documents: List[Document], db: lancedb.DBConnection, table_name: str
) -> bool:
    """
    将文档列表编码并添加到指定的LanceDB表中。

    Args:
        documents: 要添加的文档列表
        db: LanceDB数据库连接
        table_name: 目标表名

    Returns:
        bool: 操作是否成功
    """
    if not documents:
        logger.warning("没有提供要添加到存储的文档。")
        return False

    try:
        texts = [doc.page_content for doc in documents]
        embeddings = embedding_model.encode(texts)

        if embeddings is None:
            logger.error("生成嵌入失败。无法添加文档。")
            return False

        embedding_dim = embeddings.shape[1]
        table = create_or_get_table(db, table_name, embedding_dim)

        if table is None:
            logger.error("创建或获取表失败。无法添加文档。")
            return False

        data = [
            {
                "vector": vector.tolist(),
                "text": doc.page_content,
                "metadata": json.dumps(doc.metadata),
            }
            for doc, vector in zip(documents, embeddings)
        ]

        logger.info(f"正在向表 '{table_name}' 添加 {len(data)} 个文档。")
        table.add(data)
        logger.info("文档添加成功。")
        return True

    except Exception as e:
        logger.error(f"向存储添加文档失败: {e}")
        return False


def search_vector_store(
    query: str, db: lancedb.DBConnection, table_name: str, top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    在向量存储中搜索与查询最相似的文档。

    Args:
        query: 查询字符串
        db: LanceDB数据库连接
        table_name: 表名
        top_k: 返回的最相似结果数量

    Returns:
        List[Dict[str, Any]]: 搜索结果列表，每个结果包含text、metadata和score
    """
    try:
        # 尝试打开表
        table = db.open_table(table_name)
    except FileNotFoundError:
        logger.error(f"表 '{table_name}' 未找到。请先创建它。")
        return []
    except Exception as e:
        logger.error(f"打开表 '{table_name}' 失败: {e}")
        return []

    try:
        # 编码查询
        query_vector = embedding_model.encode(query)
        if query_vector is None:
            logger.error("查询编码失败。搜索中止。")
            return []

        logger.info(f"正在搜索查询 '{query}' 的前 {top_k} 个结果")

        # 执行搜索
        results = table.search(query_vector).limit(top_k).to_df()

        search_results = []
        for _, row in results.iterrows():
            try:
                metadata_str = str(row["metadata"])
                metadata = json.loads(metadata_str)
                search_results.append(
                    {
                        "text": str(row["text"]),
                        "metadata": metadata,
                        "score": float(row["_distance"]),
                    }
                )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"解析结果行失败: {e}")
                continue

        logger.info(f"找到 {len(search_results)} 个结果。")
        return search_results

    except Exception as e:
        logger.error(f"搜索操作失败: {e}")
        return []



