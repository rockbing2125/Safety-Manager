"""主窗口"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from client.services import AuthService, RegulationService, SearchService, UpdateService, DataSyncService
from client.utils.data_exporter import DataExporter
from client.utils.data_importer import DataImporter
from shared.config import settings
from shared.constants import COUNTRIES, UI_CONFIG


class UpdateButton(QPushButton):
    """带小红点的更新按钮"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.badge_count = 0
        self.setMinimumWidth(100)

    def set_badge_count(self, count: int):
        """设置小红点数字"""
        self.badge_count = count
        self.update()

    def paintEvent(self, event):
        """重绘事件，添加小红点"""
        super().paintEvent(event)

        if self.badge_count > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 绘制红色圆点
            badge_size = 18
            badge_x = self.width() - badge_size - 5
            badge_y = 5

            # 红色背景
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(badge_x, badge_y, badge_size, badge_size)

            # 白色数字
            painter.setPen(QPen(QColor(255, 255, 255)))
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(10)
            painter.setFont(font)

            text = str(self.badge_count) if self.badge_count < 100 else "99+"
            painter.drawText(badge_x, badge_y, badge_size, badge_size,
                           Qt.AlignmentFlag.AlignCenter, text)


class MainWindow(QMainWindow):
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.regulation_service = RegulationService()
        self.search_service = SearchService()
        self.update_service = UpdateService()
        self.data_sync_service = DataSyncService()
        self.current_user = auth_service.current_user
        self.last_notification_count = None  # 记录上次通知数量，None表示首次检查
        self.init_ui()
        self.load_regulations()
        self.check_data_sync_on_startup()  # 启动时检查数据同步
        self.start_update_check_timer()

    def init_ui(self):
        self.setWindowTitle(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        refresh = QAction("刷新", self)
        refresh.triggered.connect(self.load_regulations)
        file_menu.addAction(refresh)

        file_menu.addSeparator()

        # 导入/导出菜单
        export_action = QAction("导出法规数据...", self)
        export_action.triggered.connect(self.export_regulations)
        file_menu.addAction(export_action)

        import_action = QAction("导入法规数据...", self)
        import_action.triggered.connect(self.import_regulations)
        file_menu.addAction(import_action)
        
        reg_menu = menubar.addMenu("法规")
        add = QAction("新增", self)
        add.triggered.connect(self.add_regulation)
        reg_menu.addAction(add)

        edit = QAction("编辑", self)
        edit.triggered.connect(self.edit_regulation)
        reg_menu.addAction(edit)

        delete = QAction("删除", self)
        delete.triggered.connect(self.delete_regulation)
        reg_menu.addAction(delete)
        
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        toolbar.addAction(QAction("新增法规", self, triggered=self.add_regulation))
        toolbar.addAction(QAction("编辑法规", self, triggered=self.edit_regulation))
        toolbar.addAction(QAction("删除法规", self, triggered=self.delete_regulation))
        toolbar.addSeparator()
        toolbar.addAction(QAction("刷新", self, triggered=self.load_regulations))
        toolbar.addSeparator()

        # 添加带小红点的更新按钮
        self.update_button = UpdateButton("版本更新")
        self.update_button.clicked.connect(self.show_updates)
        toolbar.addWidget(self.update_button)

        # 如果是管理员，添加推送更新按钮
        if self.current_user.role.value == "admin":
            toolbar.addAction(QAction("推送更新", self, triggered=self.push_update))
            toolbar.addAction(QAction("GitHub 推送", self, triggered=self.github_push))
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        search = QHBoxLayout()
        search.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.search_regulations)
        search.addWidget(self.search_input)
        search.addWidget(QPushButton("搜索", clicked=self.search_regulations))
        layout.addLayout(search)

        # 添加提示文字
        hint_label = QLabel("双击法规进行查看法规详情")
        hint_label.setStyleSheet("color: #888; font-size: 11px; padding-left: 5px;")
        layout.addWidget(hint_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["编号", "名称", "国家", "状态", "版本", "时间"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_detail)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # 设置列宽
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        self.table.setColumnWidth(0, 200)  # 编号列
        self.table.setColumnWidth(1, 400)  # 名称列

        layout.addWidget(self.table)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.statusBar().showMessage(f"用户: {self.current_user.username}")

    def load_regulations(self):
        # 创建新的 service 实例以获取最新数据（避免数据库会话缓存问题）
        service = RegulationService()
        regs = service.list_regulations()
        self.table.setRowCount(len(regs))
        for i, r in enumerate(regs):
            # 编号列，并在其中隐藏存储ID
            code_item = QTableWidgetItem(r.code)
            code_item.setData(Qt.ItemDataRole.UserRole, r.id)  # 隐藏存储ID
            self.table.setItem(i, 0, code_item)

            self.table.setItem(i, 1, QTableWidgetItem(r.name))
            self.table.setItem(i, 2, QTableWidgetItem(r.country or ""))
            self.table.setItem(i, 3, QTableWidgetItem(r.status.value))
            self.table.setItem(i, 4, QTableWidgetItem(r.version or ""))
            self.table.setItem(i, 5, QTableWidgetItem(r.created_at.strftime("%Y-%m-%d") if r.created_at else ""))

    def search_regulations(self):
        kw = self.search_input.text().strip()
        regs = self.search_service.search(kw, None, None)
        self.table.setRowCount(len(regs))
        for i, r in enumerate(regs):
            # 编号列，并在其中隐藏存储ID
            code_item = QTableWidgetItem(r.code)
            code_item.setData(Qt.ItemDataRole.UserRole, r.id)  # 隐藏存储ID
            self.table.setItem(i, 0, code_item)

            self.table.setItem(i, 1, QTableWidgetItem(r.name))
            self.table.setItem(i, 2, QTableWidgetItem(r.country or ""))
            self.table.setItem(i, 3, QTableWidgetItem(r.status.value))
            self.table.setItem(i, 4, QTableWidgetItem(r.version or ""))
            self.table.setItem(i, 5, QTableWidgetItem(r.created_at.strftime("%Y-%m-%d") if r.created_at else ""))

    def add_regulation(self):
        from .regulation_dialog import RegulationDialog
        d = RegulationDialog(self, None, self.current_user.id)
        d.regulation_saved.connect(self.load_regulations)
        d.exec()

    def view_detail(self):
        row = self.table.currentRow()
        if row >= 0:
            rid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)  # 从隐藏数据中获取ID
            from .regulation_detail_dialog import RegulationDetailDialog
            d = RegulationDetailDialog(self, rid, self.current_user.id)
            d.exec()

    def edit_regulation(self):
        """编辑选中的法规"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要编辑的法规")
            return

        rid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)  # 从隐藏数据中获取ID
        regulation = self.regulation_service.get_regulation(rid)

        if not regulation:
            QMessageBox.warning(self, "错误", "法规不存在")
            return

        from .regulation_dialog import RegulationDialog
        d = RegulationDialog(self, regulation, self.current_user.id)
        d.regulation_saved.connect(self.load_regulations)
        d.exec()

    def delete_regulation(self):
        """删除选中的法规"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的法规")
            return

        rid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)  # 从隐藏数据中获取ID
        regulation_name = self.table.item(row, 1).text()  # 名称列从第1列改为第1列

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除法规 '{regulation_name}' 吗？\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.regulation_service.delete_regulation(rid, self.current_user.id)
            if success:
                QMessageBox.information(self, "成功", message)
                self.load_regulations()
            else:
                QMessageBox.critical(self, "错误", message)

    def show_context_menu(self, position):
        """显示右键菜单"""
        row = self.table.currentRow()
        if row < 0:
            return

        menu = QMenu(self)

        view_action = QAction("查看详情", self)
        view_action.triggered.connect(self.view_detail)
        menu.addAction(view_action)

        edit_action = QAction("编辑法规", self)
        edit_action.triggered.connect(self.edit_regulation)
        menu.addAction(edit_action)

        menu.addSeparator()

        delete_action = QAction("删除法规", self)
        delete_action.triggered.connect(self.delete_regulation)
        menu.addAction(delete_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def start_update_check_timer(self):
        """启动定时检查更新"""
        # 首次检查
        self.check_for_updates()

        # 每5分钟检查一次
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(5 * 60 * 1000)  # 5分钟

    def check_for_updates(self):
        """检查更新并更新小红点"""
        unread_count = self.update_service.get_unread_count()
        self.update_button.set_badge_count(unread_count)

        # 如果有新的通知，自动弹窗提醒
        # 1. 首次检查（last_notification_count为None）且有未读通知
        # 2. 非首次检查且通知数量增加
        should_alert = False
        if self.last_notification_count is None:
            # 首次检查，如果有未读通知就提醒
            should_alert = unread_count > 0
        else:
            # 非首次检查，只有数量增加时才提醒
            should_alert = unread_count > self.last_notification_count

        if should_alert:
            self.show_notification_alert(unread_count)

        self.last_notification_count = unread_count

    def show_notification_alert(self, count: int):
        """显示新通知提醒"""
        reply = QMessageBox.information(
            self,
            "新消息提醒",
            f"您有 {count} 条未读通知\n\n点击【版本更新】按钮查看详情",
            QMessageBox.StandardButton.Ok
        )

    def show_updates(self):
        """显示更新通知列表"""
        from .update_notifications_dialog import UpdateNotificationsDialog
        dialog = UpdateNotificationsDialog(self, self.update_service)
        dialog.exec()
        # 刷新小红点
        self.check_for_updates()

    def push_update(self):
        """管理员推送更新通知"""
        if self.current_user.role.value != "admin":
            QMessageBox.warning(self, "权限不足", "只有管理员可以推送更新")
            return

        from .push_update_dialog import PushUpdateDialog
        dialog = PushUpdateDialog(self, self.update_service)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "成功", "更新通知已推送")
            self.check_for_updates()

    def github_push(self):
        """GitHub 自动推送版本更新"""
        if self.current_user.role.value != "admin":
            QMessageBox.warning(self, "权限不足", "只有管理员可以推送更新")
            return

        from .github_push_dialog import GitHubPushDialog
        dialog = GitHubPushDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 推送成功后，刷新版本检查
            self.check_for_updates()

    def export_regulations(self):
        """导出法规数据"""
        from PyQt6.QtWidgets import QFileDialog

        # 选择导出格式
        format_reply = QMessageBox.question(
            self,
            "选择导出格式",
            "请选择导出格式：\n\n"
            "【是】- 导出为 Excel 文件（推荐）\n"
            "【否】- 导出为 JSON 文件",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )

        if format_reply == QMessageBox.StandardButton.Cancel:
            return

        is_excel = format_reply == QMessageBox.StandardButton.Yes

        # 选择保存路径
        if is_excel:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出法规数据",
                f"regulations_{settings.APP_VERSION}.xlsx",
                "Excel文件 (*.xlsx)"
            )
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出法规数据",
                f"regulations_{settings.APP_VERSION}.json",
                "JSON文件 (*.json)"
            )

        if not file_path:
            return

        # 执行导出
        try:
            exporter = DataExporter()
            if is_excel:
                success, message = exporter.export_to_excel(file_path)
            else:
                success, message = exporter.export_to_json(file_path)

            if success:
                reply = QMessageBox.information(
                    self,
                    "导出成功",
                    f"{message}\n\n文件路径: {file_path}\n\n"
                    f"您可以：\n"
                    f"1. 将此文件分享给其他用户\n"
                    f"2. 推送到 Git 仓库进行版本管理\n"
                    f"3. 作为数据备份保存\n\n"
                    f"是否打开文件所在文件夹？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )

                if reply == QMessageBox.StandardButton.Yes:
                    import subprocess
                    subprocess.run(['explorer', '/select,', file_path.replace('/', '\\')])
            else:
                QMessageBox.critical(self, "导出失败", message)
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出过程中出错: {str(e)}")

    def import_regulations(self):
        """导入法规数据"""
        from PyQt6.QtWidgets import QFileDialog

        # 选择文件
        file_path, file_type = QFileDialog.getOpenFileName(
            self,
            "导入法规数据",
            "",
            "支持的文件 (*.xlsx *.json);;Excel文件 (*.xlsx);;JSON文件 (*.json)"
        )

        if not file_path:
            return

        # 询问是否覆盖已存在的法规
        overwrite_reply = QMessageBox.question(
            self,
            "导入选项",
            "如果法规编号已存在，是否覆盖？\n\n"
            "【是】- 覆盖已存在的法规（更新数据）\n"
            "【否】- 跳过已存在的法规（只导入新法规）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.No
        )

        if overwrite_reply == QMessageBox.StandardButton.Cancel:
            return

        overwrite = overwrite_reply == QMessageBox.StandardButton.Yes

        # 执行导入
        try:
            importer = DataImporter()

            if file_path.endswith('.xlsx'):
                success, message, stats = importer.import_from_excel(
                    file_path, self.current_user.id, overwrite
                )
            elif file_path.endswith('.json'):
                success, message, stats = importer.import_from_json(
                    file_path, self.current_user.id, overwrite
                )
            else:
                QMessageBox.warning(self, "错误", "不支持的文件格式")
                return

            if success:
                # 显示详细统计
                detail_msg = message
                if stats.get('errors'):
                    detail_msg += f"\n\n错误详情（前5条）:\n"
                    for error in stats['errors'][:5]:
                        detail_msg += f"• {error}\n"

                QMessageBox.information(self, "导入完成", detail_msg)

                # 刷新列表
                self.load_regulations()
            else:
                QMessageBox.critical(self, "导入失败", message)
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入过程中出错: {str(e)}")

    def check_data_sync_on_startup(self):
        """启动时检查数据同步"""
        from client.ui.data_sync_dialog import DataSyncDialog

        # 检查Git是否可用
        success, _ = self.data_sync_service.check_git_available()
        if not success:
            # Git不可用，跳过检查
            return

        # 检查是否有数据更新
        try:
            has_update, update_info = self.data_sync_service.check_for_data_updates()

            if has_update and update_info:
                # 有更新，显示对话框
                dialog = DataSyncDialog(self, update_info)
                result = dialog.exec()

                if result == QDialog.DialogCode.Accepted:
                    # 用户选择同步并成功，重新加载数据
                    QMessageBox.information(
                        self,
                        "数据已更新",
                        "数据同步成功！正在重新加载...",
                        QMessageBox.StandardButton.Ok
                    )
                    self.load_regulations()
        except Exception as e:
            # 检查失败，静默处理
            from loguru import logger
            logger.warning(f"启动时检查数据同步失败: {e}")

    def closeEvent(self, event):
        self.auth_service.logout()
        event.accept()