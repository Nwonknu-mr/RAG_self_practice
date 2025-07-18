@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 开始RAG项目环境设置...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)

echo ✅ Python检查通过

REM 1. 创建虚拟环境
echo 📦 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo ✅ 虚拟环境创建完成
) else (
    echo ℹ️  虚拟环境已存在，跳过创建
)

REM 2. 激活虚拟环境并安装依赖
echo 📚 安装项目依赖...
call venv\Scripts\activate.bat

REM 升级pip
python -m pip install --upgrade pip

REM 安装依赖
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ 依赖安装完成
) else (
    echo ❌ 未找到requirements.txt文件
    pause
    exit /b 1
)

REM 3. 创建必要的目录结构
echo 📁 创建目录结构...
if not exist "db" mkdir db
if not exist "data\large_documents" mkdir data\large_documents
if not exist "data\embeddings" mkdir data\embeddings
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
echo ✅ 目录结构创建完成

REM 4. 检查配置文件
echo ⚙️  检查配置文件...
if not exist "src\config.py" (
    echo ❌ 未找到配置文件 src\config.py
    pause
    exit /b 1
)

REM 5. 初始化数据库（如果有测试数据）
echo 🗄️  初始化数据库...
if exist "data\test_document1.txt" if exist "data\test_document2.txt" (
    echo 📄 发现测试文档，开始索引...
    python main.py index
    echo ✅ 测试数据索引完成
) else (
    echo ℹ️  未发现测试文档，跳过自动索引
    echo 💡 提示: 请将文档放入data\目录，然后运行 'python main.py index'
)

REM 6. 运行基本测试
echo 🧪 运行基本测试...
python -c "import sys; sys.path.append('src'); from config import get_logger; from vector_store import VectorStore; print('✅ 核心模块导入测试通过')" 2>nul
if errorlevel 1 (
    echo ❌ 模块导入测试失败
    pause
    exit /b 1
)

echo.
echo 🎉 RAG项目环境设置完成！
echo.
echo 📋 接下来的步骤：
echo 1. 激活虚拟环境: venv\Scripts\activate.bat
echo 2. 添加文档到data\目录
echo 3. 运行索引: python main.py index
echo 4. 启动聊天: python main.py ask
echo 5. 启动API服务: python main.py serve
echo.
echo 📖 更多信息请查看README.md
pause
