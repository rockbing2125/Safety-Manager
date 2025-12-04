@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ============================================
echo 并网法规管理系统 - 打包脚本（分发版）
echo ============================================
echo 本脚本将打包成开箱即用的独立应用
echo - 自动配置数据库
echo - 内置更新推送功能
echo - 无需手动配置环境
echo ============================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查是否已安装 PyInstaller
echo [1/5] 检查 PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ✗ 未安装 PyInstaller，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo ✗ 安装失败！请手动运行: pip install pyinstaller
        pause
        exit /b 1
    )
) else (
    echo ✓ PyInstaller 已安装
)

echo.
echo [2/5] 安装打包所需依赖...
pip install jaraco.text jaraco.functools jaraco.context jaraco.classes platformdirs -q
if errorlevel 1 (
    echo ⚠ 依赖安装失败，继续尝试打包...
) else (
    echo ✓ 打包依赖已安装
)

echo.
echo [3/5] 清理旧的构建文件...
if exist "build" (
    rmdir /s /q "build"
    echo ✓ 已删除 build 目录
)
if exist "dist" (
    rmdir /s /q "dist"
    echo ✓ 已删除 dist 目录
)

echo.
echo [3.5/5] 准备分发环境...
REM 确保.env文件不会被打包（由spec文件控制）
if exist ".env" (
    echo ⚠ 检测到.env文件，打包时将自动排除
    echo ✓ 只会包含.env.dist作为配置模板
)

echo.
echo [3.6/5] 验证数据库文件...
if exist "data\databases\regulations.db" (
    echo ✓ 检测到开发环境数据库
    for %%F in ("data\databases\regulations.db") do (
        echo   大小: %%~zF 字节
        echo   这个数据库将被打包到程序中
    )
) else (
    echo ⚠ 警告：未找到数据库文件
    echo   打包的程序将从空数据库开始
)

echo.
echo [4/5] 开始打包...
echo 这可能需要几分钟时间，请耐心等待...
echo 提示: 已启用控制台模式，可以查看详细错误信息
echo.

pyinstaller SafetyManager.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ✗ 打包失败！
    echo 请检查错误信息并修复问题
    pause
    exit /b 1
)

echo.
echo [5/5] 验证打包结果...
if exist "dist\SafetyManager\SafetyManager.exe" (
    echo ✓ 打包成功！
    echo.
    echo 打包文件位置: dist\SafetyManager\
    echo 主程序: dist\SafetyManager\SafetyManager.exe
    echo.
) else (
    echo ✗ 找不到可执行文件！
    echo 打包可能失败，请检查上面的错误信息
    pause
    exit /b 1
)

echo.
echo [6/6] 验证数据库是否正确打包...
if exist "dist\SafetyManager\data\databases\regulations.db" (
    echo ✓ 数据库文件已打包
    for %%F in ("dist\SafetyManager\data\databases\regulations.db") do (
        echo   打包后大小: %%~zF 字节
    )

    REM 对比开发环境和打包后的文件大小
    if exist "data\databases\regulations.db" (
        for %%A in ("data\databases\regulations.db") do set dev_size=%%~zA
        for %%B in ("dist\SafetyManager\data\databases\regulations.db") do set dist_size=%%~zB

        if !dev_size! EQU !dist_size! (
            echo ✓ 数据库大小一致，打包正确！
        ) else (
            echo ⚠ 警告：数据库大小不一致！
            echo   开发环境: !dev_size! 字节
            echo   打包后:   !dist_size! 字节
            echo.
            echo   建议运行 python compare_db.py 进行详细对比
        )
    )
) else (
    echo ✗ 数据库文件未打包！
    echo   请检查 SafetyManager.spec 配置
)

echo.
echo ============================================
echo 打包完成！
echo ============================================
echo.

echo ============================================
echo 分发说明
echo ============================================
echo 1. 测试运行:
echo    运行 dist\SafetyManager\SafetyManager.exe
echo    - 应自动创建数据库
echo    - 默认账户: admin / admin123
echo    - 检查更新功能是否正常
echo.
echo 2. 更新服务器配置:
echo    在 shared\config.py 中修改:
echo    UPDATE_CHECK_URL = "你的云服务器地址"
echo    然后重新打包
echo.
echo 3. 打包分发:
echo    将整个 dist\SafetyManager\ 文件夹压缩成 zip
echo    用户解压后直接运行即可，无需配置
echo.
echo 4. 用户使用:
echo    - 直接运行 SafetyManager.exe
echo    - 自动创建本地数据库
echo    - 自动接收版本更新推送
echo    - 如需自定义配置，重命名 .env.dist 为 .env
echo ============================================
echo.

pause
