import logging
import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

# 抑制urllib3的SSL警告
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

# 从.env文件加载环境变量
load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 数据和数据库目录
DATA_DIR = ROOT_DIR / "data"
DB_DIR = ROOT_DIR / "db"

# LanceDB配置
LANCEDB_URI = DB_DIR
LANCEDB_TABLE_NAME = os.getenv("LANCEDB_TABLE_NAME", "rag_table")

# DeepSeek API配置
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "http://192.168.188.146:1234/v1")
DEEPSEEK_CHAT_MODEL = os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek-r1-distill-qwen-14b")
DEEPSEEK_EMBEDDING_MODEL = os.getenv("DEEPSEEK_EMBEDDING_MODEL", "text-embedding-nomic-embed-text-v1.5")
DEEPSEEK_MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", 1000))
DEEPSEEK_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", 0.7))

# RAG配置
TOP_K = int(os.getenv("TOP_K", 3))

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logging():
    """
    设置项目的统一日志配置。

    这个函数应该在应用启动时调用一次，确保整个项目使用统一的日志设置。
    """
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        force=True  # 强制重新配置，覆盖之前的设置
    )

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的logger实例。

    Args:
        name (str): logger的名称，通常使用模块的 __name__

    Returns:
        logging.Logger: 配置好的logger实例
    """
    return logging.getLogger(name)

# 确保目录存在
def ensure_directories():
    """确保必要的目录存在。"""
    DATA_DIR.mkdir(exist_ok=True)
    DB_DIR.mkdir(exist_ok=True)
