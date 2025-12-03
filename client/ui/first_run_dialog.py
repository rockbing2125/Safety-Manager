"""
首次运行配置向导
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QMessageBox,
    QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from shared.config import settings


class FirstRunDialog(QDialog):
    """首次运行配置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_mode = "shared"  # shared 或 local
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("数据库配置向导")
        self.setMinimumSize(600, 450)
        self.setModal(True)

        layout = QVBoxLayout()

        # 欢迎信息
        welcome_label = QLabel(
            "欢迎使用并网法规管理系统！\n\n"
            "首次运行需要配置数据库连接。\n"
            "请根据您的使用场景选择配置方式："
        )
        welcome_label.setStyleSheet("font-size: 13px; padding: 10px;")
        layout.addWidget(welcome_label)

        # 模式选择组
        mode_group = QGroupBox("使用模式")
        mode_layout = QVBoxLayout()

        self.mode_button_group = QButtonGroup()

        # 共享模式
        self.shared_radio = QRadioButton("多用户共享模式（推荐）")
        self.shared_radio.setChecked(True)
        self.shared_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.shared_radio)
        mode_layout.addWidget(self.shared_radio)

        shared_desc = QLabel(
            "  适用于多台电脑共享数据，支持推送通知功能。\n"
            "  需要配置网络共享数据库路径。"
        )
        shared_desc.setStyleSheet("color: #666; font-size: 11px; margin-left: 20px;")
        mode_layout.addWidget(shared_desc)

        mode_layout.addSpacing(10)

        # 单机模式
        self.local_radio = QRadioButton("单机模式")
        self.local_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.local_radio)
        mode_layout.addWidget(self.local_radio)

        local_desc = QLabel(
            "  适用于单台电脑独立使用，数据存储在本地。\n"
            "  不支持多用户共享和推送通知功能。"
        )
        local_desc.setStyleSheet("color: #666; font-size: 11px; margin-left: 20px;")
        mode_layout.addWidget(local_desc)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # 共享数据库配置组
        self.shared_config_group = QGroupBox("共享数据库配置")
        shared_config_layout = QFormLayout()
        shared_config_layout.setVerticalSpacing(15)  # 设置行间距

        # 数据库路径输入
        self.db_path_input = QLineEdit()
        self.db_path_input.setPlaceholderText(r"例如: \\10.0.104.252\SafetyManager\regulations.db")
        self.db_path_input.setText(r"\\10.0.104.252\SafetyManager\regulations.db")
        self.db_path_input.setMinimumHeight(32)  # 设置输入框高度
        shared_config_layout.addRow("数据库路径:", self.db_path_input)

        # 提示信息
        hint_label = QLabel(
            "提示：\n"
            "• 路径格式：\\\\服务器IP\\共享文件夹\\regulations.db\n"
            "• 确保所有电脑都能访问该共享文件夹\n"
            "• 需要有读写权限"
        )
        hint_label.setStyleSheet("color: #FF9800; font-size: 10px; padding: 5px;")
        shared_config_layout.addRow("", hint_label)

        # 测试按钮
        test_btn = QPushButton("测试连接")
        test_btn.setMaximumWidth(100)
        test_btn.clicked.connect(self.test_connection)
        shared_config_layout.addRow("", test_btn)

        self.shared_config_group.setLayout(shared_config_layout)
        layout.addWidget(self.shared_config_group)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("保存配置并启动")
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_mode_changed(self):
        """模式切换事件"""
        if self.shared_radio.isChecked():
            self.selected_mode = "shared"
            self.shared_config_group.setEnabled(True)
        else:
            self.selected_mode = "local"
            self.shared_config_group.setEnabled(False)

    def test_connection(self):
        """测试数据库连接"""
        db_path = self.db_path_input.text().strip()

        if not db_path:
            QMessageBox.warning(self, "提示", "请输入数据库路径")
            return

        try:
            from sqlalchemy import create_engine

            # 测试连接
            test_url = f"sqlite:///{db_path}"
            test_engine = create_engine(test_url)
            test_engine.connect().close()

            QMessageBox.information(
                self,
                "连接成功",
                f"数据库连接测试成功！\n\n路径：{db_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "连接失败",
                f"数据库连接失败！\n\n"
                f"错误信息：{str(e)}\n\n"
                f"请检查：\n"
                f"1. 路径是否正确\n"
                f"2. 网络共享是否可访问\n"
                f"3. 是否有读写权限"
            )

    def save_config(self):
        """保存配置"""
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"

        try:
            if self.selected_mode == "local":
                # 单机模式：使用本地路径
                config_content = (
                    "# 数据库配置 - 单机模式\n"
                    "# DATABASE_PATH 不设置，使用默认本地路径\n"
                    "\n"
                    "# 其他配置\n"
                    "OFFLINE_MODE=True\n"
                    "LOG_LEVEL=INFO\n"
                )
            else:
                # 共享模式
                db_path = self.db_path_input.text().strip()

                if not db_path:
                    QMessageBox.warning(self, "提示", "请输入数据库路径")
                    return

                # 验证路径格式
                if not db_path.endswith("regulations.db"):
                    reply = QMessageBox.question(
                        self,
                        "确认路径",
                        f"路径似乎不包含 regulations.db 文件名。\n\n"
                        f"当前路径：{db_path}\n\n"
                        f"是否继续？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return

                config_content = (
                    f"# 数据库配置 - 多用户共享模式\n"
                    f"DATABASE_PATH={db_path}\n"
                    f"\n"
                    f"# 其他配置\n"
                    f"OFFLINE_MODE=True\n"
                    f"LOG_LEVEL=INFO\n"
                )

            # 写入配置文件
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(config_content)

            QMessageBox.information(
                self,
                "配置成功",
                "配置已保存！\n\n程序将重新启动以应用新配置。"
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "保存失败",
                f"配置保存失败：{str(e)}"
            )
