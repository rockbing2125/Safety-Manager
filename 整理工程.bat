@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ============================================
echo 工程整理工具
echo ============================================
echo.
echo 此工具将清理不必要的文件，保持工程整洁
echo 所有删除的文件将备份到 cleanup_backup 目录
echo.

cd /d "%~dp0"

REM 创建备份目录
set backup_dir=cleanup_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_dir=!backup_dir: =0!
mkdir "!backup_dir!" 2>nul

echo ══════════════════════════════════════
echo 要删除的文件类别：
echo ══════════════════════════════════════
echo.
echo 1. 临时和错误文件
echo    - bash.exe.stackdump（错误转储）
echo    - nul（空文件）
echo.
echo 2. 已过时的脚本（功能已被新脚本替代）
echo    - compare_db.py（已被"数据库管理工具.bat"替代）
echo    - compare_db.bat（已被"数据库管理工具.bat"替代）
echo    - sync_database_to_dist.bat（已过时）
echo    - sync_db_to_dist.bat（已过时）
echo    - rebuild_quick.bat（已被build.bat包含）
echo    - test_direct_run.bat（测试脚本）
echo.
echo 3. 数据库迁移脚本（一次性使用）
echo    - add_coefficient_column.py
echo    - add_protocol_bit_column.py
echo.
echo 4. 调试工具
echo    - check_git_env.py（Git诊断工具，可选）
echo.
echo 5. 截图文件
echo    - screenshot-20251208-164328.png
echo.
echo 6. 根目录的参数.c文件（应该在RDB目录）
echo    - Satety_Parameter.c
echo    - 北爱尔兰G98NI并网标准_Parameter.c
echo    - 北爱尔兰G99NI并网标准_Parameter.c
echo    - 英国G100并网标准_Parameter.c
echo    - 英国G98并网标准_Parameter.c
echo    - 英国G99并网标准_Parameter.c
echo.
echo ══════════════════════════════════════
echo.

set /p confirm=是否继续清理？所有文件将先备份 (Y/N):
if /i not "%confirm%"=="Y" (
    echo 已取消清理
    pause
    exit /b 0
)

echo.
echo [1/6] 清理临时和错误文件...
set count=0
if exist "bash.exe.stackdump" (
    copy "bash.exe.stackdump" "!backup_dir!\" >nul 2>&1
    del "bash.exe.stackdump" >nul 2>&1
    echo ✓ 已删除: bash.exe.stackdump
    set /a count+=1
)
if exist "nul" (
    copy "nul" "!backup_dir!\" >nul 2>&1
    del "nul" >nul 2>&1
    echo ✓ 已删除: nul
    set /a count+=1
)
if !count!==0 (echo   [无需清理])
echo.

echo [2/6] 清理已过时的脚本...
set count=0
for %%f in (compare_db.py compare_db.bat sync_database_to_dist.bat sync_db_to_dist.bat rebuild_quick.bat test_direct_run.bat) do (
    if exist "%%f" (
        copy "%%f" "!backup_dir!\" >nul 2>&1
        del "%%f" >nul 2>&1
        echo ✓ 已删除: %%f
        set /a count+=1
    )
)
if !count!==0 (echo   [无需清理])
echo.

echo [3/6] 清理数据库迁移脚本...
set count=0
for %%f in (add_coefficient_column.py add_protocol_bit_column.py) do (
    if exist "%%f" (
        copy "%%f" "!backup_dir!\" >nul 2>&1
        del "%%f" >nul 2>&1
        echo ✓ 已删除: %%f
        set /a count+=1
    )
)
if !count!==0 (echo   [无需清理])
echo.

echo [4/6] 清理调试工具...
echo ⚠ check_git_env.py 是Git诊断工具，可能有用
set /p del_check_git=是否删除 check_git_env.py？(Y/N，默认N):
if /i "%del_check_git%"=="Y" (
    if exist "check_git_env.py" (
        copy "check_git_env.py" "!backup_dir!\" >nul 2>&1
        del "check_git_env.py" >nul 2>&1
        echo ✓ 已删除: check_git_env.py
    )
) else (
    echo   [保留] check_git_env.py
)
echo.

echo [5/6] 清理截图文件...
set count=0
if exist "screenshot-20251208-164328.png" (
    copy "screenshot-20251208-164328.png" "!backup_dir!\" >nul 2>&1
    del "screenshot-20251208-164328.png" >nul 2>&1
    echo ✓ 已删除: screenshot-20251208-164328.png
    set /a count+=1
)
if !count!==0 (echo   [无需清理])
echo.

echo [6/6] 清理根目录的参数.c文件...
echo ⚠ 这些文件应该在RDB目录中
set /p del_c_files=是否删除根目录的所有.c文件？(Y/N):
if /i "%del_c_files%"=="Y" (
    set count=0
    for %%f in (*.c) do (
        copy "%%f" "!backup_dir!\" >nul 2>&1
        del "%%f" >nul 2>&1
        echo ✓ 已删除: %%f
        set /a count+=1
    )
    if !count!==0 (echo   [无.c文件])
) else (
    echo   [保留] 所有.c文件
)
echo.

echo ══════════════════════════════════════
echo 清理完成！
echo ══════════════════════════════════════
echo.
echo 备份位置: !backup_dir!\
echo.
echo 如果需要恢复文件，可以从备份目录复制回来
echo.

REM 检查备份目录是否为空
set backup_empty=1
for %%f in ("!backup_dir!\*") do set backup_empty=0
if !backup_empty!==1 (
    echo [提示] 备份目录为空，没有文件被删除
    rmdir "!backup_dir!" 2>nul
)

echo.
pause
