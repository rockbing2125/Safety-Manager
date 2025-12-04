"""
推送更新通知对话框（管理员）
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QTextEdit, QComboBox,
    QLabel, QMessageBox, QGroupBox
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services import UpdateService
from client.models import NotificationType


class PushUpdateDialog(QDialog):
    """推送更新通知对话框"""

    def __init__(self, parent=None, update_service: UpdateService = None):
        super().__init__(parent)
        self.update_service = update_service
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("推送更新通知")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout()

        # 基本信息组
        basic_group = QGroupBox("通知信息")
        basic_layout = QFormLayout()
        basic_layout.setVerticalSpacing(15)  # 设置行间距

        # 通知类型
        self.type_combo = QComboBox()
        self.type_combo.addItem("软件版本更新", NotificationType.SOFTWARE.value)
        self.type_combo.addItem("法规内容更新", NotificationType.REGULATION.value)
        self.type_combo.setMinimumHeight(24)  # 设置下拉框高度
        basic_layout.addRow("通知类型:", self.type_combo)

        # 标题
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("例如: 系统升级至 v1.1.0")
        self.title_input.setMinimumHeight(24)  # 设置输入框高度
        basic_layout.addRow("标题 *:", self.title_input)

        # 版本号（可选）
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("例如: 1.1.0（软件更新时填写）")
        self.version_input.setMinimumHeight(24)  # 设置输入框高度
        basic_layout.addRow("版本号:", self.version_input)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # 消息内容
        message_group = QGroupBox("消息内容")
        message_layout = QVBoxLayout()

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("输入更新详情...\n例如:\n• 新增XXX功能\n• 修复XXX问题\n• 优化XXX性能")
        self.message_input.setMaximumHeight(150)
        message_layout.addWidget(self.message_input)

        message_group.setLayout(message_layout)
        layout.addWidget(message_group)

        # 提示信息
        hint = QLabel("推送后，所有用户将收到更新通知")
        hint.setStyleSheet("color: #FF9800; font-size: 11px; padding: 10px;")
        layout.addWidget(hint)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        push_btn = QPushButton("推送通知")
        push_btn.setMinimumWidth(100)
        push_btn.clicked.connect(self.push_notification)
        button_layout.addWidget(push_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def push_notification(self):
        """推送通知"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入通知标题")
            return

        notification_type = self.type_combo.currentData()
        message = self.message_input.toPlainText().strip()
        version = self.version_input.text().strip() or None

        # 创建通知
        success, msg = self.update_service.create_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            version=version
        )

        if success:
            QMessageBox.information(self, "成功", "更新通知已推送给所有用户")
            self.accept()
        else:
            QMessageBox.critical(self, "失败", f"推送失败: {msg}")
