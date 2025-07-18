#!/bin/bash

# RAG项目快速部署脚本
# 用于在新环境中快速重建项目环境和数据库

set -e  # 遇到错误立即退出

echo "🚀 开始RAG项目环境设置..."

# 检查Python版本
echo "🐍 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: 需要Python 3.9+，当前版本: $python_version"
    exit 1
fi
echo "✅ Python版本检查通过: $python_version"

# 1. 创建虚拟环境
echo "📦 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "ℹ️  虚拟环境已存在，跳过创建"
fi

# 2. 激活虚拟环境并安装依赖
echo "📚 安装项目依赖..."
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "❌ 未找到requirements.txt文件"
    exit 1
fi

# 3. 创建必要的目录结构
echo "📁 创建目录结构..."
mkdir -p db
mkdir -p data/large_documents
mkdir -p data/embeddings
mkdir -p temp
mkdir -p logs
echo "✅ 目录结构创建完成"

# 4. 检查配置文件
echo "⚙️  检查配置文件..."
if [ ! -f "src/config.py" ]; then
    echo "❌ 未找到配置文件 src/config.py"
    exit 1
fi

# 5. 初始化数据库（如果有测试数据）
echo "🗄️  初始化数据库..."
if [ -f "data/test_document1.txt" ] && [ -f "data/test_document2.txt" ]; then
    echo "📄 发现测试文档，开始索引..."
    python main.py index
    echo "✅ 测试数据索引完成"
else
    echo "ℹ️  未发现测试文档，跳过自动索引"
    echo "💡 提示: 请将文档放入data/目录，然后运行 'python main.py index'"
fi

# 6. 运行基本测试
echo "🧪 运行基本测试..."
python -c "
import sys
sys.path.append('src')
try:
    from config import get_logger
    from vector_store import VectorStore
    print('✅ 核心模块导入测试通过')
except ImportError as e:
    print(f'❌ 模块导入失败: {e}')
    sys.exit(1)
"

echo ""
echo "🎉 RAG项目环境设置完成！"
echo ""
echo "📋 接下来的步骤："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 添加文档到data/目录"
echo "3. 运行索引: python main.py index"
echo "4. 启动聊天: python main.py ask"
echo "5. 启动API服务: python main.py serve"
echo ""
echo "📖 更多信息请查看README.md"
