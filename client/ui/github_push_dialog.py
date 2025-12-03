"""
GitHub 自动推送对话框
用于自动推送版本更新到 GitHub
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel,
    QMessageBox, QGroupBox, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services.git_service import GitService
from shared.config import settings


class GitPushWorker(QThread):
    """Git 推送工作线程"""
    progress = pyqtSignal(str)  # 进度信息
    finished = pyqtSignal(bool, str)  # 完成信号(成功, 消息)

    def __init__(self, git_service: GitService, version: str,
                 changelog: list, github_token: str,
                 release_file: str, update_app_version: bool,
                 required: bool):
        super().__init__()
        self.git_service = git_service
        self.version = version
        self.changelog = changelog
        self.github_token = github_token
        self.release_file = release_file
        self.update_app_version = update_app_version
        self.required = required

    def run(self):
        """执行推送"""
        try:
            self.progress.emit("开始推送版本更新...")

            success, message = self.git_service.push_release_with_file(
                version=self.version,
                changelog=self.changelog,
                github_token=self.github_token,
                release_file=self.release_file,
                update_app_version=self.update_app_version,
                required=self.required
            )

            self.finished.emit(success, message)

        except Exception as e:
            self.finished.emit(False, f"推送失败: {str(e)}")


class GitHubPushDialog(QDialog):
    """GitHub 自动推送对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.git_service = GitService()
        self.push_worker = None
        self.init_ui()
        self.check_git_status()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("新版本推送")
        self.setMinimumSize(700, 650)
        self.setModal(True)

        layout = QVBoxLayout()

        # 标题和说明
        title = QLabel("推送新版本到 GitHub")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        desc = QLabel(
            "此功能会自动：\n"
            "1. 创建 GitHub Release 并上传安装包\n"
            "2. 更新 version.json 文件\n"
            "3. 推送到 GitHub，用户将自动收到更新通知"
        )
        desc.setStyleSheet("color: #666; font-size: 11px; padding: 5px 0;")
        layout.addWidget(desc)

        # Git 状态
        self.status_label = QLabel("检查 Git 状态...")
        self.status_label.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        layout.addWidget(self.status_label)

        # 版本信息组
        version_group = QGroupBox("版本信息")
        version_layout = QFormLayout()
        version_layout.setVerticalSpacing(15)  # 设置行间距

        # 当前版本
        current_version = self.git_service.get_current_version() or "未知"
        self.current_version_label = QLabel(current_version)
        version_layout.addRow("当前版本:", self.current_version_label)

        # 新版本号
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("例如: 1.1.5")
        self.version_input.setMinimumHeight(32)  # 设置输入框高度
        version_layout.addRow("新版本号 *:", self.version_input)

        # 发布文件选择
        file_select_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("选择要发布的压缩包（.zip 或 .rar）")
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setMinimumHeight(32)  # 设置输入框高度
        file_select_layout.addWidget(self.file_path_input)

        select_file_btn = QPushButton("选择文件...")
        select_file_btn.setMaximumWidth(100)
        select_file_btn.clicked.connect(self.select_release_file)
        file_select_layout.addWidget(select_file_btn)

        version_layout.addRow("发布文件 *:", file_select_layout)

        # 强制更新
        self.required_checkbox = QCheckBox("强制更新（用户必须更新才能使用）")
        version_layout.addRow("", self.required_checkbox)

        # 同步更新 config.py
        self.update_config_checkbox = QCheckBox("同步更新 shared/config.py 中的版本号")
        self.update_config_checkbox.setChecked(True)
        version_layout.addRow("", self.update_config_checkbox)

        version_group.setLayout(version_layout)
        layout.addWidget(version_group)

        # 更新日志
        changelog_group = QGroupBox("更新日志")
        changelog_layout = QVBoxLayout()

        self.changelog_input = QTextEdit()
        self.changelog_input.setPlaceholderText(
            "输入更新内容（每行一条）\n"
            "例如:\n"
            "✨ 新增 Excel 导出功能\n"
            "🐛 修复搜索崩溃问题\n"
            "⚡ 优化加载速度"
        )
        self.changelog_input.setMaximumHeight(120)
        changelog_layout.addWidget(self.changelog_input)

        changelog_group.setLayout(changelog_layout)
        layout.addWidget(changelog_group)

        # GitHub 配置
        github_group = QGroupBox("GitHub 配置")
        github_layout = QFormLayout()
        github_layout.setVerticalSpacing(15)  # 设置行间距

        # GitHub Token
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText("输入 GitHub Personal Access Token（高级密码）")
        self.token_input.setMinimumHeight(32)  # 设置输入框高度
        github_layout.addRow("GitHub Token *:", self.token_input)

        # 帮助链接
        help_label = QLabel(
            '<a href="https://github.com/settings/tokens">如何获取 GitHub Token？</a>'
        )
        help_label.setOpenExternalLinks(True)
        help_label.setStyleSheet("color: #0066cc; font-size: 11px;")
        github_layout.addRow("", help_label)

        github_group.setLayout(github_layout)
        layout.addWidget(github_group)

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

        self.test_btn = QPushButton("测试连接")
        self.test_btn.setMinimumWidth(100)
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)

        self.push_btn = QPushButton("推送到 GitHub")
        self.push_btn.setMinimumWidth(120)
        self.push_btn.clicked.connect(self.push_to_github)
        self.push_btn.setStyleSheet(
            "QPushButton { background-color: #28a745; color: white; font-weight: bold; }"
            "QPushButton:hover { background-color: #218838; }"
        )
        button_layout.addWidget(self.push_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def check_git_status(self):
        """检查 Git 状态"""
        # 检查 Git 可用性
        success, message = self.git_service.check_git_available()
        if not success:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet(
                "padding: 5px; border: 1px solid #dc3545; "
                "border-radius: 3px; background-color: #f8d7da; color: #721c24;"
            )
            self.push_btn.setEnabled(False)
            return

        # 检查仓库状态
        success, message = self.git_service.check_repo_status()
        if not success:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet(
                "padding: 5px; border: 1px solid #dc3545; "
                "border-radius: 3px; background-color: #f8d7da; color: #721c24;"
            )
            self.push_btn.setEnabled(False)
            return

        # 一切正常
        self.status_label.setText(f"✅ Git 环境正常，可以推送")
        self.status_label.setStyleSheet(
            "padding: 5px; border: 1px solid #28a745; "
            "border-radius: 3px; background-color: #d4edda; color: #155724;"
        )

    def test_connection(self):
        """测试 GitHub 连接"""
        github_token = self.token_input.text().strip()

        if not github_token:
            QMessageBox.warning(self, "提示", "请输入 GitHub Token")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")

        success, message = self.git_service.test_github_connection(github_token)

        self.test_btn.setEnabled(True)
        self.test_btn.setText("测试连接")

        if success:
            QMessageBox.information(self, "成功", f"✅ {message}")
        else:
            QMessageBox.warning(self, "失败", f"❌ {message}")

    def select_release_file(self):
        """选择发布文件"""
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择发布文件",
            "dist",  # 默认在dist目录
            "压缩文件 (*.zip *.rar);;所有文件 (*.*)"
        )

        if file_path:
            self.file_path_input.setText(file_path)

    def push_to_github(self):
        """推送到 GitHub"""
        # 验证输入
        version = self.version_input.text().strip()
        release_file = self.file_path_input.text().strip()
        changelog_text = self.changelog_input.toPlainText().strip()
        github_token = self.token_input.text().strip()

        if not version:
            QMessageBox.warning(self, "提示", "请输入新版本号")
            self.version_input.setFocus()
            return

        if not release_file:
            QMessageBox.warning(self, "提示", "请选择要发布的文件")
            return

        # 检查文件是否存在
        from pathlib import Path
        if not Path(release_file).exists():
            QMessageBox.warning(self, "提示", f"文件不存在：{release_file}")
            return

        if not changelog_text:
            QMessageBox.warning(self, "提示", "请输入更新日志")
            self.changelog_input.setFocus()
            return

        if not github_token:
            QMessageBox.warning(self, "提示", "请输入 GitHub Token")
            self.token_input.setFocus()
            return

        # 解析更新日志
        changelog = [line.strip() for line in changelog_text.split('\n')
                    if line.strip()]

        # 获取文件大小
        file_size_mb = Path(release_file).stat().st_size / 1024 / 1024

        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认推送",
            f"确定要推送版本 v{version} 到 GitHub 吗？\n\n"
            f"此操作将：\n"
            f"1. 创建 GitHub Release (v{version})\n"
            f"2. 上传文件: {Path(release_file).name} ({file_size_mb:.2f} MB)\n"
            f"3. 更新 version.json 文件\n"
            f"4. 提交并推送到 GitHub\n"
            f"5. 用户将自动收到更新通知\n\n"
            f"⚠️ 上传可能需要几分钟，请耐心等待。\n\n"
            f"是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # 禁用按钮
        self.push_btn.setEnabled(False)
        self.test_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_label.setVisible(True)
        self.progress_label.setText("准备推送...")

        # 创建工作线程
        self.push_worker = GitPushWorker(
            git_service=self.git_service,
            version=version,
            changelog=changelog,
            github_token=github_token,
            release_file=release_file,
            update_app_version=self.update_config_checkbox.isChecked(),
            required=self.required_checkbox.isChecked()
        )

        self.push_worker.progress.connect(self.on_progress)
        self.push_worker.finished.connect(self.on_finished)
        self.push_worker.start()

    def on_progress(self, message: str):
        """更新进度"""
        self.progress_label.setText(message)

    def on_finished(self, success: bool, message: str):
        """推送完成"""
        self.push_btn.setEnabled(True)
        self.test_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        if success:
            QMessageBox.information(
                self,
                "发布成功",
                f"🎉 {message}\n\n"
                f"✅ GitHub Release 已创建\n"
                f"✅ 安装包已上传\n"
                f"✅ version.json 已更新\n\n"
                f"用户将在启动程序时自动收到更新通知。\n"
                f"你可以在 GitHub 仓库的 Releases 页面查看。"
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "发布失败",
                f"❌ {message}\n\n"
                f"请检查：\n"
                f"1. GitHub Token 是否正确且有足够权限\n"
                f"2. 网络连接是否正常\n"
                f"3. 文件是否可以访问\n"
                f"4. GitHub API 是否可用"
            )


# 测试代码
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = GitHubPushDialog()
    dialog.show()
    sys.exit(app.exec())
