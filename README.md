# 智能RAG问答系统

## 项目概述
基于Python的智能RAG (检索增强生成) 系统，集成DeepSeek API。系统具备自动学习能力，当检索文档相关度不高时，会使用模型直接回答并将问答对保存到知识库中，实现持续学习。

## 核心特性
- **智能检索**: 基于向量相似度的语义搜索
- **DeepSeek集成**: 使用DeepSeek API进行文本生成
- **自动学习**: 低相关度问题自动保存到知识库
- **多种接口**: 命令行、API服务、演示脚本
- **多格式支持**: PDF、DOCX、TXT、MD等文档格式
- **高性能**: LanceDB向量数据库，快速检索

## 技术栈
- **语言**: Python 3.9+
- **向量数据库**: LanceDB
- **文本处理**: LangChain
- **API框架**: FastAPI
- **LLM集成**: DeepSeek API
- **文档处理**: pypdf, python-docx, unstructured

## 项目结构
```
RAG训练/
├── src/                    # 核心源代码
│   ├── config.py          # 配置管理
│   ├── document_loader.py # 文档加载器
│   ├── text_splitter.py   # 文本分割器
│   ├── embedding_model.py # 嵌入模型 (DeepSeek API)
│   ├── vector_store.py    # 向量存储 (LanceDB)
│   ├── rag_pipeline.py    # RAG主流程
│   ├── indexing.py        # 索引流程
│   └── api.py             # FastAPI服务
├── data/                   # 数据文件
│   ├── test_document1.txt # 测试文档
│   ├── test_document2.txt # 测试文档
│   └── generated_qa.txt   # 自动生成的问答对
├── db/                     # LanceDB数据库文件
├── main.py                # 主程序入口
├── demo.py                # 演示脚本
└── requirements.txt       # 依赖文件
```

## 快速开始

### 1. 环境准备
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置DeepSeek API
确保您的DeepSeek API服务正在运行在 `http://192.168.188.146:1234`

### 3. 索引文档
```bash
# 索引data目录下的所有文档
python main.py index

# 重新索引（删除旧数据）
python main.py index --reindex
```

### 4. 开始问答
```bash
# 交互式问答
python main.py ask

# 启动API服务
python main.py serve

# 运行演示
python demo.py
```

## 使用示例

### 命令行问答
```bash
$ python main.py ask
欢迎使用RAG问答系统！输入'exit'退出。

请输入您的问题: 什么是RAG系统？

--- 回答 ---
RAG系统是检索增强生成（Retrieval-Augmented Generation）的缩写...

(响应时间 2.34s)
```

### API调用
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是RAG系统？"}'
```

## 智能学习机制

系统具备自动学习能力：
1. **高相关度**: 使用检索到的文档上下文回答
2. **低相关度**: 使用模型直接回答，并保存问答对到 `data/generated_qa.txt`
3. **持续改进**: 下次重新索引时包含新的问答对，提升回答质量

## 系统性能
- **索引速度**: ~0.1秒处理多个文档
- **检索速度**: 毫秒级向量搜索
- **回答质量**: 基于DeepSeek模型的高质量中文回答
- **存储效率**: LanceDB高效向量存储

## 配置说明

主要配置项在 `src/config.py` 中：
- `DEEPSEEK_API_BASE`: DeepSeek API地址
- `DEEPSEEK_CHAT_MODEL`: 聊天模型名称
- `DEEPSEEK_EMBEDDING_MODEL`: 嵌入模型名称
- `TOP_K`: 检索返回的文档数量
- `RELEVANCE_THRESHOLD`: 相关度阈值

## API文档

启动服务后访问: http://127.0.0.1:8000/docs

