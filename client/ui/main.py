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
    setup_logging()

    try:
        logger.info("正在初始化数据库...")
        init_db()
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        print(f"数据库初始化失败: {e}")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName(settings.APP_NAME)
    app.setApplicationVersion(settings.APP_VERSION)
    app.setStyle("Fusion")
    # 添加样式表（不影响功能）
    app.setStyleSheet("""
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-height: 28px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QLineEdit {
            border: 2px solid #e1e1e1;
            border-radius: 4px;
            padding: 6px;
        }
        QLineEdit:focus {
            border-color: #0078d4;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: white;
        }
        QHeaderView::section {
            background-color: #f5f5f5;
            padding: 8px;
            border: none;
            border-bottom: 2px solid #0078d4;
            font-weight: bold;
        }"""
    )
    # 应用现代化样式
    app.setStyleSheet("""
        /* 按钮 */
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        
        /* 输入框 */
        QLineEdit {
            border: 2px solid #e1e1e1;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
        }
        QLineEdit:focus {
            border: 2px solid #0078d4;
        }
        
        /* 表格 */
        QTableWidget {
            background-color: white;
            border: 1px solid #e1e1e1;
            gridline-color: #f0f0f0;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: white;
        }
        QHeaderView::section {
            background-color: #f8f8f8;
            padding: 8px;
            border: none;
            border-bottom: 2px solid #0078d4;
            font-weight: bold;
        }
        
        /* 标签页 */
        QTabWidget::pane {
            border: 1px solid #e1e1e1;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #f0f0f0;
            padding: 10px 20px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #0078d4;
            color: white;
        }"""
    )

    login_dialog = LoginDialog()

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


if __name__ == "__main__":
    sys.exit(main())