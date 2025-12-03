"""
更新通知列表对话框
"""
import sys
from pathlib import Path
import webbrowser
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QMessageBox,
    QTextEdit, QGroupBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services import UpdateService


class CheckUpdateWorker(QThread):
    """检查更新工作线程"""
    finished = pyqtSignal(bool, object)  # (成功, 更新信息)

    def __init__(self, update_service: UpdateService):
        super().__init__()
        self.update_service = update_service

    def run(self):
        """执行检查"""
        has_update, update_info = self.update_service.check_for_updates()
        self.finished.emit(has_update, update_info)


class UpdateNotificationsDialog(QDialog):
    """更新通知列表对话框"""

    def __init__(self, parent=None, update_service: UpdateService = None):
        super().__init__(parent)
        self.update_service = update_service
        self.check_worker = None
        self.latest_update_info = None
        self.init_ui()
        self.load_notifications()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("版本更新")
        self.setMinimumSize(700, 650)
        self.setModal(True)

        layout = QVBoxLayout()

        # 标题
        title = QLabel("版本更新")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # 最新版本信息组（默认隐藏）
        self.version_group = QGroupBox("最新版本信息")
        self.version_group.setVisible(False)
        version_layout = QVBoxLayout()

        # 版本详情
        self.version_info_text = QTextEdit()
        self.version_info_text.setReadOnly(True)
        self.version_info_text.setMaximumHeight(200)
        version_layout.addWidget(self.version_info_text)

        # 更新操作按钮
        update_btn_layout = QHBoxLayout()
        update_btn_layout.addStretch()

        self.download_btn = QPushButton("下载更新")
        self.download_btn.setStyleSheet(
            "QPushButton { background-color: #28a745; color: white; font-weight: bold; padding: 8px 20px; }"
            "QPushButton:hover { background-color: #218838; }"
        )
        self.download_btn.clicked.connect(self.download_update)
        update_btn_layout.addWidget(self.download_btn)

        self.ignore_btn = QPushButton("忽略此版本")
        self.ignore_btn.clicked.connect(self.ignore_update)
        update_btn_layout.addWidget(self.ignore_btn)

        update_btn_layout.addStretch()
        version_layout.addLayout(update_btn_layout)

        self.version_group.setLayout(version_layout)
        layout.addWidget(self.version_group)

        # 进度条（默认隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 进度信息
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #0066cc; font-size: 11px;")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # 通知历史
        history_label = QLabel("通知历史")
        history_font = QFont()
        history_font.setPointSize(11)
        history_font.setBold(True)
        history_label.setFont(history_font)
        layout.addWidget(history_label)

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

        # 获取最新版本按钮
        self.check_update_btn = QPushButton("获取最新版本")
        self.check_update_btn.setStyleSheet(
            "QPushButton { background-color: #007bff; color: white; font-weight: bold; padding: 8px 20px; }"
            "QPushButton:hover { background-color: #0056b3; }"
        )
        self.check_update_btn.clicked.connect(self.check_for_updates)
        button_layout.addWidget(self.check_update_btn)

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

    def check_for_updates(self):
        """检查最新版本"""
        # 禁用按钮
        self.check_update_btn.setEnabled(False)
        self.check_update_btn.setText("检查中...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_label.setVisible(True)
        self.progress_label.setText("正在从 GitHub 获取最新版本信息...")

        # 创建工作线程
        self.check_worker = CheckUpdateWorker(self.update_service)
        self.check_worker.finished.connect(self.on_check_finished)
        self.check_worker.start()

    def on_check_finished(self, has_update: bool, update_info: dict):
        """检查完成"""
        self.check_update_btn.setEnabled(True)
        self.check_update_btn.setText("获取最新版本")
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        if has_update and update_info:
            # 保存更新信息
            self.latest_update_info = update_info

            # 显示版本信息
            info_text = f"📦 最新版本: {update_info.get('version')}\n"
            info_text += f"📅 发布日期: {update_info.get('release_date', '未知')}\n\n"

            if update_info.get('required'):
                info_text += "⚠️ 此版本为强制更新\n\n"

            if update_info.get('changelog'):
                info_text += "📝 更新内容:\n"
                for item in update_info.get('changelog', []):
                    info_text += f"  • {item}\n"

            if update_info.get('download_url'):
                info_text += f"\n🔗 下载链接: {update_info.get('download_url')}\n"

            self.version_info_text.setPlainText(info_text)
            self.version_group.setVisible(True)

            QMessageBox.information(
                self,
                "发现新版本",
                f"发现新版本 {update_info.get('version')}！\n\n"
                f"当前版本: {self.update_service.current_version}\n"
                f"最新版本: {update_info.get('version')}\n\n"
                f"请查看下方详细信息。"
            )
        else:
            self.version_group.setVisible(False)
            QMessageBox.information(
                self,
                "已是最新版本",
                f"当前版本 {self.update_service.current_version} 已是最新版本！"
            )

    def download_update(self):
        """下载更新"""
        if not self.latest_update_info:
            QMessageBox.warning(self, "错误", "没有可用的更新信息")
            return

        download_url = self.latest_update_info.get('download_url')
        if not download_url:
            QMessageBox.warning(self, "错误", "没有找到下载链接")
            return

        # 打开浏览器下载
        reply = QMessageBox.question(
            self,
            "下载更新",
            f"即将打开浏览器下载新版本 {self.latest_update_info.get('version')}\n\n"
            f"下载完成后，请手动解压并替换程序文件。\n\n"
            f"是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                webbrowser.open(download_url)
                QMessageBox.information(
                    self,
                    "提示",
                    "已在浏览器中打开下载链接。\n\n"
                    "下载完成后：\n"
                    "1. 解压下载的文件\n"
                    "2. 关闭当前程序\n"
                    "3. 用新版本覆盖旧版本\n"
                    "4. 重新启动程序"
                )
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开浏览器失败: {str(e)}")

    def ignore_update(self):
        """忽略此版本更新"""
        reply = QMessageBox.question(
            self,
            "确认忽略",
            "确定要忽略此版本更新吗？\n\n"
            "忽略后，版本信息将被隐藏，\n"
            "但您仍可以点击【获取最新版本】按钮查看。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.version_group.setVisible(False)
            self.latest_update_info = None
            QMessageBox.information(self, "已忽略", "已忽略此版本更新")
