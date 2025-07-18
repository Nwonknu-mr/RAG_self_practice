@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo === 双远程仓库设置脚本 ===
echo.

REM 检查当前远程仓库
echo 当前远程仓库配置：
git remote -v
echo.

REM 提示用户输入GitHub仓库URL
echo 请确保您已在GitHub上创建了仓库，然后输入GitHub仓库的URL：
echo 格式示例: https://github.com/username/repository-name.git
echo 或者: git@github.com:username/repository-name.git
set /p github_url="GitHub仓库URL: "

if "%github_url%"=="" (
    echo 错误：GitHub仓库URL不能为空
    pause
    exit /b 1
)

REM 添加GitHub远程仓库
echo.
echo 正在添加GitHub远程仓库...
git remote add github "%github_url%"

if %errorlevel% equ 0 (
    echo ✅ GitHub远程仓库添加成功
) else (
    echo ❌ GitHub远程仓库添加失败
    pause
    exit /b 1
)

REM 显示更新后的远程仓库配置
echo.
echo 更新后的远程仓库配置：
git remote -v
echo.

REM 提示推送选项
echo === 推送选项 ===
echo 现在您可以使用以下命令进行推送：
echo.
echo 1. 推送到阿里云 (origin):
echo    git push origin master
echo.
echo 2. 推送到GitHub:
echo    git push github master
echo.
echo 3. 同时推送到两个仓库:
echo    git push origin master ^&^& git push github master
echo.

REM 询问是否立即推送
set /p push_now="是否现在就推送到两个仓库？(y/n): "

if /i "%push_now%"=="y" (
    echo.
    echo 正在提交当前更改...
    
    REM 添加所有更改
    git add .
    
    REM 提交更改
    set /p commit_message="请输入提交信息: "
    if "!commit_message!"=="" set commit_message=Update project files
    
    git commit -m "!commit_message!"
    
    echo.
    echo 正在推送到阿里云...
    git push origin master
    
    echo.
    echo 正在推送到GitHub...
    git push github master
    
    if %errorlevel% equ 0 (
        echo.
        echo ✅ 成功推送到两个仓库！
    ) else (
        echo.
        echo ❌ 推送过程中出现错误，请检查网络连接和仓库权限
    )
) else (
    echo.
    echo 设置完成！您可以稍后手动推送。
)

echo.
echo === 脚本执行完成 ===
pause
