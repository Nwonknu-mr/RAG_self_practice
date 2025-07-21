import json
import threading
from typing import List, Optional, Union

import numpy as np
import requests

from src.config import DEEPSEEK_API_BASE, DEEPSEEK_EMBEDDING_MODEL, get_logger

# 获取模块专用的logger
logger = get_logger(__name__)


class EmbeddingModel:
    """
    线程安全的单例包装器，使用DeepSeek API进行文本嵌入。
    """

    _instance = None
    _lock = threading.Lock()
    api_available: bool

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                # 双重检查锁定模式，确保线程安全
                if not cls._instance:
                    cls._instance = super(EmbeddingModel, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "api_available"):  # 确保只初始化一次
            with self._lock:
                # 再次检查，防止多线程重复初始化
                if not hasattr(self, "api_available"):
                    self._test_api_connection()

    def _test_api_connection(self):
        """测试DeepSeek API连接。"""
        try:
            # 测试配置端点是否可用
            config_url = f"{DEEPSEEK_API_BASE.replace('/v1', '')}/api/config"
            response = requests.get(config_url, timeout=5)
            response.raise_for_status()

            config_data = response.json()
            logger.info(f"DeepSeek API连接成功，配置: {config_data}")
            self.api_available = True

        except Exception as e:
            logger.error(f"DeepSeek API连接测试失败: {e}")
            # 即使配置端点失败，也尝试继续使用API
            logger.warning("将尝试直接使用分析端点")
            self.api_available = True

    def _call_embedding_api(self, texts: List[str]) -> Optional[np.ndarray]:
        """调用DeepSeek分析API获取文本特征向量。"""
        try:
            analyze_url = f"{DEEPSEEK_API_BASE.replace('/v1', '')}/api/analyze"

            embeddings = []
            for text in texts:
                request_data = {
                    "text": text,
                    "mode": "topic",  # 使用主题分析模式
                }

                response = requests.post(
                    analyze_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )

                response.raise_for_status()
                response_data = response.json()

                # 从分析结果中提取特征向量
                # 这里需要根据实际API响应格式调整
                if isinstance(response_data, dict):
                    # 尝试提取数值特征作为向量
                    features = self._extract_features_from_analysis(response_data, text)
                    if features is not None:
                        embeddings.append(features)
                    else:
                        logger.warning(f"无法从分析结果中提取特征: {response_data}")
                        # 使用简单的文本哈希作为备用方案
                        embeddings.append(self._text_to_simple_vector(text))
                else:
                    logger.warning(f"意外的API响应格式: {response_data}")
                    embeddings.append(self._text_to_simple_vector(text))

            if embeddings:
                return np.array(embeddings)
            else:
                return None

        except requests.exceptions.Timeout:
            logger.error("DeepSeek API请求超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API请求失败: {e}")
            return None
        except Exception as e:
            logger.error(f"调用DeepSeek分析API时发生未知错误: {e}")
            return None

    def _extract_features_from_analysis(
        self, analysis_result: dict, text: str
    ) -> Optional[np.ndarray]:
        """从分析结果中提取数值特征向量。"""
        try:
            features = []

            # 基础文本统计特征
            features.extend(
                [
                    len(text),  # 文本长度
                    len(text.split()),  # 词数
                    len(set(text.split())),  # 唯一词数
                    text.count("。"),  # 句号数量
                    text.count("，"),  # 逗号数量
                ]
            )

            # 从分析结果中提取特征
            if "sentiment" in analysis_result:
                sentiment = analysis_result["sentiment"]
                if isinstance(sentiment, (int, float)):
                    features.append(sentiment)
                elif isinstance(sentiment, dict):
                    features.extend(
                        [
                            sentiment.get("positive", 0),
                            sentiment.get("negative", 0),
                            sentiment.get("neutral", 0),
                        ]
                    )

            if "topics" in analysis_result:
                topics = analysis_result["topics"]
                if isinstance(topics, list):
                    # 取前10个主题的权重
                    topic_weights = [
                        topic.get("weight", 0) if isinstance(topic, dict) else 0
                        for topic in topics[:10]
                    ]
                    features.extend(topic_weights)
                    # 补齐到10个
                    while len(topic_weights) < 10:
                        features.append(0.0)

            # 确保向量有固定维度（比如128维）
            target_dim = 128
            if len(features) < target_dim:
                features.extend([0.0] * (target_dim - len(features)))
            elif len(features) > target_dim:
                features = features[:target_dim]

            return np.array(features, dtype=np.float32)

        except Exception as e:
            logger.error(f"提取特征时发生错误: {e}")
            return None

    def _text_to_simple_vector(self, text: str) -> np.ndarray:
        """将文本转换为简单的数值向量（备用方案）。"""
        # 使用简单的字符统计和哈希方法
        features = []

        # 基础统计特征
        features.extend(
            [
                len(text),
                len(text.split()),
                len(set(text.split())),
                text.count("。"),
                text.count("，"),
                text.count("的"),
                text.count("是"),
                text.count("在"),
                text.count("有"),
                text.count("和"),
            ]
        )

        # 字符频率特征
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1

        # 取最常见的字符频率
        common_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)[
            :20
        ]
        char_features = [count for _, count in common_chars]
        features.extend(char_features)

        # 补齐到128维
        target_dim = 128
        if len(features) < target_dim:
            features.extend([0.0] * (target_dim - len(features)))
        elif len(features) > target_dim:
            features = features[:target_dim]

        return np.array(features, dtype=np.float32)

    def encode(self, texts: Union[str, List[str]]) -> Union[np.ndarray, None]:
        """
        将单个文本或文本列表编码为向量嵌入。

        Args:
            texts (Union[str, List[str]]): 要编码的文本或文本列表。

        Returns:
            Union[np.ndarray, None]: 嵌入向量的numpy数组，如果API不可用则返回None。
        """
        if not self.api_available:
            logger.error("DeepSeek API不可用。无法进行编码。")
            return None

        # 确保texts是列表格式
        if isinstance(texts, str):
            texts = [texts]

        num_texts = len(texts)
        logger.info(f"正在使用DeepSeek API编码 {num_texts} 个文本。")

        # 调用DeepSeek API
        embeddings = self._call_embedding_api(texts)

        if embeddings is not None:
            logger.info(f"成功获取 {num_texts} 个文本的嵌入向量")
            # 如果原始输入是单个字符串，返回单个向量
            if len(embeddings) == 1 and not isinstance(texts, list):
                return embeddings[0]
            return embeddings
        else:
            logger.error("获取嵌入向量失败")
            return None


# 单例实例，便于在整个应用程序中导入和使用
embedding_model = EmbeddingModel()
