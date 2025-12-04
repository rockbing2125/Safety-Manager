"""
程序入口
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.config import settings
from shared.constants import LOG_FORMAT
from client.models import init_db
from client.ui import LoginDialog, MainWindow


def setup_logging():
    """配置日志"""
    logger.remove()

    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True
    )

    log_file = settings.LOG_DIR / f"app_main.log"
    logger.add(
        log_file,
        format=LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8"
    )

    logger.info("=" * 50)
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动")
    logger.info("=" * 50)


def main():
    """主函数"""
    try:
        print(">>> 步骤 1/5: 配置日志...")
        setup_logging()
        print(">>> 日志配置成功")
    except Exception as e:
        print(f"!!! 日志配置失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n按回车键退出...")
        input()
        return 1

    try:
        print(">>> 步骤 2/5: 初始化数据库...")
        logger.info("正在初始化数据库...")

        # 打包环境下，首次运行时从 _internal 复制数据库
        from shared.config import ensure_database_exists
        ensure_database_exists()

        logger.info(f"数据库路径: {settings.SQLITE_DB_PATH}")
        print(f">>> 数据库路径: {settings.SQLITE_DB_PATH}")
        sys.stdout.flush()  # 强制刷新输出缓冲
        init_db()
        print(">>> 数据库初始化成功")
        logger.info("数据库初始化成功")
        sys.stdout.flush()  # 强制刷新输出缓冲
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        print(f"!!! 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        print("\n按回车键退出...")
        input()
        return 1

    try:
        print(">>> 步骤 3/5: 创建 Qt 应用...")
        logger.info("正在创建 Qt 应用...")
        sys.stdout.flush()
        app = QApplication(sys.argv)
        print(">>> QApplication 实例已创建")
        sys.stdout.flush()
        app.setApplicationName(settings.APP_NAME)
        print(f">>> 应用名称: {settings.APP_NAME}")
        sys.stdout.flush()
        app.setApplicationVersion(settings.APP_VERSION)
        print(f">>> 应用版本: {settings.APP_VERSION}")
        sys.stdout.flush()
        app.setStyle("Fusion")
        print(">>> Qt 应用创建成功")
        logger.info("Qt 应用创建成功")
        sys.stdout.flush()
    except Exception as e:
        print(f"!!! Qt 应用创建失败: {e}")
        logger.error(f"Qt 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        print("\n按回车键退出...")
        input()
        return 1

    try:
        print(">>> 步骤 4/5: 应用样式...")
        logger.info("正在应用样式...")
        sys.stdout.flush()
        # 应用样式表
        stylesheet = """
QPushButton{background:#0078d4;color:white;border:none;padding:8px 16px;border-radius:4px;font-weight:bold;min-height:28px}
QPushButton:hover{background:#106ebe}
QLineEdit{border:2px solid #e1e1e1;border-radius:4px;padding:8px 10px;min-height:20px}
QLineEdit:focus{border-color:#0078d4}
QTableWidget::item:selected{background:#0078d4;color:white}
QHeaderView::section{background:#f5f5f5;padding:8px;border:none;border-bottom:2px solid #0078d4;font-weight:bold}
QTabBar::tab:selected{background:#0078d4;color:white}
    """
        app.setStyleSheet(stylesheet)
        print(">>> 样式应用成功")
        logger.info("样式应用成功")
        sys.stdout.flush()
    except Exception as e:
        print(f"!!! 样式应用失败: {e}")
        logger.error(f"样式应用失败: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        print("\n按回车键退出...")
        input()
        return 1

    try:
        print(">>> 步骤 5/5: 显示登录对话框...")
        logger.info("正在创建登录对话框...")
        sys.stdout.flush()
        login_dialog = LoginDialog()
        print(">>> 登录对话框已创建")
        logger.info("登录对话框已创建")
        sys.stdout.flush()
    except Exception as e:
        print(f"!!! 登录对话框创建失败: {e}")
        logger.error(f"登录对话框创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        print("\n按回车键退出...")
        input()
        return 1

    try:
        if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
            auth_service = login_dialog.get_auth_service()
            main_window = MainWindow(auth_service)
            main_window.show()

            logger.info("主窗口已显示")
            exit_code = app.exec()
            logger.info(f"{settings.APP_NAME} 退出")
            return exit_code
        else:
            logger.info("用户取消登录")
            return 0
    except Exception as e:
        print(f"!!! 运行时错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n按回车键退出...")
        input()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n!!! 致命错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n按回车键退出...")
        input()
        sys.exit(1)