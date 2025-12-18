@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ============================================
echo 数据库同步工具
echo ============================================
echo.
echo 此工具用于同步网络共享数据库到本地，以便打包
echo.

REM 读取.env文件中的DATABASE_PATH配置
set "network_db="
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if "%%a"=="DATABASE_PATH" set "network_db=%%b"
    )
)

if not defined network_db (
    echo ✗ .env文件中未配置DATABASE_PATH
    echo   当前使用本地数据库，无需同步
    pause
    exit /b 0
)

echo 检测到网络数据库配置：
echo %network_db%
echo.

REM 检查网络数据库是否可访问
if not exist "%network_db%" (
    echo ✗ 无法访问网络数据库！
    echo.
    echo 可能的原因：
    echo 1. 网络连接断开
    echo 2. 共享服务器离线
    echo 3. 没有访问权限
    echo 4. 路径配置错误
    echo.
    echo 请检查：
    echo 1. 网络连接是否正常
    echo 2. 能否访问 \\10.0.104.252
    echo 3. SafetyManager 共享文件夹是否存在
    echo.
    pause
    exit /b 1
)

echo ✓ 网络数据库可访问
echo.

REM 显示文件信息
echo 网络数据库信息：
for %%F in ("%network_db%") do (
    echo   大小: %%~zF 字节
    echo   修改时间: %%~tF
)
echo.

echo 本地数据库信息：
if exist "data\databases\regulations.db" (
    for %%F in ("data\databases\regulations.db") do (
        echo   大小: %%~zF 字节
        echo   修改时间: %%~tF
    )
) else (
    echo   ✗ 本地数据库不存在
)
echo.

REM 对比修改时间
echo 正在对比数据库内容...
python -c "import sqlite3; n_conn = sqlite3.connect(r'%network_db%'); l_conn = sqlite3.connect(r'data\databases\regulations.db'); n_cur = n_conn.cursor(); l_cur = l_conn.cursor(); n_cur.execute('SELECT COUNT(*) FROM regulations'); l_cur.execute('SELECT COUNT(*) FROM regulations'); n_count = n_cur.fetchone()[0]; l_count = l_cur.fetchone()[0]; print(f'网络数据库法规数: {n_count}'); print(f'本地数据库法规数: {l_count}'); n_conn.close(); l_conn.close()" 2>nul

if errorlevel 1 (
    echo ⚠ 无法对比数据库内容，但可以继续同步
)

echo.
echo ⚠ 警告：同步操作将覆盖本地数据库！
echo.
set /p confirm=是否从网络数据库同步到本地？(Y/N):

if /i not "%confirm%"=="Y" (
    echo.
    echo 已取消同步操作
    pause
    exit /b 0
)

echo.
echo 正在同步...

REM 备份当前本地数据库
if exist "data\databases\regulations.db" (
    if not exist "backup" mkdir backup
    set backup_name=backup\regulations_before_sync_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db
    set backup_name=!backup_name: =0!
    copy "data\databases\regulations.db" "!backup_name!" >nul
    echo ✓ 已备份本地数据库到: !backup_name!
)

REM 确保目标目录存在
if not exist "data\databases" mkdir "data\databases"

REM 从网络复制到本地
copy "%network_db%" "data\databases\regulations.db" >nul

if errorlevel 1 (
    echo ✗ 同步失败！
    pause
    exit /b 1
)

echo ✓ 同步成功！
echo.
echo 网络数据库已同步到本地：data\databases\regulations.db
echo 现在可以运行 build.bat 进行打包了
echo.
pause
exit /b 0
