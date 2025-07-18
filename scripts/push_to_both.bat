@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo === 双仓库推送脚本 ===
echo.

REM 检查是否有未提交的更改
git diff-index --quiet HEAD -- >nul 2>&1
if %errorlevel% neq 0 (
    echo 检测到未提交的更改，正在添加和提交...
    
    REM 显示当前状态
    echo.
    echo 当前状态：
    git status --short
    echo.
    
    REM 添加所有更改
    git add .
    
    REM 获取提交信息
    if "%~1"=="" (
        set /p commit_message="请输入提交信息: "
        if "!commit_message!"=="" (
            for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set current_date=%%c-%%a-%%b
            for /f "tokens=1-2 delims=: " %%a in ('time /t') do set current_time=%%a:%%b
            set commit_message=Update project files - !current_date! !current_time!
        )
    ) else (
        set commit_message=%~1
    )
    
    REM 提交更改
    git commit -m "!commit_message!"
    
    if %errorlevel% neq 0 (
        echo ❌ 提交失败
        pause
        exit /b 1
    )
    
    echo ✅ 更改已提交
) else (
    echo 没有检测到未提交的更改
)

echo.
echo 开始推送到远程仓库...

REM 推送到阿里云
echo.
echo 正在推送到阿里云 (origin)...
git push origin master

if %errorlevel% equ 0 (
    echo ✅ 成功推送到阿里云
    set aliyun_success=true
) else (
    echo ❌ 推送到阿里云失败
    set aliyun_success=false
)

REM 推送到GitHub
echo.
echo 正在推送到GitHub...
git push github master

if %errorlevel% equ 0 (
    echo ✅ 成功推送到GitHub
    set github_success=true
) else (
    echo ❌ 推送到GitHub失败
    set github_success=false
)

REM 总结结果
echo.
echo === 推送结果总结 ===
if "!aliyun_success!"=="true" (
    echo ✅ 阿里云: 成功
) else (
    echo ❌ 阿里云: 失败
)

if "!github_success!"=="true" (
    echo ✅ GitHub: 成功
) else (
    echo ❌ GitHub: 失败
)

if "!aliyun_success!"=="true" if "!github_success!"=="true" (
    echo.
    echo 🎉 所有仓库推送成功！
) else if "!aliyun_success!"=="true" (
    echo.
    echo ⚠️  部分仓库推送成功，请检查失败的仓库
) else if "!github_success!"=="true" (
    echo.
    echo ⚠️  部分仓库推送成功，请检查失败的仓库
) else (
    echo.
    echo ❌ 所有仓库推送失败，请检查网络连接和权限设置
)

echo.
echo === 脚本执行完成 ===
pause
