"""
法规详情查看对话框
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView,
    QFormLayout, QListWidget, QFileDialog  # 添加QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import subprocess
import platform

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.models import Regulation, SessionLocal, ChangeHistory
from client.services import RegulationService
from shared.constants import DocumentType, EntityType, ChangeType


class RegulationDetailDialog(QDialog):
    """法规详情查看对话框"""

    def __init__(self, parent=None, regulation_id: int = None, user_id: int = None):
        super().__init__(parent)
        self.regulation_id = regulation_id
        self.user_id = user_id
        self.regulation_service = RegulationService()
        self.db = SessionLocal()

        self.regulation = self.regulation_service.get_regulation(regulation_id)
        if not self.regulation:
            QMessageBox.critical(self, "错误", "法规不存在")
            self.reject()
            return

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"法规详情 - {self.regulation.name}")
        self.setMinimumSize(900, 700)
        self.setModal(True)

        layout = QVBoxLayout()

        # 标题（美化）
        title_label = QLabel(self.regulation.name)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)

        # 标签页
        self.tab_widget = QTabWidget()

        # 基本信息
        self.tab_widget.addTab(self.create_info_tab(), "基本信息")

        #参数编辑
        self.tab_widget.addTab(self.create_parameters_tab(), "参数编辑")  # 新增
		
        # 文档列表
        self.tab_widget.addTab(self.create_documents_tab(), "法规文档")

        # 代码列表
        self.tab_widget.addTab(self.create_codes_tab(), "代码文件")

        # 历史记录
        self.tab_widget.addTab(self.create_history_tab(), "历史记录")

        layout.addWidget(self.tab_widget)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_info_tab(self):
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.addRow("法规编号:", QLabel(self.regulation.code))
        form_layout.addRow("法规名称:", QLabel(self.regulation.name))
        form_layout.addRow("国家/地区:", QLabel(self.regulation.country or ""))
        form_layout.addRow("分类:", QLabel(self.regulation.category or ""))
        form_layout.addRow("版本号:", QLabel(self.regulation.version or ""))
        form_layout.addRow("状态:", QLabel(self.regulation.status.value))

        if self.regulation.created_at:
            form_layout.addRow("创建时间:", QLabel(self.regulation.created_at.strftime("%Y-%m-%d %H:%M:%S")))

        layout.addLayout(form_layout)

        # 标签
        if self.regulation.tags:
            layout.addWidget(QLabel("标签:"))
            tag_list = QListWidget()
            tag_list.setMaximumHeight(100)
            for tag in self.regulation.tags:
                tag_list.addItem(tag.name)
            layout.addWidget(tag_list)

        # 描述
        layout.addWidget(QLabel("描述:"))
        desc_text = QTextEdit()
        desc_text.setPlainText(self.regulation.description or "")
        desc_text.setReadOnly(True)
        layout.addWidget(desc_text)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_documents_tab(self):
        """创建文档标签页"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 工具栏
        toolbar = QHBoxLayout()

        upload_btn = QPushButton("上传文档")
        upload_btn.clicked.connect(self.upload_document)
        toolbar.addWidget(upload_btn)

        view_btn = QPushButton("查看文档")
        view_btn.clicked.connect(self.view_document)
        toolbar.addWidget(view_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 文档列表
        self.doc_table = QTableWidget()
        self.doc_table.setColumnCount(5)
        self.doc_table.setHorizontalHeaderLabels([
            "ID", "文件名", "类型", "大小", "上传时间"
        ])
        self.doc_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.doc_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.doc_table.doubleClicked.connect(self.view_document)

        header = self.doc_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.doc_table)

        widget.setLayout(layout)
        return widget

    def create_codes_tab(self):
        """创建代码标签页"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 工具栏
        toolbar = QHBoxLayout()

        upload_btn = QPushButton("上传代码")
        upload_btn.clicked.connect(self.upload_code)
        toolbar.addWidget(upload_btn)

        view_btn = QPushButton("查看代码")
        view_btn.clicked.connect(self.view_code)
        toolbar.addWidget(view_btn)

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

        header = self.code_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.code_table)

        widget.setLayout(layout)
        return widget

    def create_history_tab(self):
        """创建历史记录标签页"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 历史记录列表
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "变更类型", "变更摘要", "操作人", "变更时间"
        ])
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.history_table)

        widget.setLayout(layout)
        return widget

    def load_data(self):
        """加载所有数据"""
        self.load_documents()
        self.load_codes()
        self.load_history()

    def load_documents(self):
        """加载文档列表"""
        documents = self.regulation.documents
        self.doc_table.setRowCount(len(documents))

        for row, doc in enumerate(documents):
            self.doc_table.setItem(row, 0, QTableWidgetItem(str(doc.id)))
            self.doc_table.setItem(row, 1, QTableWidgetItem(doc.file_name))
            self.doc_table.setItem(row, 2, QTableWidgetItem(doc.doc_type.value.upper()))

            size_kb = doc.file_size / 1024 if doc.file_size else 0
            size_str = f"{size_kb:.2f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
            self.doc_table.setItem(row, 3, QTableWidgetItem(size_str))

            time_str = doc.upload_at.strftime("%Y-%m-%d %H:%M") if doc.upload_at else ""
            self.doc_table.setItem(row, 4, QTableWidgetItem(time_str))

    def load_codes(self):
        """加载代码列表"""
        codes = self.regulation.code_files
        self.code_table.setRowCount(len(codes))

        for row, code in enumerate(codes):
            self.code_table.setItem(row, 0, QTableWidgetItem(str(code.id)))
            self.code_table.setItem(row, 1, QTableWidgetItem(code.file_name))
            self.code_table.setItem(row, 2, QTableWidgetItem(code.version or ""))
            self.code_table.setItem(row, 3, QTableWidgetItem(code.description or ""))

            time_str = code.created_at.strftime("%Y-%m-%d %H:%M") if code.created_at else ""
            self.code_table.setItem(row, 4, QTableWidgetItem(time_str))

    def load_history(self):
        """加载历史记录"""
        history = self.db.query(ChangeHistory).filter(
            ChangeHistory.entity_type == EntityType.REGULATION,
            ChangeHistory.entity_id == self.regulation_id
        ).order_by(ChangeHistory.changed_at.desc()).all()

        self.history_table.setRowCount(len(history))

        for row, record in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(record.change_type.value))
            self.history_table.setItem(row, 1, QTableWidgetItem(record.change_summary or ""))

            user_name = record.user.username if record.user else "系统"
            self.history_table.setItem(row, 2, QTableWidgetItem(user_name))

            time_str = record.changed_at.strftime("%Y-%m-%d %H:%M:%S") if record.changed_at else ""
            self.history_table.setItem(row, 3, QTableWidgetItem(time_str))

    def upload_document(self):
        """上传文档"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文档文件", "", "文档文件 (*.pdf *.docx *.doc)"
        )

        if not file_path:
            return

        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            doc_type = DocumentType.PDF
        elif ext in ['.docx', '.doc']:
            doc_type = DocumentType.DOCX
        else:
            QMessageBox.warning(self, "警告", "不支持的文件类型")
            return

        success, message, document = self.regulation_service.add_document(
            self.regulation_id, file_path, doc_type, self.user_id
        )

        if success:
            QMessageBox.information(self, "成功", message)
            self.load_documents()
        else:
            QMessageBox.critical(self, "错误", message)

    def view_document(self):
        """查看文档"""
        current_row = self.doc_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要查看的文档")
            return

        doc_id = int(self.doc_table.item(current_row, 0).text())
        document = next((d for d in self.regulation.documents if d.id == doc_id), None)

        if not document:
            QMessageBox.warning(self, "警告", "文档不存在")
            return

        file_path = Path(document.file_path)
        if not file_path.exists():
            QMessageBox.warning(self, "警告", "文件不存在")
            return

        try:
            if platform.system() == 'Windows':
                subprocess.run(['start', '', str(file_path)], shell=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', str(file_path)])
            else:
                subprocess.run(['xdg-open', str(file_path)])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")

    def upload_code(self):
        """上传代码"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择C代码文件", "", "C代码文件 (*.c *.h *.cpp *.hpp)"
        )

        if not file_path:
            return

        # 简化版：直接上传
        success, message, code_file = self.regulation_service.add_code_file(
            regulation_id=self.regulation_id,
            file_path=file_path,
            description="C代码文件",
            usage_guide="请查看代码注释",
            version="1.0",
            created_by=self.user_id
        )

        if success:
            QMessageBox.information(self, "成功", message)
            self.load_codes()
        else:
            QMessageBox.critical(self, "错误", message)

    def view_code(self):
        """查看代码"""
        current_row = self.code_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要查看的代码")
            return

        code_id = int(self.code_table.item(current_row, 0).text())
        code_file = next((c for c in self.regulation.code_files if c.id == code_id), None)

        if not code_file:
            QMessageBox.warning(self, "警告", "代码文件不存在")
            return

        # 使用系统默认程序打开
        file_path = Path(code_file.file_path)
        if not file_path.exists():
            QMessageBox.warning(self, "警告", "文件不存在")
            return

        try:
            if platform.system() == 'Windows':
                subprocess.run(['start', '', str(file_path)], shell=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', str(file_path)])
            else:
                subprocess.run(['xdg-open', str(file_path)])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")

    def create_parameters_tab(self):
        """创建参数编辑标签页"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 工具栏
        toolbar_layout = QHBoxLayout()

        import_btn = QPushButton("导入Excel表格")
        import_btn.clicked.connect(self.import_excel_parameters)
        toolbar_layout.addWidget(import_btn)

        add_row_btn = QPushButton("新增行")
        add_row_btn.clicked.connect(self.add_parameter_row)
        toolbar_layout.addWidget(add_row_btn)

        delete_row_btn = QPushButton("删除选中行")
        delete_row_btn.clicked.connect(self.delete_parameter_row)
        toolbar_layout.addWidget(delete_row_btn)

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

        # 允许单击编辑
        self.param_table.setEditTriggers(QTableWidget.EditTrigger.SelectedClicked | QTableWidget.EditTrigger.AnyKeyPressed)

        # 设置列宽
        header = self.param_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.param_table)

        widget.setLayout(layout)
		
		 # 加载已保存的参数
        self.load_saved_parameters()  # 添加这一行
		
        return widget

    def add_parameter_row(self):
        """新增参数行"""
        row = self.param_table.rowCount()
        self.param_table.insertRow(row)

    def delete_parameter_row(self):
        """删除选中的参数行"""
        current_row = self.param_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self,
                "确认删除",
                "确定要删除这一行吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.param_table.removeRow(current_row)

    def import_excel_parameters(self):
        """导入Excel参数（正确处理合并单元格）"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )

        if not file_path:
            return

        try:
            import openpyxl

            wb = openpyxl.load_workbook(file_path)
            ws = wb.active

            # 清空
            self.param_table.setRowCount(0)
            self.param_table.clearSpans()

            # 读取所有数据（从第2行开始，跳过表头）
            all_rows = []
            for excel_row in ws.iter_rows(min_row=2, values_only=True):
                if excel_row and any(cell is not None for cell in excel_row[:7]):
                    row_data = []
                    for col_idx in range(7):
                        value = excel_row[col_idx] if col_idx < len(excel_row) else None
                        row_data.append(str(value) if value is not None else "")
                    all_rows.append(row_data)

            # 填充表格
            self.param_table.setRowCount(len(all_rows))
            for row_idx, row_data in enumerate(all_rows):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(value)
                    self.param_table.setItem(row_idx, col_idx, item)

            # 应用合并单元格（对类别列）
            self.apply_category_merge()

            QMessageBox.information(
                self, "导入成功",
                f"成功导入 {len(all_rows)} 行参数！\n\n"
                f"类别列已自动合并显示。"
            )

        except ImportError:
            QMessageBox.critical(self, "错误", "需要: pip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败:\n{str(e)}")


            # 应用合并单元格（仅对前7列）
            for (table_row, table_col), (row_span, col_span) in merge_info.items():
                if table_col < 7:  # 只合并前7列
                    # 确保不超出表格范围
                    if table_row < self.param_table.rowCount():
                        actual_row_span = min(row_span, self.param_table.rowCount() - table_row)
                        actual_col_span = min(col_span, 7 - table_col)
                        
                        self.param_table.setSpan(table_row, table_col, actual_row_span, actual_col_span)

            QMessageBox.information(
                self,
                "导入成功",
                f"成功导入 {row_count} 行参数数据！\n\n"
                f"合并单元格已正确显示。\n"
                f"双击单元格可编辑。"
            )

        except ImportError:
            QMessageBox.critical(
                self,
                "错误",
                "需要安装openpyxl库\n\n"
                "请执行: pip install openpyxl"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "导入失败",
                f"Excel导入失败:\n\n{str(e)}"
            )
            import traceback
            traceback.print_exc()

    def save_parameters(self):
        """保存参数到数据库"""
        row_count = self.param_table.rowCount()

        if row_count == 0:
            QMessageBox.warning(self, "提示", "没有参数需要保存")
            return

        try:
            from client.models import RegulationParameter

            # 删除现有参数
            self.db.query(RegulationParameter).filter(
                RegulationParameter.regulation_id == self.regulation_id
            ).delete()

            # 保存新参数
            saved_count = 0
            for row in range(row_count):
                category = self.param_table.item(row, 0).text() if self.param_table.item(row, 0) else ""
                parameter = self.param_table.item(row, 1).text() if self.param_table.item(row, 1) else ""
                default_val = self.param_table.item(row, 2).text() if self.param_table.item(row, 2) else ""
                upper = self.param_table.item(row, 3).text() if self.param_table.item(row, 3) else ""
                lower = self.param_table.item(row, 4).text() if self.param_table.item(row, 4) else ""
                unit = self.param_table.item(row, 5).text() if self.param_table.item(row, 5) else ""
                remark = self.param_table.item(row, 6).text() if self.param_table.item(row, 6) else ""

                param = RegulationParameter(
                    regulation_id=self.regulation_id,
                    category=category,
                    parameter_name=parameter,
                    default_value=default_val,
                    upper_limit=upper,
                    lower_limit=lower,
                    unit=unit,
                    remark=remark,
                    row_order=row
                )
                self.db.add(param)
                saved_count += 1

            # 提交
            self.db.commit()

            # 记录历史
            if self.user_id:
                ChangeHistory.create_change_record(
                    self.db, EntityType.REGULATION, self.regulation_id,
                    ChangeType.UPDATE, {"parameter_count": saved_count},
                    f"编辑参数: 保存了 {saved_count} 个参数", self.user_id
                )

            QMessageBox.information(
                self, "保存成功",
                f"成功保存 {saved_count} 个参数！\n\n数据已保存到数据库。"
            )

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "保存失败", f"保存失败:\n{str(e)}")

    def load_saved_parameters(self):
        """加载已保存的参数"""
        try:
            from client.models import RegulationParameter

            params = self.db.query(RegulationParameter).filter(
                RegulationParameter.regulation_id == self.regulation_id
            ).order_by(RegulationParameter.row_order).all()

            if params and len(params) > 0:
                self.param_table.setRowCount(0)
                self.param_table.clearSpans()

                for row, param in enumerate(params):
                    self.param_table.insertRow(row)
                    self.param_table.setItem(row, 0, QTableWidgetItem(param.category or ""))
                    self.param_table.setItem(row, 1, QTableWidgetItem(param.parameter_name or ""))
                    self.param_table.setItem(row, 2, QTableWidgetItem(param.default_value or ""))
                    self.param_table.setItem(row, 3, QTableWidgetItem(param.upper_limit or ""))
                    self.param_table.setItem(row, 4, QTableWidgetItem(param.lower_limit or ""))
                    self.param_table.setItem(row, 5, QTableWidgetItem(param.unit or ""))
                    self.param_table.setItem(row, 6, QTableWidgetItem(param.remark or ""))

                self.apply_category_merge()

        except:
            pass

    def apply_category_merge(self):
        """自动合并类别列"""
        row_count = self.param_table.rowCount()
        if row_count == 0:
            return

        i = 0
        while i < row_count:
            category_item = self.param_table.item(i, 0)
            if category_item and category_item.text().strip():
                category = category_item.text().strip()
                start_row = i
                
                j = i + 1
                while j < row_count:
                    next_item = self.param_table.item(j, 0)
                    next_category = next_item.text().strip() if next_item else ""
                    
                    if not next_category or next_category == category:
                        j += 1
                    else:
                        break
                
                span = j - start_row
                if span > 1:
                    self.param_table.setSpan(start_row, 0, span, 1)
                
                i = j
            else:
                i += 1

    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'db'):
            self.db.close()
        event.accept()