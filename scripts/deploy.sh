#!/bin/bash

# 一键部署脚本
# 结合清理、Git优化和上传功能

set -e

echo "🚀 RAG项目一键部署脚本"
echo "=========================="

# 1. 检查Git仓库状态
if [ ! -d ".git" ]; then
    echo "📁 初始化Git仓库..."
    git init
    echo "✅ Git仓库初始化完成"
fi

# 2. 运行Git优化配置
echo "⚙️  优化Git配置..."
if [ -f "scripts/optimize_git.sh" ]; then
    chmod +x scripts/optimize_git.sh
    ./scripts/optimize_git.sh
else
    echo "⚠️  未找到Git优化脚本，跳过优化"
fi

# 3. 清理项目文件
echo "🧹 清理项目文件..."
if [ -f "scripts/clean_project.sh" ]; then
    chmod +x scripts/clean_project.sh
    ./scripts/clean_project.sh
else
    echo "⚠️  未找到清理脚本，手动清理..."
    # 基本清理
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    rm -rf temp/ tmp/ logs/ 2>/dev/null || true
fi

# 4. 检查.gitignore
if [ ! -f ".gitignore" ]; then
    echo "⚠️  未找到.gitignore文件，创建基本版本..."
    cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
venv/
db/
*.log
.DS_Store
temp/
tmp/
EOF
fi

# 5. 添加文件到Git
echo "📦 添加文件到Git..."
git add .gitignore
git add scripts/
git add src/
git add main.py requirements.txt README.md

# 检查是否有data目录的小文件
if [ -d "data" ]; then
    # 只添加小于1MB的文件
    find data -type f -size -1M -exec git add {} \;
    echo "✅ 已添加data目录中的小文件"
fi

# 6. 提交更改
echo "💾 提交更改..."
if git diff --staged --quiet; then
    echo "ℹ️  没有需要提交的更改"
else
    git commit -m "项目初始化: 添加核心代码和配置文件

- 添加RAG系统核心代码
- 配置Git优化设置
- 添加项目部署脚本
- 更新.gitignore规则"
    echo "✅ 更改已提交"
fi

# 7. 推送到远程仓库（如果已配置）
echo "🌐 检查远程仓库..."
if git remote | grep -q origin; then
    read -p "🤔 是否推送到远程仓库? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 推送到远程仓库..."
        git push -u origin main || git push -u origin master
        echo "✅ 推送完成"
    fi
else
    echo "ℹ️  未配置远程仓库"
    echo "💡 要添加远程仓库，请运行:"
    echo "   git remote add origin <your-repo-url>"
    echo "   git push -u origin main"
fi

echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 项目已准备就绪，包含以下脚本:"
echo "   scripts/setup_project.sh    - 新环境快速部署"
echo "   scripts/setup_project.bat   - Windows环境部署"
echo "   scripts/optimize_git.sh     - Git性能优化"
echo "   scripts/clean_project.sh    - 项目文件清理"
echo ""
echo "🔄 在新环境中部署项目:"
echo "   1. git clone <your-repo-url>"
echo "   2. cd <project-directory>"
echo "   3. chmod +x scripts/setup_project.sh"
echo "   4. ./scripts/setup_project.sh"
