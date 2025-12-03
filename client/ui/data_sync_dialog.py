"""
数据同步对话框
用于显示和应用远程数据更新
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QGroupBox, QTextEdit, QProgressBar,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services.data_sync_service import DataSyncService


class DataSyncWorker(QThread):
    """数据同步工作线程"""
    progress = pyqtSignal(str)  # 进度信息
    finished = pyqtSignal(bool, str)  # 完成信号(成功, 消息)

    def __init__(self, sync_service: DataSyncService):
        super().__init__()
        self.sync_service = sync_service

    def run(self):
        """执行拉取"""
        try:
            self.progress.emit("正在拉取远程更新...")
            success, message = self.sync_service.pull_updates()
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"同步失败: {str(e)}")


class DataSyncDialog(QDialog):
    """数据同步对话框"""

    def __init__(self, parent=None, update_info: dict = None):
        super().__init__(parent)
        self.sync_service = DataSyncService()
        self.update_info = update_info or {}
        self.sync_worker = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("发现数据更新")
        self.setMinimumSize(650, 550)
        self.setModal(True)

        layout = QVBoxLayout()

        # 标题
        title = QLabel("📦 发现新的数据更新")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # 说明
        desc = QLabel(
            "检测到远程仓库有新的数据更新。\n"
            "其他用户可能已经更新了法规参数，建议您立即同步以获取最新数据。"
        )
        desc.setStyleSheet("color: #666; font-size: 11px; padding: 5px 0; margin-bottom: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # 更新统计
        stats_label = QLabel()
        total_commits = self.update_info.get('total_commits', 0)
        changed_files = self.update_info.get('changed_files', [])
        has_data_changes = self.update_info.get('has_data_changes', False)

        stats_text = f"📊 发现 {total_commits} 个新提交"
        if has_data_changes:
            stats_text += " | ⚠️ 包含数据库更新"

        stats_label.setText(stats_text)
        stats_label.setStyleSheet(
            "padding: 8px; background-color: #e7f3ff; "
            "border: 1px solid #b3d9ff; border-radius: 4px; font-weight: bold;"
        )
        layout.addWidget(stats_label)

        # 提交历史组
        commits_group = QGroupBox("更新内容")
        commits_layout = QVBoxLayout()

        self.commits_list = QListWidget()
        self.commits_list.setMaximumHeight(180)

        commits = self.update_info.get('commits', [])
        if commits:
            for commit in commits:
                item_text = (
                    f"[{commit.get('hash', 'unknown')}] "
                    f"{commit.get('message', '无提交信息')}\n"
                    f"    作者: {commit.get('author', '未知')} | "
                    f"时间: {commit.get('date', '未知')[:19]}"
                )
                item = QListWidgetItem(item_text)
                self.commits_list.addItem(item)
        else:
            item = QListWidgetItem("未获取到提交信息")
            self.commits_list.addItem(item)

        commits_layout.addWidget(self.commits_list)
        commits_group.setLayout(commits_layout)
        layout.addWidget(commits_group)

        # 变更文件组
        files_group = QGroupBox(f"变更的文件 ({len(changed_files)} 个)")
        files_layout = QVBoxLayout()

        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(120)

        if changed_files:
            for file in changed_files[:20]:  # 最多显示20个
                # 高亮数据文件
                if any(pattern in file for pattern in ['RDB/', 'data/', '.db', '.sqlite']):
                    item = QListWidgetItem(f"📁 {file}")
                    item.setForeground(Qt.GlobalColor.blue)
                else:
                    item = QListWidgetItem(f"📄 {file}")
                self.files_list.addItem(item)

            if len(changed_files) > 20:
                item = QListWidgetItem(f"... 还有 {len(changed_files) - 20} 个文件")
                self.files_list.addItem(item)
        else:
            item = QListWidgetItem("未检测到文件变更")
            self.files_list.addItem(item)

        files_layout.addWidget(self.files_list)
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)

        # 警告信息
        if has_data_changes:
            warning_label = QLabel(
                "⚠️ 注意：此更新包含数据库变更，同步后程序将自动重新加载数据。"
            )
            warning_label.setStyleSheet(
                "padding: 8px; background-color: #fff3cd; "
                "border: 1px solid #ffc107; border-radius: 4px; color: #856404;"
            )
            warning_label.setWordWrap(True)
            layout.addWidget(warning_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 进度信息
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #0066cc; font-size: 11px;")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.later_btn = QPushButton("稍后同步")
        self.later_btn.setMinimumWidth(100)
        self.later_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.later_btn)

        self.sync_btn = QPushButton("立即同步")
        self.sync_btn.setMinimumWidth(120)
        self.sync_btn.clicked.connect(self.sync_data)
        self.sync_btn.setStyleSheet(
            "QPushButton { background-color: #28a745; color: white; font-weight: bold; padding: 8px; }"
            "QPushButton:hover { background-color: #218838; }"
        )
        button_layout.addWidget(self.sync_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def sync_data(self):
        """同步数据"""
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认同步",
            "确定要同步远程数据更新吗？\n\n"
            "此操作将：\n"
            "1. 拉取远程仓库的最新数据\n"
            "2. 自动合并到本地\n"
            "3. 重新加载应用数据\n\n"
            "建议在同步前保存当前工作。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # 禁用按钮
        self.sync_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("准备同步...")

        # 创建工作线程
        self.sync_worker = DataSyncWorker(self.sync_service)
        self.sync_worker.progress.connect(self.on_progress)
        self.sync_worker.finished.connect(self.on_finished)
        self.sync_worker.start()

    def on_progress(self, message: str):
        """更新进度"""
        self.progress_label.setText(message)

    def on_finished(self, success: bool, message: str):
        """同步完成"""
        self.sync_btn.setEnabled(True)
        self.later_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        if success:
            # 同步成功
            result = QMessageBox.information(
                self,
                "同步成功",
                f"✅ {message}\n\n"
                f"数据已成功同步！\n\n"
                f"程序需要重新加载数据以应用更新。\n"
                f"是否立即重新加载？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if result == QMessageBox.StandardButton.Yes:
                # 通知主窗口重新加载
                self.accept()  # 返回 Accepted 状态
            else:
                self.reject()
        else:
            # 同步失败
            QMessageBox.critical(
                self,
                "同步失败",
                f"❌ {message}\n\n"
                f"可能的原因：\n"
                f"1. 网络连接问题\n"
                f"2. 本地有未提交的冲突\n"
                f"3. 没有远程仓库访问权限\n\n"
                f"您可以稍后再试，或手动使用 git pull 命令同步。"
            )


# 测试代码
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 模拟更新信息
    test_update_info = {
        'branch': 'main',
        'total_commits': 3,
        'commits': [
            {
                'hash': 'abc123de',
                'author': '张三',
                'email': 'zhangsan@example.com',
                'date': '2024-01-20 10:30:00',
                'message': '更新法规参数：新增CE认证标准'
            },
            {
                'hash': '456def78',
                'author': '李四',
                'email': 'lisi@example.com',
                'date': '2024-01-20 09:15:00',
                'message': '修复数据导入bug'
            }
        ],
        'changed_files': [
            'RDB/regulations.db',
            'client/services/regulation_service.py',
            'README.md'
        ],
        'has_data_changes': True
    }

    dialog = DataSyncDialog(update_info=test_update_info)
    dialog.show()
    sys.exit(app.exec())
