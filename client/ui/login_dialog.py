"""
登录对话框
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services import AuthService
from shared.config import settings


class LoginDialog(QDialog):
    """登录对话框"""

    login_success = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_service = AuthService()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{settings.APP_NAME} - 登录")
        self.setFixedSize(480, 520)
        self.setModal(True)

        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #667eea, stop:1 #764ba2);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        # 登录卡片容器
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(20)

        # 标题
        title_label = QLabel(settings.APP_NAME)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        card_layout.addWidget(title_label)

        # 版本
        version_label = QLabel(f"版本 {settings.APP_VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #7f8c8d; font-size: 13px; margin-bottom: 10px;")
        card_layout.addWidget(version_label)

        card_layout.addSpacing(10)

        # 用户名
        username_label = QLabel("👤 用户名")
        username_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 13px;")
        card_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setText("admin")
        self.username_input.setMinimumHeight(36)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(5)

        # 密码
        password_label = QLabel("🔒 密码")
        password_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 13px;")
        card_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(36)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(15)

        # 登录按钮
        self.login_button = QPushButton("登  录")
        self.login_button.setMinimumHeight(42)
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #5568d3, stop:1 #6a3f91);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #4a5ab8, stop:1 #5d3780);
            }
        """)
        self.login_button.clicked.connect(self.login)
        card_layout.addWidget(self.login_button)

        # 提示
        hint_label = QLabel("💡 默认账号: admin / admin123")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("""
            color: #95a5a6;
            font-size: 12px;
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 6px;
            margin-top: 5px;
        """)
        card_layout.addWidget(hint_label)

        layout.addWidget(card)
        self.setLayout(layout)

        self.username_input.setFocus()

    def login(self):
        """登录"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username:
            QMessageBox.warning(self, "警告", "请输入用户名")
            return

        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return

        success, message, user = self.auth_service.login(username, password)

        if success:
            QMessageBox.information(self, "成功", message)
            self.login_success.emit(user)
            self.accept()
        else:
            QMessageBox.critical(self, "错误", message)
            self.password_input.clear()
            self.password_input.setFocus()

    def get_auth_service(self):
        """获取认证服务"""
        return self.auth_service