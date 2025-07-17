from pathlib import Path
from typing import List, Dict, Type

from langchain.docstore.document import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

from src.config import DATA_DIR, get_logger

# 获取模块专用的logger
logger = get_logger(__name__)

# 文件扩展名到加载器类的映射
LOADER_MAPPING: Dict[str, Type] = {
    ".pdf": PyPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".md": UnstructuredMarkdownLoader,
    ".txt": TextLoader,
}


def load_documents(source_dir: Path = DATA_DIR) -> List[Document]:
    """
    从指定的源目录加载所有文档，根据文件扩展名使用相应的加载器。

    Args:
        source_dir (Path): 包含文档的目录路径。

    Returns:
        List[Document]: 已加载的文档列表。
    """
    all_docs = []
    logger.info(f"Loading documents from: {source_dir}")

    if not source_dir.is_dir():
        logger.error(f"Source directory not found: {source_dir}")
        return []

    for file_path in source_dir.iterdir():
        if file_path.is_file():
            loader_class = LOADER_MAPPING.get(file_path.suffix.lower())
            if loader_class:
                try:
                    logger.info(f"Loading file: {file_path}")
                    loader = loader_class(str(file_path))
                    docs = loader.load()
                    all_docs.extend(docs)
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")
            else:
                logger.warning(
                    f"Unsupported file type: {file_path.suffix}. Skipping."
                )

    logger.info(f"Successfully loaded {len(all_docs)} documents.")
    return all_docs



