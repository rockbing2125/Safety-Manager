"""
更新通知列表对话框
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services import UpdateService


class UpdateNotificationsDialog(QDialog):
    """更新通知列表对话框"""

    def __init__(self, parent=None, update_service: UpdateService = None):
        super().__init__(parent)
        self.update_service = update_service
        self.init_ui()
        self.load_notifications()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("更新通知")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        layout = QVBoxLayout()

        # 标题
        title = QLabel("更新通知")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # 通知列表
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.mark_as_read)
        layout.addWidget(self.list_widget)

        # 提示文字
        hint = QLabel("双击通知标记为已读")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        mark_all_btn = QPushButton("全部已读")
        mark_all_btn.clicked.connect(self.mark_all_as_read)
        button_layout.addWidget(mark_all_btn)

        clear_btn = QPushButton("清空通知")
        clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_notifications(self):
        """加载通知列表"""
        self.list_widget.clear()
        notifications = self.update_service.get_all_notifications()

        if not notifications:
            item = QListWidgetItem("暂无更新通知")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            return

        for notif in notifications:
            # 创建列表项
            type_text = "软件更新" if notif.type == "software" else "法规更新"
            time_str = notif.created_at.strftime("%Y-%m-%d %H:%M") if notif.created_at else ""

            item_text = f"[{type_text}] {notif.title}\n{time_str}"
            if notif.message:
                item_text += f"\n{notif.message[:50]}..."

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, notif.id)

            # 未读通知用粗体显示
            if not notif.is_read:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(Qt.GlobalColor.lightGray)

            self.list_widget.addItem(item)

    def mark_as_read(self, item: QListWidgetItem):
        """标记为已读"""
        notif_id = item.data(Qt.ItemDataRole.UserRole)
        if notif_id:
            success, message = self.update_service.mark_as_read(notif_id)
            if success:
                # 刷新列表
                self.load_notifications()

    def mark_all_as_read(self):
        """标记所有为已读"""
        success, message = self.update_service.mark_all_as_read()
        if success:
            QMessageBox.information(self, "成功", "已将所有通知标记为已读")
            self.load_notifications()
        else:
            QMessageBox.warning(self, "失败", message)

    def clear_all(self):
        """清空所有通知"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有通知吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.update_service.clear_all_notifications()
            if success:
                QMessageBox.information(self, "成功", "已清空所有通知")
                self.load_notifications()
            else:
                QMessageBox.warning(self, "失败", message)
