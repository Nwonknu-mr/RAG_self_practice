#!/bin/bash

# 设置双远程仓库脚本
# 用于同时推送到阿里云和GitHub

echo "=== 双远程仓库设置脚本 ==="
echo ""

# 检查当前远程仓库
echo "当前远程仓库配置："
git remote -v
echo ""

# 提示用户输入GitHub仓库URL
echo "请确保您已在GitHub上创建了仓库，然后输入GitHub仓库的URL："
echo "格式示例: https://github.com/username/repository-name.git"
echo "或者: git@github.com:username/repository-name.git"
read -p "GitHub仓库URL: " github_url

if [ -z "$github_url" ]; then
    echo "错误：GitHub仓库URL不能为空"
    exit 1
fi

# 添加GitHub远程仓库
echo ""
echo "正在添加GitHub远程仓库..."
git remote add github "$github_url"

if [ $? -eq 0 ]; then
    echo "✅ GitHub远程仓库添加成功"
else
    echo "❌ GitHub远程仓库添加失败"
    exit 1
fi

# 显示更新后的远程仓库配置
echo ""
echo "更新后的远程仓库配置："
git remote -v
echo ""

# 提示推送选项
echo "=== 推送选项 ==="
echo "现在您可以使用以下命令进行推送："
echo ""
echo "1. 推送到阿里云 (origin):"
echo "   git push origin master"
echo ""
echo "2. 推送到GitHub:"
echo "   git push github master"
echo ""
echo "3. 同时推送到两个仓库:"
echo "   git push origin master && git push github master"
echo ""

# 询问是否立即推送
read -p "是否现在就推送到两个仓库？(y/n): " push_now

if [ "$push_now" = "y" ] || [ "$push_now" = "Y" ]; then
    echo ""
    echo "正在提交当前更改..."
    
    # 添加所有更改
    git add .
    
    # 提交更改
    read -p "请输入提交信息: " commit_message
    if [ -z "$commit_message" ]; then
        commit_message="Update project files"
    fi
    
    git commit -m "$commit_message"
    
    echo ""
    echo "正在推送到阿里云..."
    git push origin master
    
    echo ""
    echo "正在推送到GitHub..."
    git push github master
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 成功推送到两个仓库！"
    else
        echo ""
        echo "❌ 推送过程中出现错误，请检查网络连接和仓库权限"
    fi
else
    echo ""
    echo "设置完成！您可以稍后手动推送。"
fi

echo ""
echo "=== 脚本执行完成 ==="
