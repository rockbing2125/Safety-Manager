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
        """导入Excel参数（正确处理合并单元格和图片）"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )

        if not file_path:
            return

        try:
            import openpyxl
            from io import BytesIO
            from PyQt6.QtGui import QPixmap, QIcon
            from PyQt6.QtCore import QSize
            import zipfile
            import re

            wb = openpyxl.load_workbook(file_path)
            ws = wb.active

            # 清空
            self.param_table.setRowCount(0)
            self.param_table.clearSpans()

            # 提取Excel中的图片
            image_map = {}  # 存储图片位置映射 {(row, col): QPixmap}
            dispimg_id_map = {}  # 存储DISPIMG ID到图片的映射 {id: QPixmap}

            # 方法1: 从ZIP包中提取所有媒体文件（适用于DISPIMG）
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # 查找所有图片文件
                    for file_name in zip_ref.namelist():
                        if file_name.startswith('xl/media/'):
                            # 提取文件名中的ID或索引
                            image_data = zip_ref.read(file_name)
                            pixmap = QPixmap()
                            if pixmap.loadFromData(image_data):
                                # 使用文件名作为key
                                base_name = file_name.split('/')[-1]
                                dispimg_id_map[base_name] = pixmap
                                print(f"从ZIP提取图片: {base_name}, 尺寸: {pixmap.width()}x{pixmap.height()}")
            except Exception as e:
                print(f"从ZIP提取图片失败: {e}")

            # 方法2: 使用openpyxl的_images（适用于直接插入的图片）
            if hasattr(ws, '_images') and ws._images:
                for idx, img in enumerate(ws._images):
                    try:
                        image_data = img._data()
                        pixmap = QPixmap()
                        if pixmap.loadFromData(image_data):
                            if hasattr(img, 'anchor') and hasattr(img.anchor, '_from'):
                                from_anchor = img.anchor._from
                                row = from_anchor.row - 1
                                col = from_anchor.col
                                if row >= 0 and col < 7:
                                    image_map[(row, col)] = pixmap
                                    print(f"从_images提取图片: 位置({row}, {col})")
                    except Exception as e:
                        print(f"处理_images图片失败: {e}")
                        continue

            # 读取所有数据（从第2行开始，跳过表头）
            # 先用非values_only模式读取，以便获取公式
            all_rows = []
            row_image_info = {}  # {(row, col): image_id}

            for row_idx, excel_row in enumerate(ws.iter_rows(min_row=2, max_col=7)):
                if not excel_row:
                    continue

                # 检查这一行是否有任何非空值
                has_data = any(cell.value is not None for cell in excel_row)
                if not has_data:
                    continue

                row_data = []
                for col_idx, cell in enumerate(excel_row):
                    value = cell.value

                    # 打印单元格信息用于调试
                    if value is not None and col_idx < 7:
                        print(f"Cell({row_idx+2},{col_idx+1}): value={value}, type={type(value)}, data_type={cell.data_type if hasattr(cell, 'data_type') else 'N/A'}")

                    # 检查是否是公式（data_type=='f'表示formula）
                    if hasattr(cell, 'data_type') and cell.data_type == 'f':
                        # 对于公式单元格，value是计算结果，需要获取公式本身
                        formula = cell.value  # 在openpyxl中，公式单元格的value就是公式字符串
                        if isinstance(formula, str) and '_xlfn.DISPIMG' in formula:
                            # 提取ID：=_xlfn.DISPIMG("ID_xxx",1)
                            match = re.search(r'ID_([A-F0-9]+)', formula)
                            if match:
                                image_id = match.group(1)
                                row_image_info[(row_idx, col_idx)] = image_id
                                print(f"✓ 检测到DISPIMG at ({row_idx},{col_idx}): ID_{image_id}")
                            value = "__IMAGE__"
                        elif isinstance(value, str) and '_xlfn.DISPIMG' in str(value):
                            # 如果value本身包含DISPIMG
                            match = re.search(r'ID_([A-F0-9]+)', str(value))
                            if match:
                                image_id = match.group(1)
                                row_image_info[(row_idx, col_idx)] = image_id
                                print(f"✓ 检测到DISPIMG(value) at ({row_idx},{col_idx}): ID_{image_id}")
                            value = "__IMAGE__"

                    row_data.append(str(value) if value is not None else "")
                all_rows.append(row_data)

            # 填充表格
            self.param_table.setRowCount(len(all_rows))

            # 如果有从ZIP提取的图片，按顺序分配给DISPIMG位置
            zip_images_list = list(dispimg_id_map.values())
            dispimg_positions = sorted(row_image_info.keys())  # 按位置排序

            print(f"总共有{len(zip_images_list)}个ZIP图片, {len(dispimg_positions)}个DISPIMG位置")

            # 将ZIP图片按顺序映射到DISPIMG位置
            for idx, pos in enumerate(dispimg_positions):
                if idx < len(zip_images_list):
                    image_map[pos] = zip_images_list[idx]
                    print(f"映射图片{idx}到位置{pos}")

            for row_idx, row_data in enumerate(all_rows):
                # 设置行高（如果该行有图片，设置更大的行高）
                has_image = any((row_idx, col) in image_map for col in range(7))
                if has_image:
                    self.param_table.setRowHeight(row_idx, 80)
                else:
                    self.param_table.setRowHeight(row_idx, 30)

                for col_idx, value in enumerate(row_data):
                    # 检查该位置是否有图片
                    if (row_idx, col_idx) in image_map:
                        # 创建带图片图标的item
                        pixmap = image_map[(row_idx, col_idx)]
                        # 缩放图片到合适大小
                        scaled_pixmap = pixmap.scaled(60, 60, aspectRatioMode=1, transformMode=1)
                        icon = QIcon(scaled_pixmap)
                        item = QTableWidgetItem(icon, "")
                        item.setData(Qt.ItemDataRole.UserRole, "IMAGE")  # 标记为图片
                        print(f"在({row_idx},{col_idx})显示图片")
                    elif value == "__IMAGE__":
                        # 有图片标记但没找到实际图片
                        item = QTableWidgetItem("[图片未提取]")
                        print(f"在({row_idx},{col_idx})无法提取图片")
                    else:
                        item = QTableWidgetItem(value)

                    self.param_table.setItem(row_idx, col_idx, item)

            # 应用合并单元格（对类别列）
            self.apply_category_merge()

            image_count = len(image_map)
            zip_image_count = len(dispimg_id_map)
            dispimg_formula_count = len(dispimg_positions)

            msg = f"✅ 成功导入 {len(all_rows)} 行参数！\n\n"
            msg += f"📊 导入统计:\n"
            msg += f"  • 类别列已自动合并显示\n"
            msg += f"  • 从ZIP提取了 {zip_image_count} 个图片文件\n"
            msg += f"  • 检测到 {dispimg_formula_count} 个DISPIMG公式\n"
            msg += f"  • 成功显示 {image_count} 个图片\n"

            if dispimg_formula_count > image_count:
                msg += f"\n⚠️ 有 {dispimg_formula_count - image_count} 个图片无法显示"

            QMessageBox.information(self, "导入成功", msg)

        except ImportError:
            QMessageBox.critical(self, "错误", "需要: pip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败:\n{str(e)}")
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
                # 处理图片单元格：如果单元格被标记为图片，保存为"[图片]"
                def get_cell_value(row, col):
                    item = self.param_table.item(row, col)
                    if not item:
                        return ""
                    # 检查是否是图片单元格
                    if item.data(Qt.ItemDataRole.UserRole) == "IMAGE":
                        return "[图片]"
                    return item.text()

                category = get_cell_value(row, 0)
                parameter = get_cell_value(row, 1)
                default_val = get_cell_value(row, 2)
                upper = get_cell_value(row, 3)
                lower = get_cell_value(row, 4)
                unit = get_cell_value(row, 5)
                remark = get_cell_value(row, 6)

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