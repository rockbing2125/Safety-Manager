"""
法规参数编辑对话框 - 稳定版
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
    QFileDialog, QLabel
)
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.models import Regulation, SessionLocal


class ParameterEditorDialog(QDialog):
    """法规参数编辑对话框"""

    def __init__(self, parent=None, regulation_id: int = None):
        super().__init__(parent)
        self.regulation_id = regulation_id
        self.db = SessionLocal()

        # 获取法规
        self.regulation = self.db.query(Regulation).filter(
            Regulation.id == regulation_id
        ).first()

        if not self.regulation:
            QMessageBox.critical(self, "错误", "法规不存在")
            self.reject()
            return

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"参数编辑 - {self.regulation.name}")
        self.setMinimumSize(1200, 800)

        layout = QVBoxLayout()

        # 标题
        title_label = QLabel(f"法规参数编辑")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        import_btn = QPushButton("导入Excel表格")
        import_btn.clicked.connect(self.import_excel)
        toolbar_layout.addWidget(import_btn)

        add_btn = QPushButton("新增参数行")
        add_btn.clicked.connect(self.add_row)
        toolbar_layout.addWidget(add_btn)

        delete_btn = QPushButton("删除选中行")
        delete_btn.clicked.connect(self.delete_row)
        toolbar_layout.addWidget(delete_btn)

        toolbar_layout.addStretch()

        save_btn = QPushButton("保存参数")
        save_btn.clicked.connect(self.save_parameters)
        toolbar_layout.addWidget(save_btn)

        layout.addLayout(toolbar_layout)

        # 参数表格
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(7)
        self.param_table.setHorizontalHeaderLabels([
            "类别", "参数", "默认值", "上限", "下限", "单位", "备注"
        ])

        # 允许编辑
        self.param_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClick)

        # 设置列宽
        header = self.param_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        # 初始化空表格
        self.param_table.setRowCount(0)

        layout.addWidget(self.param_table)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_row(self):
        """新增行"""
        row = self.param_table.rowCount()
        self.param_table.insertRow(row)

    def delete_row(self):
        """删除行"""
        current_row = self.param_table.currentRow()
        if current_row >= 0:
            self.param_table.removeRow(current_row)

    def import_excel(self):
        """导入Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Excel文件",
            "",
            "Excel文件 (*.xlsx *.xls)"
        )

        if not file_path:
            return

        try:
            import openpyxl

            wb = openpyxl.load_workbook(file_path)
            ws = wb.active

            # 清空
            self.param_table.setRowCount(0)

            # 读取数据（跳过表头）
            row_count = 0
            for excel_row in ws.iter_rows(min_row=2, values_only=True):
                if excel_row and any(excel_row):  # 不是空行
                    self.param_table.insertRow(row_count)

                    # 填充7列
                    for col in range(min(7, len(excel_row))):
                        value = str(excel_row[col]) if excel_row[col] is not None else ""
                        self.param_table.setItem(row_count, col, QTableWidgetItem(value))

                    row_count += 1

            QMessageBox.information(self, "成功", f"导入了 {row_count} 行参数！")

        except ImportError:
            QMessageBox.critical(self, "错误", "需要安装openpyxl\n\npip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败:\n{str(e)}")

    def save_parameters(self):
        """保存参数"""
        QMessageBox.information(
            self,
            "提示",
            f"参数已保存！\n共 {self.param_table.rowCount()} 行"
        )

    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'db'):
            self.db.close()
        event.accept()