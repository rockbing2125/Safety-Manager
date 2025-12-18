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

from client.models import Regulation, RegulationParameter, SessionLocal


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
        self.load_parameters()

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

        generate_code_btn = QPushButton("参数代码合成")
        generate_code_btn.clicked.connect(self.generate_c_code)
        toolbar_layout.addWidget(generate_code_btn)

        toolbar_layout.addStretch()

        save_btn = QPushButton("保存参数")
        save_btn.clicked.connect(self.save_parameters)
        toolbar_layout.addWidget(save_btn)

        layout.addLayout(toolbar_layout)

        # 参数表格
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(9)
        self.param_table.setHorizontalHeaderLabels([
            "类别", "参数", "默认值", "上限", "下限", "单位", "系数", "协议位", "备注"
        ])

        # 允许编辑
        self.param_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClick)

        # 设置列宽
        header = self.param_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)

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

                    # 填充9列
                    for col in range(min(9, len(excel_row))):
                        value = str(excel_row[col]) if excel_row[col] is not None else ""
                        self.param_table.setItem(row_count, col, QTableWidgetItem(value))

                    row_count += 1

            QMessageBox.information(self, "成功", f"导入了 {row_count} 行参数！")

        except ImportError:
            QMessageBox.critical(self, "错误", "需要安装openpyxl\n\npip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败:\n{str(e)}")

    def load_parameters(self):
        """从数据库加载参数"""
        try:
            parameters = self.db.query(RegulationParameter).filter(
                RegulationParameter.regulation_id == self.regulation_id
            ).order_by(RegulationParameter.row_order).all()

            self.param_table.setRowCount(len(parameters))

            for row, param in enumerate(parameters):
                # 列索引：0类别, 1参数, 2默认值, 3上限, 4下限, 5单位, 6系数, 7协议位, 8备注
                self.param_table.setItem(row, 0, QTableWidgetItem(param.category or ""))
                self.param_table.setItem(row, 1, QTableWidgetItem(param.parameter_name or ""))
                self.param_table.setItem(row, 2, QTableWidgetItem(param.default_value or ""))
                self.param_table.setItem(row, 3, QTableWidgetItem(param.upper_limit or ""))
                self.param_table.setItem(row, 4, QTableWidgetItem(param.lower_limit or ""))
                self.param_table.setItem(row, 5, QTableWidgetItem(param.unit or ""))
                self.param_table.setItem(row, 6, QTableWidgetItem(param.coefficient or ""))
                self.param_table.setItem(row, 7, QTableWidgetItem(param.protocol_bit or ""))
                self.param_table.setItem(row, 8, QTableWidgetItem(param.remark or ""))

        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载参数失败: {str(e)}")

    def save_parameters(self):
        """保存参数到数据库"""
        try:
            # 删除旧的参数
            self.db.query(RegulationParameter).filter(
                RegulationParameter.regulation_id == self.regulation_id
            ).delete()

            # 保存新的参数
            for row in range(self.param_table.rowCount()):
                # 列索引：0类别, 1参数, 2默认值, 3上限, 4下限, 5单位, 6系数, 7协议位, 8备注
                category = self.param_table.item(row, 0).text() if self.param_table.item(row, 0) else ""
                param_name = self.param_table.item(row, 1).text() if self.param_table.item(row, 1) else ""
                default_val = self.param_table.item(row, 2).text() if self.param_table.item(row, 2) else ""
                upper = self.param_table.item(row, 3).text() if self.param_table.item(row, 3) else ""
                lower = self.param_table.item(row, 4).text() if self.param_table.item(row, 4) else ""
                unit = self.param_table.item(row, 5).text() if self.param_table.item(row, 5) else ""
                coef = self.param_table.item(row, 6).text() if self.param_table.item(row, 6) else ""
                protocol = self.param_table.item(row, 7).text() if self.param_table.item(row, 7) else ""
                remark = self.param_table.item(row, 8).text() if self.param_table.item(row, 8) else ""

                param = RegulationParameter(
                    regulation_id=self.regulation_id,
                    category=category,
                    parameter_name=param_name,
                    default_value=default_val,
                    upper_limit=upper,
                    lower_limit=lower,
                    unit=unit,
                    coefficient=coef,
                    protocol_bit=protocol,
                    remark=remark,
                    row_order=row
                )
                self.db.add(param)

            self.db.commit()
            QMessageBox.information(
                self,
                "成功",
                f"参数已保存！\n共 {self.param_table.rowCount()} 行"
            )

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")

    def generate_c_code(self):
        """生成C代码文件"""
        try:
            # 读取模板文件
            template_path = Path(__file__).resolve().parent.parent.parent / "Satety_Parameter.c"
            if not template_path.exists():
                QMessageBox.critical(self, "错误", f"模板文件不存在: {template_path}")
                return

            with open(template_path, 'r', encoding='utf-8') as f:
                template_lines = f.readlines()

            # 收集表格数据，按协议位建立索引
            protocol_data = {}
            for row in range(self.param_table.rowCount()):
                # 列索引：0类别, 1参数, 2默认值, 3上限, 4下限, 5单位, 6系数, 7协议位, 8备注
                protocol_item = self.param_table.item(row, 7)  # 协议位
                default_item = self.param_table.item(row, 2)   # 默认值
                coef_item = self.param_table.item(row, 6)      # 系数

                protocol = protocol_item.text().strip() if protocol_item else ""
                default_val = default_item.text().strip() if default_item else ""
                coef = coef_item.text().strip() if coef_item else ""

                # 如果协议位是"-"或为空，跳过
                if protocol == "-" or not protocol:
                    continue

                # 如果默认值是"-"或为空，设置为0
                if default_val == "-" or not default_val:
                    calculated_value = 0
                else:
                    try:
                        # 计算：默认值 / 系数
                        if coef and coef != "-" and float(coef) != 0:
                            calculated_value = float(default_val) / float(coef)
                        else:
                            calculated_value = float(default_val)

                        # 四舍五入取整
                        calculated_value = int(round(calculated_value))
                    except (ValueError, ZeroDivisionError):
                        calculated_value = 0

                protocol_data[protocol] = calculated_value

            # 生成新的C代码
            new_lines = []
            for i, line in enumerate(template_lines):
                # 跳过前4行（注释和列标题）
                if i < 4:
                    new_lines.append(line)
                    continue

                # 最后一行
                if line.strip() == "};":
                    new_lines.append(line)
                    continue

                # 解析数据行
                if "//" in line and "{" in line:
                    # 提取注释部分的协议位
                    comment_part = line.split("//")[1].strip()
                    protocol_match = comment_part.split()[0] if comment_part else ""

                    # 查找协议位对应的值
                    if protocol_match in protocol_data:
                        value = protocol_data[protocol_match]
                    else:
                        value = 0

                    # 处理负数
                    if value < 0:
                        default_str = f"(Uint16){value}"
                    else:
                        default_str = str(value)

                    # 重新构建这一行，保留原来的MIN、MAX和注释
                    # 提取原来的MIN和MAX
                    data_part = line.split("{")[1].split("}")[0]
                    parts = [p.strip() for p in data_part.split(",")]

                    if len(parts) >= 3:
                        min_val = parts[1]
                        max_val = parts[2]
                    else:
                        min_val = "32768"
                        max_val = "32767"

                    # 提取完整注释
                    full_comment = line.split("//")[1] if "//" in line else ""

                    # 格式化新行
                    new_line = f"    {{   {default_str:<7} ,   {min_val:<6} ,   {max_val:<6} }},   // {full_comment}"
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)

            # 选择保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存C代码文件",
                f"{self.regulation.name}_Parameter.c",
                "C文件 (*.c)"
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)

                QMessageBox.information(self, "成功", f"C代码文件已生成：\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败:\n{str(e)}")

    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'db'):
            self.db.close()
        event.accept()