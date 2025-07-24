from typing import List

import nltk  # type: ignore
from langchain.docstore.document import Document
from langchain.text_splitter import (
    NLTKTextSplitter,
    RecursiveCharacterTextSplitter,
)

from src.config import get_logger

# 获取模块专用的logger
logger = get_logger(__name__)


def ensure_nltk_data():
    """
    检查NLTK的'punkt'分词器是否可用，如果不可用则下载。
    """
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        logger.info("NLTK 'punkt' model not found. Downloading...")
        nltk.download("punkt")
        logger.info("NLTK 'punkt' download complete.")


# 在模块加载时确保NLTK数据可用
ensure_nltk_data()


def split_documents(documents: List[Document]) -> List[Document]:
    """
    对文档列表执行两步分割。

    首先，使用RecursiveCharacterTextSplitter将文档分割成较大的块（段落）。
    然后，使用NLTKTextSplitter将这些块分割成更小的块（句子）。

    Args:
        documents (List[Document]): 要分割的文档列表。

    Returns:
        List[Document]: 句子级别的文档块列表，包含丰富的元数据。
    """
    logger.info(
        f"Starting two-step text splitting on {len(documents)} documents."
    )

    # 第一步分割：分成段落/章节
    paragraph_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=False,
    )

    # 第二步分割：分成句子
    # 设置较小的chunk_size以确保NLTK按句子分割
    sentence_splitter = NLTKTextSplitter(chunk_size=200)

    final_chunks = []
    for doc in documents:
        paragraph_chunks = paragraph_splitter.split_documents([doc])
        for i, para_chunk in enumerate(paragraph_chunks):
            chunk_item = {'para': para_chunk, 'sentences': []}
            sentence_chunks = sentence_splitter.split_documents([para_chunk])
            for j, sent_chunk in enumerate(sentence_chunks):
                # 丰富元数据
                source = doc.metadata.get("source", "N/A")
                sent_chunk.metadata["source"] = source
                sent_chunk.metadata["paragraph_num"] = i
                sent_chunk.metadata["sentence_num_in_para"] = j
                chunk_item['sentences'].appen(sent_chunk)
            final_chunks.append(chunk_item)

    logger.info(
        f"Splitting complete. Generated {len(final_chunks)} chunks."
    )
    return final_chunks



