@echo off
chcp 65001 >nul
echo ============================================
echo 清理工程临时文件
echo ============================================
echo.

cd /d "%~dp0"

echo [1/6] 清理 Python 缓存...
if exist "__pycache__" (
    rmdir /s /q "__pycache__"
    echo ✓ 已删除根目录 __pycache__
)
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d" 2>nul
    echo ✓ 已删除 %%d
)
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo ✓ Python 缓存清理完成

echo.
echo [2/6] 清理构建产物...
if exist "build" (
    rmdir /s /q "build"
    echo ✓ 已删除 build 目录
)
if exist "dist" (
    rmdir /s /q "dist"
    echo ✓ 已删除 dist 目录
)
del /s /q *.spec.bak 2>nul
echo ✓ 构建产物清理完成

echo.
echo [3/6] 清理日志文件...
if exist "data\logs" (
    del /q "data\logs\*.log" 2>nul
    echo ✓ 已清理日志文件
)

echo.
echo [4/6] 清理临时文件...
del /q nul 2>nul
del /q *.bak 2>nul
del /q bash.exe.stackdump 2>nul
del /q compare_db.py 2>nul
del /q sync_db_to_dist.bat 2>nul
del /q rebuild_quick.bat 2>nul
del /q test_direct_run.bat 2>nul
echo ✓ 临时文件清理完成

echo.
echo [5/6] 清理 IDE 配置...
if exist ".vscode" (
    rmdir /s /q ".vscode"
    echo ✓ 已删除 .vscode
)
if exist ".idea" (
    rmdir /s /q ".idea"
    echo ✓ 已删除 .idea
)
del /q .DS_Store 2>nul
echo ✓ IDE 配置清理完成

echo.
echo [6/6] 清理用户数据（可选）...
echo ⚠ 以下操作会删除开发环境的数据库和用户数据
set /p clean_data="是否清理用户数据？(Y/N，默认N): "
if /i "%clean_data%"=="Y" (
    del /q "data\databases\*.db" 2>nul
    del /q "data\databases\*.sqlite" 2>nul
    if exist "data\documents" rmdir /s /q "data\documents" 2>nul
    if exist "data\codes" rmdir /s /q "data\codes" 2>nul
    if exist "data\parameter_images" rmdir /s /q "data\parameter_images" 2>nul
    echo ✓ 用户数据已清理
) else (
    echo [跳过] 保留用户数据
)

echo.
echo ============================================
echo 清理完成！
echo ============================================
echo.
echo 工程已准备好提交到版本控制系统
echo.

pause
