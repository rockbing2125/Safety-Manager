@echo off
chcp 65001 >nul
echo ========================================
echo 同步数据库到打包目录
echo ========================================
echo.

REM 检查开发环境数据库是否存在
if not exist "data\databases\regulations.db" (
    echo [错误] 开发环境数据库不存在: data\databases\regulations.db
    pause
    exit /b 1
)

REM 检查打包目录是否存在
if not exist "dist\SafetyManager" (
    echo [错误] 打包目录不存在: dist\SafetyManager
    echo 请先运行 build.bat 进行打包
    pause
    exit /b 1
)

REM 创建目标目录（如果不存在）
if not exist "dist\SafetyManager\data\databases" (
    echo [创建] 创建目标目录...
    mkdir "dist\SafetyManager\data\databases"
)

REM 显示文件信息
echo [源文件] data\databases\regulations.db
for %%F in ("data\databases\regulations.db") do (
    echo   大小: %%~zF 字节
    echo   时间: %%~tF
)
echo.

echo [目标文件] dist\SafetyManager\data\databases\regulations.db
if exist "dist\SafetyManager\data\databases\regulations.db" (
    for %%F in ("dist\SafetyManager\data\databases\regulations.db") do (
        echo   大小: %%~zF 字节
        echo   时间: %%~tF
    )
) else (
    echo   [不存在]
)
echo.

REM 询问确认
set /p confirm="是否要覆盖打包目录中的数据库？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    exit /b 0
)

REM 备份旧数据库（如果存在）
if exist "dist\SafetyManager\data\databases\regulations.db" (
    echo [备份] 备份旧数据库...
    copy /Y "dist\SafetyManager\data\databases\regulations.db" "dist\SafetyManager\data\databases\regulations.db.bak" >nul
    echo   备份到: dist\SafetyManager\data\databases\regulations.db.bak
)

REM 复制数据库
echo [复制] 正在复制最新数据库...
copy /Y "data\databases\regulations.db" "dist\SafetyManager\data\databases\regulations.db" >nul

if %errorlevel%==0 (
    echo.
    echo ========================================
    echo [成功] 数据库同步完成！
    echo ========================================
    echo.
    echo 现在可以运行 dist\SafetyManager\SafetyManager.exe
    echo 或者重新打包: build.bat
) else (
    echo.
    echo [错误] 复制失败！错误代码: %errorlevel%
)

echo.
pause
