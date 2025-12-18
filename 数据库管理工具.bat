@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ============================================
echo 并网法规管理系统 - 数据库管理工具
echo ============================================
echo.

REM 读取网络数据库配置
set "network_db="
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if "%%a"=="DATABASE_PATH" set "network_db=%%b"
    )
)

:menu
echo 请选择操作：
echo 1. 备份本地数据库
echo 2. 从备份恢复数据库
echo 3. 从 dist 目录恢复数据库（在打包前使用）
echo 4. 从网络数据库同步到本地（打包前必须）
echo 5. 查看所有数据库文件信息
echo 6. 查看备份列表
echo 7. 对比网络和本地数据库差异
echo 8. 退出
echo.

if defined network_db (
    echo [当前配置了网络数据库: %network_db%]
    echo.
)

set /p choice=请输入选项 (1-8):

if "%choice%"=="1" goto backup_dev
if "%choice%"=="2" goto restore_from_backup
if "%choice%"=="3" goto restore_from_dist
if "%choice%"=="4" goto sync_from_network
if "%choice%"=="5" goto show_db_info
if "%choice%"=="6" goto list_backups
if "%choice%"=="7" goto compare_databases
if "%choice%"=="8" goto end
echo 无效选项，请重新选择
echo.
goto menu

:backup_dev
echo.
echo [备份开发环境数据库]
if not exist "data\databases\regulations.db" (
    echo ✗ 未找到开发环境数据库！
    echo.
    pause
    goto menu
)

if not exist "backup" mkdir backup
set backup_name=backup\regulations_manual_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db
set backup_name=!backup_name: =0!
copy "data\databases\regulations.db" "!backup_name!" >nul
echo ✓ 备份成功！
echo   备份文件: !backup_name!
for %%F in ("!backup_name!") do (
    echo   文件大小: %%~zF 字节
)
echo.
pause
goto menu

:restore_from_backup
echo.
echo [从备份恢复数据库]
if not exist "backup\*.db" (
    echo ✗ 未找到任何备份文件！
    echo.
    pause
    goto menu
)

echo 可用的备份文件：
echo.
set idx=0
for %%F in (backup\*.db) do (
    set /a idx+=1
    echo !idx!. %%~nxF (%%~zF 字节, %%~tF)
    set "file_!idx!=%%F"
)
echo.
set /p restore_choice=请输入要恢复的备份编号:

if not defined file_!restore_choice! (
    echo ✗ 无效选项
    echo.
    pause
    goto menu
)

echo.
echo ⚠ 警告：恢复操作将覆盖当前的开发环境数据库！
set /p confirm=确定要继续吗？(Y/N):
if /i not "%confirm%"=="Y" (
    echo 已取消恢复操作
    echo.
    pause
    goto menu
)

REM 先备份当前数据库
if exist "data\databases\regulations.db" (
    set current_backup=backup\regulations_before_restore_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db
    set current_backup=!current_backup: =0!
    copy "data\databases\regulations.db" "!current_backup!" >nul
    echo ✓ 已备份当前数据库到: !current_backup!
)

REM 恢复选择的备份
copy "!file_%restore_choice%!" "data\databases\regulations.db" >nul
echo ✓ 恢复成功！
echo   已从 !file_%restore_choice%! 恢复数据库
echo.
pause
goto menu

:restore_from_dist
echo.
echo [从 dist 目录恢复数据库]
if not exist "dist\SafetyManager\data\databases\regulations.db" (
    echo ✗ 未找到 dist 目录中的数据库文件！
    echo   可能 dist 目录尚未创建或已被清空。
    echo.
    pause
    goto menu
)

echo 检测到以下数据库：
echo.
echo dist 数据库:
for %%F in ("dist\SafetyManager\data\databases\regulations.db") do (
    echo   文件大小: %%~zF 字节
    echo   修改时间: %%~tF
)
echo.
echo 开发数据库:
for %%F in ("data\databases\regulations.db") do (
    echo   文件大小: %%~zF 字节
    echo   修改时间: %%~tF
)
echo.
echo ⚠ 警告：此操作将用 dist 目录的数据库覆盖开发环境数据库！
set /p confirm=确定要继续吗？(Y/N):
if /i not "%confirm%"=="Y" (
    echo 已取消恢复操作
    echo.
    pause
    goto menu
)

REM 先备份当前数据库
if not exist "backup" mkdir backup
set current_backup=backup\regulations_before_dist_restore_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db
set current_backup=!current_backup: =0!
copy "data\databases\regulations.db" "!current_backup!" >nul
echo ✓ 已备份当前数据库到: !current_backup!

REM 从 dist 恢复
copy "dist\SafetyManager\data\databases\regulations.db" "data\databases\regulations.db" >nul
echo ✓ 恢复成功！
echo   已从 dist 目录恢复数据库
echo.
pause
goto menu

:sync_from_network
echo.
echo [从网络数据库同步到本地]
if not defined network_db (
    echo ✗ 未配置网络数据库
    echo   .env文件中没有DATABASE_PATH配置
    echo.
    pause
    goto menu
)

echo 网络数据库路径: %network_db%
echo.

if not exist "%network_db%" (
    echo ✗ 无法访问网络数据库
    echo   请检查网络连接和共享权限
    echo.
    pause
    goto menu
)

echo ✓ 网络数据库可访问
echo.
echo 网络数据库：
for %%F in ("%network_db%") do (
    echo   大小: %%~zF 字节
    echo   修改时间: %%~tF
)
echo.
echo 本地数据库：
if exist "data\databases\regulations.db" (
    for %%F in ("data\databases\regulations.db") do (
        echo   大小: %%~zF 字节
        echo   修改时间: %%~tF
    )
) else (
    echo   ✗ 不存在
)
echo.

set /p confirm=确认同步？这将覆盖本地数据库 (Y/N):
if /i not "%confirm%"=="Y" (
    echo 已取消
    echo.
    pause
    goto menu
)

REM 备份当前本地数据库
if exist "data\databases\regulations.db" (
    if not exist "backup" mkdir backup
    set backup_name=backup\regulations_before_sync_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db
    set backup_name=!backup_name: =0!
    copy "data\databases\regulations.db" "!backup_name!" >nul
    echo ✓ 已备份本地数据库
)

if not exist "data\databases" mkdir "data\databases"
copy "%network_db%" "data\databases\regulations.db" >nul
echo ✓ 同步成功！
echo.
pause
goto menu

:compare_databases
echo.
echo [对比数据库差异]
if not defined network_db (
    echo ✗ 未配置网络数据库
    echo.
    pause
    goto menu
)

if not exist "%network_db%" (
    echo ✗ 网络数据库不可访问
    echo.
    pause
    goto menu
)

if not exist "data\databases\regulations.db" (
    echo ✗ 本地数据库不存在
    echo.
    pause
    goto menu
)

echo 正在对比数据库...
echo.
python -c "import sqlite3; n_conn = sqlite3.connect(r'%network_db%'); l_conn = sqlite3.connect(r'data\databases\regulations.db'); n_cur = n_conn.cursor(); l_cur = l_conn.cursor(); n_cur.execute('SELECT COUNT(*) FROM regulations'); l_cur.execute('SELECT COUNT(*) FROM regulations'); n_count = n_cur.fetchone()[0]; l_count = l_cur.fetchone()[0]; print('═══════════════════════════════════'); print(f'网络数据库法规数: {n_count}'); print(f'本地数据库法规数: {l_count}'); print(f'差异: {n_count - l_count:+d}'); print('═══════════════════════════════════'); n_cur.execute('SELECT id, name, updated_at FROM regulations ORDER BY updated_at DESC LIMIT 5'); print('\n网络数据库最近更新的5条法规:'); [print(f'  {r[0]:3d}. {r[1]} ({r[2]})') for r in n_cur.fetchall()]; l_cur.execute('SELECT id, name, updated_at FROM regulations ORDER BY updated_at DESC LIMIT 5'); print('\n本地数据库最近更新的5条法规:'); [print(f'  {r[0]:3d}. {r[1]} ({r[2]})') for r in l_cur.fetchall()]; n_conn.close(); l_conn.close()"
echo.
pause
goto menu

:show_db_info
echo.
echo [数据库文件信息]
echo.
echo 1. 本地开发数据库:
if exist "data\databases\regulations.db" (
    for %%F in ("data\databases\regulations.db") do (
        echo    路径: %%F
        echo    大小: %%~zF 字节
        echo    修改时间: %%~tF
    )
) else (
    echo    ✗ 不存在
)
echo.
echo 2. dist 打包数据库:
if exist "dist\SafetyManager\data\databases\regulations.db" (
    for %%F in ("dist\SafetyManager\data\databases\regulations.db") do (
        echo    路径: %%F
        echo    大小: %%~zF 字节
        echo    修改时间: %%~tF
    )
) else (
    echo    ✗ 不存在
)
echo.
echo 3. 网络共享数据库:
if defined network_db (
    echo    路径: %network_db%
    if exist "%network_db%" (
        for %%F in ("%network_db%") do (
            echo    大小: %%~zF 字节
            echo    修改时间: %%~tF
        )
    ) else (
        echo    ✗ 当前不可访问
    )
) else (
    echo    ✗ 未配置
)
echo.
pause
goto menu

:list_backups
echo.
echo [备份文件列表]
echo.
if not exist "backup\*.db" (
    echo ✗ 未找到任何备份文件
) else (
    for %%F in (backup\*.db) do (
        echo %%~nxF
        echo   大小: %%~zF 字节
        echo   时间: %%~tF
        echo.
    )
)
pause
goto menu

:end
echo.
echo 再见！
timeout /t 2 >nul
exit /b 0
