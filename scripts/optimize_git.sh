#!/bin/bash

# Git配置优化脚本
# 用于优化Git上传性能和处理大文件

echo "🚀 开始Git配置优化..."

# 1. 增加HTTP缓冲区大小 (500MB)
echo "📦 设置HTTP缓冲区大小..."
git config --global http.postBuffer 524288000

# 2. 启用最大压缩
echo "🗜️  启用压缩..."
git config --global core.compression 9

# 3. 设置超时时间
echo "⏰ 设置超时配置..."
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# 4. 启用并行处理
echo "⚡ 启用并行处理..."
git config --global pack.threads 0

# 5. 优化网络设置
echo "🌐 优化网络设置..."
git config --global http.version HTTP/1.1
git config --global http.keepalive true

# 6. 设置更大的包文件大小限制
echo "📁 设置包文件限制..."
git config --global pack.packSizeLimit 2g

# 7. 显示当前配置
echo "✅ Git配置优化完成！当前相关配置："
echo "HTTP缓冲区: $(git config --global http.postBuffer)"
echo "压缩级别: $(git config --global core.compression)"
echo "包线程数: $(git config --global pack.threads)"

echo "🎉 Git优化配置完成！"
