"""
密码修改对话框
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QWidget, QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services import AuthService


class ChangePasswordDialog(QDialog):
    """密码修改对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_service = AuthService()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("修改密码")
        self.setFixedSize(420, 480)
        self.setModal(True)

        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #11998e, stop:1 #38ef7d);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # 卡片容器
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(18)

        # 标题
        title_label = QLabel("修改密码")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px; padding: 5px;")
        title_label.setMinimumHeight(40)
        card_layout.addWidget(title_label)

        card_layout.addSpacing(5)

        # 用户名
        username_label = QLabel("👤 用户名")
        username_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 13px;")
        card_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
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

        # 旧密码
        old_password_label = QLabel("🔒 旧密码")
        old_password_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 13px;")
        card_layout.addWidget(old_password_label)

        self.old_password_input = self.create_password_input("请输入旧密码")
        card_layout.addWidget(self.old_password_input['container'])

        # 新密码
        new_password_label = QLabel("🔑 新密码")
        new_password_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 13px;")
        card_layout.addWidget(new_password_label)

        self.new_password_input = self.create_password_input("请输入新密码")
        card_layout.addWidget(self.new_password_input['container'])

        # 确认新密码
        confirm_password_label = QLabel("🔑 确认新密码")
        confirm_password_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 13px;")
        card_layout.addWidget(confirm_password_label)

        self.confirm_password_input = self.create_password_input("请再次输入新密码")
        self.confirm_password_input['input'].returnPressed.connect(self.change_password)
        card_layout.addWidget(self.confirm_password_input['container'])

        card_layout.addSpacing(10)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 确认按钮
        self.confirm_button = QPushButton("确认修改")
        self.confirm_button.setMinimumHeight(38)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #11998e, stop:1 #38ef7d);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
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
        self.confirm_button.clicked.connect(self.change_password)
        button_layout.addWidget(self.confirm_button)

        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumHeight(38)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #2c3e50;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        card_layout.addLayout(button_layout)

        layout.addWidget(card)
        self.setLayout(layout)

        self.username_input.setFocus()

    def create_password_input(self, placeholder):
        """创建带眼睛图标的密码输入框"""
        # 密码输入框容器
        password_container = QWidget()
        password_container.setStyleSheet("background-color: transparent;")
        password_container.setMinimumHeight(44)  # 增加容器高度以容纳完整边框
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(5)
        password_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # 垂直居中对齐

        password_input = QLineEdit()
        password_input.setPlaceholderText(placeholder)
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setFixedHeight(40)  # 设置固定高度
        password_input.setStyleSheet("""
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
        password_layout.addWidget(password_input, 1)

        # 眼睛图标按钮
        toggle_btn = QToolButton()
        toggle_btn.setText("👁")
        toggle_btn.setFixedSize(40, 40)  # 与输入框同高
        toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_btn.setStyleSheet("""
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
        toggle_btn.clicked.connect(lambda: self.toggle_password_visibility(password_input, toggle_btn))
        password_layout.addWidget(toggle_btn, 0)

        return {
            'container': password_container,
            'input': password_input,
            'toggle_btn': toggle_btn
        }

    def toggle_password_visibility(self, password_input, toggle_btn):
        """切换密码可见性"""
        if password_input.echoMode() == QLineEdit.EchoMode.Password:
            password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            toggle_btn.setText("🙈")
        else:
            password_input.setEchoMode(QLineEdit.EchoMode.Password)
            toggle_btn.setText("👁")

    def change_password(self):
        """修改密码"""
        username = self.username_input.text().strip()
        old_password = self.old_password_input['input'].text()
        new_password = self.new_password_input['input'].text()
        confirm_password = self.confirm_password_input['input'].text()

        if not username:
            QMessageBox.warning(self, "警告", "请输入用户名")
            return

        if not old_password:
            QMessageBox.warning(self, "警告", "请输入旧密码")
            return

        if not new_password:
            QMessageBox.warning(self, "警告", "请输入新密码")
            return

        if not confirm_password:
            QMessageBox.warning(self, "警告", "请确认新密码")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的新密码不一致")
            return

        if len(new_password) < 6:
            QMessageBox.warning(self, "警告", "新密码长度至少为6位")
            return

        success, message = self.auth_service.change_password(username, old_password, new_password)

        if success:
            QMessageBox.information(self, "成功", message)
            self.accept()
        else:
            QMessageBox.critical(self, "错误", message)
            self.old_password_input['input'].clear()
            self.old_password_input['input'].setFocus()
