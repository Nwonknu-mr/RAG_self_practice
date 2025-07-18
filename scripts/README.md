# 项目部署脚本说明

本目录包含了RAG项目的自动化部署和管理脚本，帮助您快速在不同环境中部署和管理项目。

## 📁 脚本文件说明

### 🚀 部署相关脚本

#### `deploy.sh` - 一键部署脚本
**用途**: 完整的项目部署流程，包括清理、Git优化和上传
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

#### `setup_project.sh` - Linux/Mac环境设置
**用途**: 在新环境中快速重建项目环境
```bash
chmod +x scripts/setup_project.sh
./scripts/setup_project.sh
```

#### `setup_project.bat` - Windows环境设置
**用途**: Windows系统下的项目环境设置
```cmd
scripts\setup_project.bat
```

### ⚙️ 优化和清理脚本

#### `optimize_git.sh` - Git性能优化
**用途**: 优化Git配置以提高大文件上传性能
```bash
chmod +x scripts/optimize_git.sh
./scripts/optimize_git.sh
```

#### `clean_project.sh` - 项目清理
**用途**: 清理不需要上传的文件，为Git提交做准备
```bash
chmod +x scripts/clean_project.sh
./scripts/clean_project.sh
```

### 🔄 双仓库管理脚本

#### `setup_dual_remote.sh` / `setup_dual_remote.bat` - 双远程仓库设置
**用途**: 设置同时推送到阿里云和GitHub的双仓库配置
```bash
# Linux/Mac
chmod +x scripts/setup_dual_remote.sh
./scripts/setup_dual_remote.sh

# Windows
scripts\setup_dual_remote.bat
```

#### `push_to_both.sh` / `push_to_both.bat` - 双仓库同步推送
**用途**: 一键同时推送代码到阿里云和GitHub
```bash
# Linux/Mac
./scripts/push_to_both.sh "提交信息"

# Windows
scripts\push_to_both.bat "提交信息"
```

## 🔄 典型使用流程

### 首次部署到GitHub
```bash
# 1. 运行一键部署脚本
./scripts/deploy.sh

# 2. 添加远程仓库（如果还没有）
git remote add origin https://github.com/username/repo.git

# 3. 推送到GitHub
git push -u origin main
```

### 在新环境中部署项目
```bash
# 1. 克隆仓库
git clone https://github.com/username/repo.git
cd repo

# 2. 运行环境设置脚本
chmod +x scripts/setup_project.sh
./scripts/setup_project.sh

# 3. 开始使用
source venv/bin/activate
python main.py ask
```

### 设置双仓库管理（阿里云 + GitHub）
```bash
# 1. 确保您已在GitHub上创建对应仓库
# 2. 运行双仓库设置脚本
./scripts/setup_dual_remote.sh

# 3. 按提示输入GitHub仓库URL
# 4. 选择是否立即推送到两个仓库

# 5. 日常使用 - 同时推送到两个仓库
./scripts/push_to_both.sh "更新说明"
```

### 手动双仓库管理
```bash
# 查看当前远程仓库配置
git remote -v

# 分别推送到不同仓库
git push origin master    # 推送到阿里云
git push github master    # 推送到GitHub

# 同时推送到两个仓库
git push origin master && git push github master
```

## 📋 脚本功能详解

### Git优化配置
- HTTP缓冲区大小: 500MB
- 压缩级别: 最大(9)
- 超时设置: 无限制
- 并行处理: 启用
- 包文件限制: 2GB

### 自动创建的目录结构
```
project/
├── db/                 # 数据库文件（自动重建）
├── data/
│   ├── large_documents/
│   └── embeddings/
├── temp/              # 临时文件
├── logs/              # 日志文件
└── venv/              # 虚拟环境（自动重建）
```

### 被.gitignore排除的文件
- `venv/` - 虚拟环境
- `db/` - 数据库文件
- `__pycache__/` - Python缓存
- `*.log` - 日志文件
- 临时文件和系统文件

## 🛠️ 故障排除

### 权限问题
```bash
# 给所有脚本添加执行权限
chmod +x scripts/*.sh
```

### Python版本问题
确保系统安装了Python 3.9+:
```bash
python3 --version
```

### Git推送失败
如果推送大文件失败，可以：
1. 运行Git优化脚本
2. 使用Git LFS处理大文件
3. 分批推送文件

### 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 清理pip缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt
```

## 💡 最佳实践

1. **首次部署前**: 运行`clean_project.sh`清理不必要的文件
2. **定期维护**: 使用`optimize_git.sh`保持Git性能
3. **新环境部署**: 始终使用`setup_project.sh`确保环境一致性
4. **大文件处理**: 考虑使用Git LFS或外部存储

## 🔗 相关链接

- [Git LFS文档](https://git-lfs.github.io/)
- [Python虚拟环境指南](https://docs.python.org/3/tutorial/venv.html)
- [GitHub大文件处理](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
