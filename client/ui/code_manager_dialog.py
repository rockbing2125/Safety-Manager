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
        # 允许单击编辑
        self.code_table.setEditTriggers(
            QTableWidget.EditTrigger.SelectedClicked |
            QTableWidget.EditTrigger.DoubleClicked
        )
        # 连接编辑完成信号
        self.code_table.itemChanged.connect(self.on_item_changed)
        # 双击文件名列时查看代码
        self.code_table.cellDoubleClicked.connect(self.on_cell_double_clicked)

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
        # 暂时断开信号，避免加载时触发编辑事件
        self.code_table.itemChanged.disconnect(self.on_item_changed)

        codes = self.db.query(CodeFile).order_by(
            CodeFile.created_at.desc()
        ).all()

        self.code_table.setRowCount(len(codes))

        for row, code in enumerate(codes):
            # ID - 不可编辑
            id_item = QTableWidgetItem(str(code.id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.code_table.setItem(row, 0, id_item)

            # 文件名 - 不可编辑
            filename_item = QTableWidgetItem(code.file_name)
            filename_item.setFlags(filename_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.code_table.setItem(row, 1, filename_item)

            # 版本 - 可编辑
            version_item = QTableWidgetItem(code.version or "")
            self.code_table.setItem(row, 2, version_item)

            # 说明 - 可编辑
            desc_item = QTableWidgetItem(code.description or "")
            self.code_table.setItem(row, 3, desc_item)

            # 创建时间 - 不可编辑
            time_str = code.created_at.strftime("%Y-%m-%d %H:%M") if code.created_at else ""
            time_item = QTableWidgetItem(time_str)
            time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.code_table.setItem(row, 4, time_item)

        # 重新连接信号
        self.code_table.itemChanged.connect(self.on_item_changed)

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

    def on_item_changed(self, item):
        """单元格内容改变时保存到数据库"""
        row = item.row()
        col = item.column()

        # 只处理版本(2)和说明(3)列
        if col not in [2, 3]:
            return

        code_id = int(self.code_table.item(row, 0).text())
        code = self.db.query(CodeFile).filter(CodeFile.id == code_id).first()

        if not code:
            return

        try:
            if col == 2:  # 版本列
                code.version = item.text().strip() or None
            elif col == 3:  # 说明列
                code.description = item.text().strip() or None

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def on_cell_double_clicked(self, row, col):
        """双击单元格时的处理"""
        # 只有双击文件名列(1)时才查看代码
        if col == 1:
            self.view_code()

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
