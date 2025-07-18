#!/bin/bash

# 同时推送到阿里云和GitHub的便捷脚本

echo "=== 双仓库推送脚本 ==="
echo ""

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD --; then
    echo "检测到未提交的更改，正在添加和提交..."
    
    # 显示当前状态
    echo ""
    echo "当前状态："
    git status --short
    echo ""
    
    # 添加所有更改
    git add .
    
    # 获取提交信息
    if [ -z "$1" ]; then
        read -p "请输入提交信息: " commit_message
        if [ -z "$commit_message" ]; then
            commit_message="Update project files - $(date '+%Y-%m-%d %H:%M:%S')"
        fi
    else
        commit_message="$1"
    fi
    
    # 提交更改
    git commit -m "$commit_message"
    
    if [ $? -ne 0 ]; then
        echo "❌ 提交失败"
        exit 1
    fi
    
    echo "✅ 更改已提交"
else
    echo "没有检测到未提交的更改"
fi

echo ""
echo "开始推送到远程仓库..."

# 推送到阿里云
echo ""
echo "正在推送到阿里云 (origin)..."
git push origin master

if [ $? -eq 0 ]; then
    echo "✅ 成功推送到阿里云"
    aliyun_success=true
else
    echo "❌ 推送到阿里云失败"
    aliyun_success=false
fi

# 推送到GitHub
echo ""
echo "正在推送到GitHub..."
git push github master

if [ $? -eq 0 ]; then
    echo "✅ 成功推送到GitHub"
    github_success=true
else
    echo "❌ 推送到GitHub失败"
    github_success=false
fi

# 总结结果
echo ""
echo "=== 推送结果总结 ==="
if [ "$aliyun_success" = true ]; then
    echo "✅ 阿里云: 成功"
else
    echo "❌ 阿里云: 失败"
fi

if [ "$github_success" = true ]; then
    echo "✅ GitHub: 成功"
else
    echo "❌ GitHub: 失败"
fi

if [ "$aliyun_success" = true ] && [ "$github_success" = true ]; then
    echo ""
    echo "🎉 所有仓库推送成功！"
elif [ "$aliyun_success" = true ] || [ "$github_success" = true ]; then
    echo ""
    echo "⚠️  部分仓库推送成功，请检查失败的仓库"
else
    echo ""
    echo "❌ 所有仓库推送失败，请检查网络连接和权限设置"
fi

echo ""
echo "=== 脚本执行完成 ==="
