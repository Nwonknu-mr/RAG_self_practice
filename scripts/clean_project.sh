#!/bin/bash

# 项目清理脚本
# 用于清理不需要上传到GitHub的文件，为上传做准备

echo "🧹 开始清理项目文件..."

# 1. 清理Python缓存文件
echo "🐍 清理Python缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true
echo "✅ Python缓存清理完成"

# 2. 清理虚拟环境（可选）
read -p "🤔 是否删除虚拟环境目录? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "venv" ]; then
        rm -rf venv
        echo "✅ 虚拟环境已删除"
    else
        echo "ℹ️  虚拟环境目录不存在"
    fi
else
    echo "ℹ️  保留虚拟环境目录"
fi

# 3. 清理数据库文件（可选）
read -p "🗄️  是否删除数据库文件? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "db" ]; then
        rm -rf db
        echo "✅ 数据库文件已删除"
    else
        echo "ℹ️  数据库目录不存在"
    fi
else
    echo "ℹ️  保留数据库文件"
fi

# 4. 清理临时文件
echo "🗑️  清理临时文件..."
rm -rf temp/ tmp/ 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.orig" -delete 2>/dev/null || true
echo "✅ 临时文件清理完成"

# 5. 清理日志文件
echo "📝 清理日志文件..."
rm -rf logs/ 2>/dev/null || true
find . -name "*.log" -delete 2>/dev/null || true
echo "✅ 日志文件清理完成"

# 6. 清理系统文件
echo "💻 清理系统文件..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true
echo "✅ 系统文件清理完成"

# 7. 显示清理后的项目大小
echo "📊 清理后的项目统计:"
if command -v du >/dev/null 2>&1; then
    echo "项目总大小: $(du -sh . | cut -f1)"
fi

if command -v find >/dev/null 2>&1; then
    file_count=$(find . -type f | wc -l)
    echo "文件总数: $file_count"
fi

echo ""
echo "🎉 项目清理完成！"
echo "💡 提示: 现在可以安全地提交到Git仓库"
echo "📋 建议的下一步操作:"
echo "   git add ."
echo "   git commit -m '项目初始化'"
echo "   git push origin main"
