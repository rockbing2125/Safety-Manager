@echo off
chcp 65001 >nul
echo ============================================
echo 配置共享数据库（多用户使用）
echo ============================================
echo.
echo 此脚本帮助您配置网络共享数据库，
echo 以便多台电脑可以接收推送更新。
echo.
echo 当前问题：推送更新只在本机生效，其他电脑看不到
echo 解决方案：所有电脑使用同一个共享数据库文件
echo.
pause

cd /d "%~dp0"

echo.
echo ============================================
echo 步骤 1：选择共享方式
echo ============================================
echo.
echo [1] 使用网络共享路径（推荐，局域网内）
echo     例如：\\192.168.1.100\SafetyManager\regulations.db
echo.
echo [2] 使用映射网络驱动器
echo     例如：Z:\SafetyManager\regulations.db
echo.
echo [3] 仍使用本地数据库（取消配置）
echo.
set /p choice="请选择 [1/2/3]: "

if "%choice%"=="3" (
    echo 已取消配置
    pause
    exit /b 0
)

if "%choice%"=="1" (
    echo.
    echo ============================================
    echo 步骤 2：输入网络共享路径
    echo ============================================
    echo.
    echo 格式示例：
    echo   \\192.168.1.100\SafetyManager\regulations.db
    echo   \\公司服务器\共享文件夹\SafetyManager\regulations.db
    echo.
    set /p db_path="请输入完整路径: "
)

if "%choice%"=="2" (
    echo.
    echo ============================================
    echo 步骤 2：输入网络驱动器路径
    echo ============================================
    echo.
    echo 格式示例：
    echo   Z:\SafetyManager\regulations.db
    echo.
    set /p db_path="请输入完整路径: "
)

echo.
echo ============================================
echo 步骤 3：确认配置
echo ============================================
echo.
echo 将配置数据库路径为：
echo %db_path%
echo.
set /p confirm="确认配置？[Y/N]: "

if /i not "%confirm%"=="Y" (
    echo 已取消配置
    pause
    exit /b 0
)

echo.
echo ============================================
echo 步骤 4：写入配置文件
echo ============================================
echo.

REM 创建或更新 .env 文件
echo # 数据库配置 > .env
echo DATABASE_PATH=%db_path% >> .env
echo. >> .env
echo # 其他配置保持默认 >> .env
echo OFFLINE_MODE=True >> .env
echo LOG_LEVEL=INFO >> .env

echo ✓ 配置已写入 .env 文件
echo.

echo ============================================
echo 步骤 5：验证配置
echo ============================================
echo.

REM 检查路径是否可访问
if exist "%db_path%" (
    echo ✓ 数据库文件存在：%db_path%
) else (
    echo ⚠ 数据库文件不存在，将在首次运行时创建
    echo.
    echo 提示：请确保：
    echo   1. 网络路径可访问
    echo   2. 有读写权限
    echo   3. 目标文件夹已创建
)

echo.
echo ============================================
echo 配置完成！
echo ============================================
echo.
echo 下一步：
echo   1. 在其他电脑上运行此脚本，使用相同的路径
echo   2. 重启程序以加载新配置
echo   3. 推送更新后，所有电脑都能收到
echo.
echo 注意事项：
echo   • 所有电脑必须使用相同的数据库路径
echo   • 确保网络稳定，路径可访问
echo   • 建议定期备份数据库文件
echo.

pause
