"""
法规选择器对话框
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services import RegulationService


class RegulationSelectorDialog(QDialog):
    """法规选择器对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_regulation_id = None
        self.regulation_service = RegulationService()
        self.init_ui()
        self.load_regulations()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("选择法规")
        self.setMinimumSize(800, 500)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 搜索栏
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入法规编号或名称进行搜索...")
        self.search_input.textChanged.connect(self.search_regulations)
        search_layout.addWidget(self.search_input)

        layout.addLayout(search_layout)

        # 法规列表
        self.regulation_table = QTableWidget()
        self.regulation_table.setColumnCount(4)
        self.regulation_table.setHorizontalHeaderLabels([
            "ID", "编号", "名称", "国家/地区"
        ])
        self.regulation_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.regulation_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.regulation_table.doubleClicked.connect(self.select_and_close)

        # 设置行高
        self.regulation_table.verticalHeader().setDefaultSectionSize(40)
        self.regulation_table.verticalHeader().setMinimumSectionSize(40)

        # 设置列宽
        header = self.regulation_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.regulation_table.setColumnWidth(0, 60)   # ID
        self.regulation_table.setColumnWidth(1, 150)  # 编号
        self.regulation_table.setColumnWidth(2, 400)  # 名称
        header.setStretchLastSection(True)            # 国家/地区

        layout.addWidget(self.regulation_table)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        select_btn = QPushButton("选择")
        select_btn.setMinimumWidth(100)
        select_btn.clicked.connect(self.select_regulation)
        button_layout.addWidget(select_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_regulations(self):
        """加载法规列表"""
        regulations = self.regulation_service.list_regulations()
        self.display_regulations(regulations)

    def search_regulations(self):
        """搜索法规"""
        keyword = self.search_input.text().strip()
        if keyword:
            from client.services import SearchService
            search_service = SearchService()
            regulations = search_service.search(keyword, None, None)
        else:
            regulations = self.regulation_service.list_regulations()

        self.display_regulations(regulations)

    def display_regulations(self, regulations):
        """显示法规列表"""
        self.regulation_table.setRowCount(len(regulations))

        for row, reg in enumerate(regulations):
            # ID（隐藏存储）
            id_item = QTableWidgetItem(str(reg.id))
            id_item.setData(Qt.ItemDataRole.UserRole, reg.id)
            self.regulation_table.setItem(row, 0, id_item)

            self.regulation_table.setItem(row, 1, QTableWidgetItem(reg.code))
            self.regulation_table.setItem(row, 2, QTableWidgetItem(reg.name))
            self.regulation_table.setItem(row, 3, QTableWidgetItem(reg.country or ""))

    def select_regulation(self):
        """选择法规"""
        selected_rows = self.regulation_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请选择一个法规")
            return

        row = self.regulation_table.currentRow()
        self.selected_regulation_id = int(self.regulation_table.item(row, 0).text())
        self.accept()

    def select_and_close(self):
        """双击选择并关闭"""
        self.select_regulation()
