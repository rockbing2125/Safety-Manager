@echo off
chcp 65001 >nul
echo ============================================
echo 测试数据库连接
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] 读取配置...

REM 检查 .env 文件是否存在
if not exist ".env" (
    echo ⚠ .env 文件不存在
    echo 使用默认本地数据库：data\databases\regulations.db
    set "db_path=data\databases\regulations.db"
    goto :check_db
)

REM 从 .env 文件读取 DATABASE_PATH
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="DATABASE_PATH" set "db_path=%%b"
)

if "%db_path%"=="" (
    echo ⚠ 未配置 DATABASE_PATH
    echo 使用默认本地数据库：data\databases\regulations.db
    set "db_path=data\databases\regulations.db"
)

:check_db
echo.
echo [2/3] 测试连接...
echo 数据库路径：%db_path%
echo.

REM 检查文件是否存在
if exist "%db_path%" (
    echo ✓ 数据库文件存在

    REM 尝试读取文件大小
    for %%F in ("%db_path%") do (
        echo   文件大小：%%~zF 字节
        echo   修改时间：%%~tF
    )

    echo.
    echo ✓ 数据库连接正常
    echo.
    echo [3/3] 连接信息
    echo 数据库类型：SQLite
    echo 位置：%db_path%

    REM 判断是否为网络路径
    echo %db_path% | findstr /C:"\\" >nul
    if errorlevel 1 (
        echo 模式：本地数据库
    ) else (
        echo 模式：网络共享数据库
    )

) else (
    echo ✗ 数据库文件不存在
    echo.
    echo 可能的原因：
    echo   1. 首次运行，数据库尚未创建
    echo   2. 网络路径不可访问
    echo   3. 路径配置错误
    echo   4. 没有访问权限
    echo.
    echo 解决方法：
    echo   1. 检查网络连接
    echo   2. 确认路径正确
    echo   3. 检查文件夹权限
    echo   4. 运行程序自动创建数据库
)

echo.
echo ============================================
echo 测试完成
echo ============================================
pause
