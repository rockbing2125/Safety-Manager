"""
法规新增/编辑对话框
"""
import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QMessageBox, QGroupBox, QListWidget
)
from PyQt6.QtCore import pyqtSignal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.models import Regulation, NotificationType
from client.services import RegulationService, UpdateService
from shared.constants import RegulationStatus, COUNTRIES, REGULATION_CATEGORIES


class RegulationDialog(QDialog):
    """法规新增/编辑对话框"""

    regulation_saved = pyqtSignal()

    def __init__(self, parent=None, regulation: Optional[Regulation] = None, user_id: Optional[int] = None):
        super().__init__(parent)
        self.regulation = regulation
        self.user_id = user_id
        self.regulation_service = RegulationService()
        self.update_service = UpdateService()
        self.is_edit_mode = regulation is not None

        self.init_ui()

        if self.is_edit_mode:
            self.load_regulation_data()

    def init_ui(self):
        """初始化UI"""
        title = "编辑法规" if self.is_edit_mode else "新增法规"
        self.setWindowTitle(title)
        self.setMinimumSize(700, 600)
        self.setModal(True)

        layout = QVBoxLayout()

        # 基本信息组
        basic_group = self.create_basic_info_group()
        layout.addWidget(basic_group)

        # 详细信息组
        detail_group = self.create_detail_info_group()
        layout.addWidget(detail_group)

        # 标签组
        tag_group = self.create_tag_group()
        layout.addWidget(tag_group)

        # 按钮组
        button_layout = self.create_buttons()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_basic_info_group(self):
        """创建基本信息组"""
        group = QGroupBox("基本信息")
        layout = QFormLayout()
        layout.setVerticalSpacing(15)  # 设置行间距

        # 法规编号
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("例如: EN50549-1")
        self.code_input.setMinimumHeight(32)  # 设置输入框高度
        layout.addRow("法规编号 *:", self.code_input)

        # 法规名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: 欧洲并网标准 EN50549-1")
        self.name_input.setMinimumHeight(32)  # 设置输入框高度
        layout.addRow("法规名称 *:", self.name_input)

        # 国家/地区
        self.country_combo = QComboBox()
        self.country_combo.addItem("请选择...", None)
        for country in COUNTRIES:
            self.country_combo.addItem(country, country)
        self.country_combo.setMinimumHeight(32)  # 设置下拉框高度
        self.country_combo.currentTextChanged.connect(self._on_country_changed)
        layout.addRow("国家/地区:", self.country_combo)

        # 自定义国家/地区输入框（选择"其他"时显示）
        self.custom_country_input = QLineEdit()
        self.custom_country_input.setPlaceholderText("请输入国家/地区名称")
        self.custom_country_input.setMinimumHeight(32)
        self.custom_country_input.hide()  # 默认隐藏
        layout.addRow("", self.custom_country_input)

        # 版本号
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("例如: 2019")
        self.version_input.setMinimumHeight(32)  # 设置输入框高度
        layout.addRow("版本号:", self.version_input)

        # 状态
        self.status_combo = QComboBox()
        for status in RegulationStatus:
            self.status_combo.addItem(status.value, status)
        self.status_combo.setMinimumHeight(32)  # 设置下拉框高度
        layout.addRow("状态:", self.status_combo)

        group.setLayout(layout)
        return group

    def create_detail_info_group(self):
        """创建详细信息组"""
        group = QGroupBox("详细信息")
        layout = QVBoxLayout()

        desc_label = QLabel("描述:")
        layout.addWidget(desc_label)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("输入法规的详细描述...")
        self.description_input.setMaximumHeight(150)
        layout.addWidget(self.description_input)

        group.setLayout(layout)
        return group

    def create_tag_group(self):
        """创建标签组"""
        group = QGroupBox("标签")
        layout = QHBoxLayout()

        # 标签列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("当前标签:"))
        self.tag_list = QListWidget()
        left_layout.addWidget(self.tag_list)
        layout.addLayout(left_layout)

        # 标签操作
        right_layout = QVBoxLayout()

        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("输入新标签...")
        self.tag_input.setMinimumHeight(32)  # 设置输入框高度
        right_layout.addWidget(self.tag_input)

        add_tag_btn = QPushButton("添加标签")
        add_tag_btn.clicked.connect(self.add_tag)
        right_layout.addWidget(add_tag_btn)

        remove_tag_btn = QPushButton("删除选中")
        remove_tag_btn.clicked.connect(self.remove_tag)
        right_layout.addWidget(remove_tag_btn)

        right_layout.addStretch()
        layout.addLayout(right_layout)

        group.setLayout(layout)
        return group

    def create_buttons(self):
        """创建按钮组"""
        layout = QHBoxLayout()
        layout.addStretch()

        save_btn = QPushButton("保存")
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.save_regulation)
        layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        layout.addStretch()
        return layout

    def _on_country_changed(self, text):
        """国家/地区选择变化时的处理"""
        if text == "其他":
            self.custom_country_input.show()
            self.custom_country_input.setFocus()
        else:
            self.custom_country_input.hide()
            self.custom_country_input.clear()

    def load_regulation_data(self):
        """加载法规数据（编辑模式）"""
        if not self.regulation:
            return

        self.code_input.setText(self.regulation.code)
        self.name_input.setText(self.regulation.name)

        if self.regulation.country:
            index = self.country_combo.findData(self.regulation.country)
            if index >= 0:
                self.country_combo.setCurrentIndex(index)
            else:
                # 国家不在列表中，选择"其他"并填入自定义输入框
                other_index = self.country_combo.findData("其他")
                if other_index >= 0:
                    self.country_combo.setCurrentIndex(other_index)
                    self.custom_country_input.setText(self.regulation.country)

        if self.regulation.version:
            self.version_input.setText(self.regulation.version)

        index = self.status_combo.findData(self.regulation.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        if self.regulation.description:
            self.description_input.setPlainText(self.regulation.description)

        for tag in self.regulation.tags:
            self.tag_list.addItem(tag.name)

    def add_tag(self):
        """添加标签"""
        tag_name = self.tag_input.text().strip()
        if not tag_name:
            return

        for i in range(self.tag_list.count()):
            if self.tag_list.item(i).text() == tag_name:
                QMessageBox.warning(self, "警告", "标签已存在")
                return

        self.tag_list.addItem(tag_name)
        self.tag_input.clear()

    def remove_tag(self):
        """删除标签"""
        current_item = self.tag_list.currentItem()
        if current_item:
            self.tag_list.takeItem(self.tag_list.row(current_item))

    def get_tags(self):
        """获取所有标签"""
        tags = []
        for i in range(self.tag_list.count()):
            tags.append(self.tag_list.item(i).text())
        return tags

    def validate_input(self):
        """验证输入"""
        if not self.code_input.text().strip():
            QMessageBox.warning(self, "警告", "请输入法规编号")
            return False

        if not self.name_input.text().strip():
            QMessageBox.warning(self, "警告", "请输入法规名称")
            return False

        return True

    def save_regulation(self):
        """保存法规"""
        if not self.validate_input():
            return

        code = self.code_input.text().strip()
        name = self.name_input.text().strip()

        # 获取国家/地区，如果选择"其他"则使用自定义输入
        country = self.country_combo.currentData()
        if country == "其他":
            custom_country = self.custom_country_input.text().strip()
            if not custom_country:
                QMessageBox.warning(self, "警告", "请输入自定义的国家/地区名称")
                return
            country = custom_country

        version = self.version_input.text().strip()
        status = self.status_combo.currentData()
        description = self.description_input.toPlainText().strip()
        tags = self.get_tags()

        try:
            if self.is_edit_mode:
                success, message, regulation = self.regulation_service.update_regulation(
                    self.regulation.id,
                    code=code,
                    name=name,
                    country=country,
                    version=version or None,
                    status=status,
                    description=description or None,
                    tags=tags,
                    updated_by=self.user_id
                )
            else:
                success, message, regulation = self.regulation_service.create_regulation(
                    code=code,
                    name=name,
                    country=country,
                    version=version or None,
                    status=status,
                    description=description or None,
                    created_by=self.user_id,
                    tags=tags
                )

            if success:
                QMessageBox.information(self, "成功", message)

                # 推送更新通知
                if regulation:
                    action = "更新" if self.is_edit_mode else "新增"
                    notification_title = f"法规{action}: {regulation.name}"
                    notification_message = f"法规编号: {regulation.code}\n" \
                                         f"国家/地区: {regulation.country or '未指定'}\n" \
                                         f"版本: {regulation.version or '未指定'}"

                    self.update_service.create_notification(
                        notification_type=NotificationType.REGULATION.value,
                        title=notification_title,
                        message=notification_message,
                        regulation_id=regulation.id
                    )

                self.regulation_saved.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "错误", message)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")