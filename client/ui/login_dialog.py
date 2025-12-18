"""
登录对话框
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QWidget, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services import AuthService
from shared.config import settings
from client.ui.change_password_dialog import ChangePasswordDialog


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

        # 设置对话框样式 - 改用清新的蓝绿色渐变
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #11998e, stop:1 #38ef7d);
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
        version_label.setMinimumHeight(24)
        version_label.setStyleSheet("color: #7f8c8d; font-size: 13px; margin-bottom: 10px; padding: 2px 0px;")
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
                background-color: transparent;
            }
            QLineEdit:focus {
                border: 2px solid #11998e;
                background-color: #f8fbff;
            }
        """)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(5)

        # 密码
        password_label = QLabel("🔒 密码")
        password_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 13px;")
        card_layout.addWidget(password_label)

        # 密码输入框容器
        password_container = QWidget()
        password_container.setStyleSheet("background-color: transparent;")
        password_container.setMinimumHeight(44)  # 增加容器高度以容纳完整边框
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(5)
        password_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # 垂直居中对齐

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)  # 设置固定高度
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 14px;
                background-color: transparent;
            }
            QLineEdit:focus {
                border: 2px solid #11998e;
                background-color: #f8fbff;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        password_layout.addWidget(self.password_input, 1)

        # 眼睛图标按钮
        self.toggle_password_btn = QToolButton()
        self.toggle_password_btn.setText("👁")
        self.toggle_password_btn.setFixedSize(40, 40)  # 与输入框同高
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.setStyleSheet("""
            QToolButton {
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                background-color: transparent;
                font-size: 16px;
                padding: 0px;
            }
            QToolButton:hover {
                background-color: #f8fbff;
                border: 2px solid #11998e;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_btn, 0)

        card_layout.addWidget(password_container)

        card_layout.addSpacing(15)

        # 登录按钮
        self.login_button = QPushButton("登  录")
        self.login_button.setMinimumHeight(42)
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #11998e, stop:1 #38ef7d);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #0f8278, stop:1 #2dd96c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #0d6b63, stop:1 #25c25a);
            }
        """)
        self.login_button.clicked.connect(self.login)
        card_layout.addWidget(self.login_button)

        card_layout.addSpacing(10)

        # 修改密码链接
        change_password_label = QLabel('<a href="#" style="color: #11998e; text-decoration: none;">修改密码</a>')
        change_password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_password_label.setTextFormat(Qt.TextFormat.RichText)
        change_password_label.setCursor(Qt.CursorShape.PointingHandCursor)
        change_password_label.setMinimumHeight(32)  # 确保高度足够显示文字
        change_password_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                padding: 8px 5px;
            }
            QLabel:hover {
                color: #0f8278;
            }
        """)
        change_password_label.linkActivated.connect(self.show_change_password_dialog)
        card_layout.addWidget(change_password_label)

        # 提示
        hint_label = QLabel("💡 默认账号: admin / admin123")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setMinimumHeight(36)  # 确保高度足够
        hint_label.setStyleSheet("""
            color: #95a5a6;
            font-size: 12px;
            padding: 10px 8px;
            background-color: #f8f9fa;
            border-radius: 6px;
            margin-top: 5px;
        """)
        card_layout.addWidget(hint_label)

        layout.addWidget(card)
        self.setLayout(layout)

        self.username_input.setFocus()

    def toggle_password_visibility(self):
        """切换密码可见性"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("👁")

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

    def show_change_password_dialog(self):
        """显示修改密码对话框"""
        dialog = ChangePasswordDialog(self)
        dialog.exec()

    def get_auth_service(self):
        """获取认证服务"""
        return self.auth_service