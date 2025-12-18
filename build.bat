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

REM 在清空 dist 目录前，检查并备份可能的用户数据
if exist "dist\SafetyManager\data\databases\regulations.db" (
    echo.
    echo ⚠ 警告：检测到 dist 目录中存在数据库文件！
    echo   这可能包含你在打包程序中编辑的数据。
    echo.

    REM 获取文件大小和修改时间
    for %%F in ("dist\SafetyManager\data\databases\regulations.db") do (
        set dist_db_size=%%~zF
        set dist_db_time=%%~tF
    )
    for %%F in ("data\databases\regulations.db") do (
        set dev_db_size=%%~zF
        set dev_db_time=%%~tF
    )

    echo   dist 数据库: !dist_db_size! 字节, 修改时间: !dist_db_time!
    echo   开发数据库: !dev_db_size! 字节, 修改时间: !dev_db_time!
    echo.
    echo   建议操作：
    echo   1. 如果你刚才在 dist 程序中编辑了数据，请先按 Ctrl+C 取消
    echo   2. 手动复制 dist\SafetyManager\data\databases\regulations.db
    echo   3. 覆盖到 data\databases\regulations.db
    echo   4. 然后重新运行此脚本
    echo.

    REM 创建自动备份
    if not exist "backup" mkdir backup
    set backup_name=backup\regulations_dist_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db
    set backup_name=!backup_name: =0!
    copy "dist\SafetyManager\data\databases\regulations.db" "!backup_name!" >nul
    echo ✓ 已自动备份到: !backup_name!
    echo.

    choice /C YN /M "是否继续清空 dist 目录"
    if errorlevel 2 (
        echo.
        echo 已取消打包。请先处理数据库文件。
        pause
        exit /b 0
    )
)

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
echo [3.6/5] 验证数据库配置...

REM 检查是否配置了网络数据库
set "network_db_path="
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if "%%a"=="DATABASE_PATH" set "network_db_path=%%b"
    )
)

if defined network_db_path (
    echo ⚠ 检测到网络数据库配置！
    echo   .env 配置: DATABASE_PATH=%network_db_path%
    echo.
    echo   ⚠️ 重要提醒：
    echo   1. 启动程序.pyw使用的是网络数据库
    echo   2. 打包将使用本地数据库: data\databases\regulations.db
    echo   3. 如果你在启动程序.pyw中编辑了数据，需要先同步！
    echo.

    REM 检查网络数据库是否可访问
    if exist "%network_db_path%" (
        echo ✓ 网络数据库可访问

        REM 对比网络和本地数据库
        echo.
        echo 网络数据库：
        for %%F in ("%network_db_path%") do (
            set network_size=%%~zF
            echo   大小: %%~zF 字节
            echo   修改时间: %%~tF
        )
        echo.
        echo 本地数据库：
        if exist "data\databases\regulations.db" (
            for %%F in ("data\databases\regulations.db") do (
                set local_size=%%~zF
                echo   大小: %%~zF 字节
                echo   修改时间: %%~tF
            )
        ) else (
            echo   ✗ 不存在
            set local_size=0
        )
        echo.

        REM 对比数据库内容
        echo 正在对比数据库内容...
        python -c "import sqlite3; try: n_conn = sqlite3.connect(r'%network_db_path%'); l_conn = sqlite3.connect(r'data\databases\regulations.db'); n_cur = n_conn.cursor(); l_cur = l_conn.cursor(); n_cur.execute('SELECT COUNT(*) FROM regulations'); l_cur.execute('SELECT COUNT(*) FROM regulations'); n_count = n_cur.fetchone()[0]; l_count = l_cur.fetchone()[0]; print(f'  网络数据库法规数: {n_count}'); print(f'  本地数据库法规数: {l_count}'); diff = n_count - l_count; print(f'  差异: {diff:+d} 条法规'); n_conn.close(); l_conn.close(); exit(0 if diff == 0 else 1); except: exit(2)" 2>nul
        set db_compare_result=!errorlevel!

        echo.
        echo ══════════════════════════════════════
        echo  打包选项：
        echo  [S] 同步网络数据库到本地后打包（推荐）
        echo  [C] 继续使用当前本地数据库打包
        echo  [N] 取消打包
        echo ══════════════════════════════════════
        echo.

        REM 如果数据库有差异，默认建议同步
        if !db_compare_result! NEQ 0 (
            echo ⚠ 网络和本地数据库不一致，强烈建议同步！
            echo.
        )

        choice /C SCN /M "请选择"
        set sync_choice=!errorlevel!

        if !sync_choice!==3 (
            echo.
            echo 已取消打包
            pause
            exit /b 0
        )

        if !sync_choice!==1 (
            echo.
            echo [开始同步网络数据库到本地]
            echo.

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
            echo 正在从网络同步...
            copy "%network_db_path%" "data\databases\regulations.db" >nul

            if errorlevel 1 (
                echo ✗ 同步失败！无法从网络复制数据库
                echo.
                pause
                exit /b 1
            )

            echo ✓ 同步成功！
            echo.
            echo 已同步网络数据库到本地
            for %%F in ("data\databases\regulations.db") do (
                echo   本地数据库新大小: %%~zF 字节
            )
            echo.
            echo 继续打包...
            echo.
        ) else (
            echo.
            echo ⚠ 继续使用当前本地数据库打包
            echo   注意：网络数据库的更新将不会包含在打包程序中
            echo.
        )
    ) else (
        echo ✗ 网络数据库当前不可访问: %network_db_path%
        echo.
        echo   可能的原因：
        echo   1. 网络连接断开
        echo   2. 共享服务器离线
        echo   3. 没有访问权限
        echo.
        echo   将使用本地数据库继续打包
        echo.

        choice /C YN /M "是否继续打包"
        if errorlevel 2 (
            echo.
            echo 已取消打包
            pause
            exit /b 0
        )
    )
)

if exist "data\databases\regulations.db" (
    echo ✓ 检测到本地数据库
    for %%F in ("data\databases\regulations.db") do (
        echo   大小: %%~zF 字节
        echo   修改时间: %%~tF
        echo   这个数据库将被打包到程序中
    )
) else (
    echo ⚠ 警告：未找到本地数据库文件
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
