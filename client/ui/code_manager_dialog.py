"""
代码管理对话框
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QHeaderView, QComboBox, QLabel
)
from PyQt6.QtCore import Qt
import subprocess
import platform

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.models import SessionLocal, CodeFile, Regulation
from client.services import RegulationService


class CodeManagerDialog(QDialog):
    """代码管理对话框"""

    def __init__(self, parent=None, user_id: int = None):
        super().__init__(parent)
        self.user_id = user_id
        self.regulation_service = RegulationService()
        self.db = SessionLocal()
        self.init_ui()
        self.load_codes()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("代码文件管理")
        self.setMinimumSize(900, 600)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 工具栏
        toolbar = QHBoxLayout()

        upload_btn = QPushButton("上传代码文件")
        upload_btn.clicked.connect(self.upload_code)
        toolbar.addWidget(upload_btn)

        view_btn = QPushButton("查看代码")
        view_btn.clicked.connect(self.view_code)
        toolbar.addWidget(view_btn)

        delete_btn = QPushButton("删除代码")
        delete_btn.clicked.connect(self.delete_code)
        toolbar.addWidget(delete_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 代码列表
        self.code_table = QTableWidget()
        self.code_table.setColumnCount(5)
        self.code_table.setHorizontalHeaderLabels([
            "ID", "文件名", "版本", "说明", "创建时间"
        ])
        self.code_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.code_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.code_table.doubleClicked.connect(self.view_code)

        # 设置行高
        self.code_table.verticalHeader().setDefaultSectionSize(40)
        self.code_table.verticalHeader().setMinimumSectionSize(40)

        # 设置列宽
        header = self.code_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.code_table.setColumnWidth(0, 60)   # ID
        self.code_table.setColumnWidth(1, 250)  # 文件名
        self.code_table.setColumnWidth(2, 100)  # 版本
        self.code_table.setColumnWidth(3, 300)  # 说明
        header.setStretchLastSection(True)      # 创建时间

        layout.addWidget(self.code_table)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_codes(self):
        """加载代码列表"""
        codes = self.db.query(CodeFile).order_by(
            CodeFile.created_at.desc()
        ).all()

        self.code_table.setRowCount(len(codes))

        for row, code in enumerate(codes):
            self.code_table.setItem(row, 0, QTableWidgetItem(str(code.id)))
            self.code_table.setItem(row, 1, QTableWidgetItem(code.file_name))
            self.code_table.setItem(row, 2, QTableWidgetItem(code.version or ""))
            self.code_table.setItem(row, 3, QTableWidgetItem(code.description or ""))

            time_str = code.created_at.strftime("%Y-%m-%d %H:%M") if code.created_at else ""
            self.code_table.setItem(row, 4, QTableWidgetItem(time_str))

    def upload_code(self):
        """上传代码文件"""
        # 选择法规
        from .regulation_selector_dialog import RegulationSelectorDialog
        selector = RegulationSelectorDialog(self)
        if selector.exec() != QDialog.DialogCode.Accepted:
            return

        regulation_id = selector.selected_regulation_id
        if not regulation_id:
            QMessageBox.warning(self, "提示", "请选择法规")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择代码文件", "",
            "代码文件 (*.py *.cpp *.c *.h *.java *.js *.ts *.go *.rs);;所有文件 (*.*)"
        )

        if not file_path:
            return

        success, message, _ = self.regulation_service.add_code_file(
            regulation_id, file_path, None, None, self.user_id
        )

        if success:
            QMessageBox.information(self, "成功", message)
            self.load_codes()
        else:
            QMessageBox.critical(self, "错误", message)

    def view_code(self):
        """查看代码"""
        selected_rows = self.code_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请选择要查看的代码文件")
            return

        row = self.code_table.currentRow()
        code_id = int(self.code_table.item(row, 0).text())

        code = self.db.query(CodeFile).filter(CodeFile.id == code_id).first()
        if not code:
            QMessageBox.critical(self, "错误", "代码文件不存在")
            return

        file_path = Path(code.file_path)
        if not file_path.exists():
            QMessageBox.critical(self, "错误", "文件不存在")
            return

        try:
            if platform.system() == 'Windows':
                subprocess.run(['start', '', str(file_path)], shell=True, check=True)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(file_path)], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(file_path)], check=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")

    def delete_code(self):
        """删除代码"""
        selected_rows = self.code_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请选择要删除的代码文件")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除选中的代码文件吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        row = self.code_table.currentRow()
        code_id = int(self.code_table.item(row, 0).text())

        success, message = self.regulation_service.delete_code_file(code_id, self.user_id)

        if success:
            QMessageBox.information(self, "成功", message)
            self.load_codes()
        else:
            QMessageBox.critical(self, "错误", message)

    def closeEvent(self, event):
        """关闭事件"""
        self.db.close()
        super().closeEvent(event)
