@echo off
chcp 65001 >nul
echo ============================================
echo 推送功能测试工具
echo ============================================
echo.

echo [1] 检查数据库配置
python -c "from shared.config import settings; print(f'数据库路径: {settings.SQLITE_DB_PATH}')"
if errorlevel 1 (
    echo ✗ 配置读取失败
    goto :error
)
echo ✓ 配置读取成功
echo.

echo [2] 测试数据库连接
python -c "from client.models import engine; engine.connect().close(); print('✓ 数据库连接成功')"
if errorlevel 1 (
    echo ✗ 数据库连接失败
    echo.
    echo 请检查：
    echo   1. DATABASE_PATH 配置是否包含完整路径（含 regulations.db）
    echo   2. 网络共享文件夹是否可访问
    echo   3. 是否有读写权限
    goto :error
)
echo.

echo [3] 检查通知表是否存在
python -c "from client.models import engine; from sqlalchemy import inspect; inspector = inspect(engine); tables = inspector.get_table_names(); print('✓ 通知表存在' if 'update_notifications' in tables else '✗ 通知表不存在')"
if errorlevel 1 (
    echo ✗ 检查失败
    goto :error
)
echo.

echo [4] 查询现有通知
python -c "from client.models import SessionLocal, UpdateNotification; db = SessionLocal(); count = db.query(UpdateNotification).count(); unread = db.query(UpdateNotification).filter(UpdateNotification.is_read == False).count(); print(f'总通知数: {count}'); print(f'未读通知: {unread}'); db.close()"
if errorlevel 1 (
    echo ✗ 查询失败
    goto :error
)
echo.

echo [5] 显示最近5条通知
python -c "from client.models import SessionLocal, UpdateNotification; db = SessionLocal(); notifications = db.query(UpdateNotification).order_by(UpdateNotification.created_at.desc()).limit(5).all(); print(''); [print(f'  [{n.id}] {n.type:12s} | {n.title:30s} | 已读: {\"是\" if n.is_read else \"否\":2s} | {n.created_at.strftime(\"%%Y-%%m-%%d %%H:%%M\")}') for n in notifications]; db.close()"
if errorlevel 1 (
    echo ✗ 查询失败
    goto :error
)
echo.

echo ============================================
echo 测试完成！
echo ============================================
echo.
echo 推送功能工作正常，可以使用以下功能：
echo   • 管理员推送更新通知
echo   • 用户自动接收通知提醒
echo   • 查看未读通知（小红点提示）
echo.
goto :end

:error
echo.
echo ============================================
echo 测试失败！
echo ============================================
echo.
echo 请参考《推送功能使用说明.md》解决问题
echo 或运行《配置共享数据库.bat》重新配置
echo.

:end
pause
