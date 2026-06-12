@echo off
chcp 65001 >nul
cd /d D:\HugoBlog\myblog

echo ================================
echo Hugo Blog 一键发布
echo ================================

echo.
echo [1/5] 检查 Hugo 构建...
hugo --gc --minify
if errorlevel 1 (
    echo.
    echo Hugo 构建失败，已停止发布。
    pause
    exit /b 1
)

echo.
echo [2/5] 查看 Git 状态...
git status

echo.
echo [3/5] 添加所有变更...
git add -A

echo.
echo [4/5] 创建提交...
set commit_msg=update blog %date% %time%
git commit -m "%commit_msg%"

echo.
echo [5/5] 推送到 GitHub...
git push

echo.
echo ================================
echo 发布命令已执行完成。
echo 请去 GitHub Actions 检查是否绿色成功。
echo ================================
pause