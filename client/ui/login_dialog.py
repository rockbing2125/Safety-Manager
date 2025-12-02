"""
登录对话框
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
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
        self.setFixedSize(400, 300)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        title_label = QLabel(settings.APP_NAME)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setMinimumHeight(40)
        layout.addWidget(title_label)

        # 版本
        version_label = QLabel(f"版本 {settings.APP_VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        layout.addSpacing(10)

        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setFixedWidth(80)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setText("admin")
        self.username_input.setMinimumHeight(35)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_label.setFixedWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self.login)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        layout.addSpacing(10)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.login_button = QPushButton("登录")
        self.login_button.setFixedWidth(100)
        self.login_button.clicked.connect(self.login)
        button_layout.addWidget(self.login_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 提示
        hint_label = QLabel("默认账号: admin / admin123")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(hint_label)

        layout.addStretch()
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