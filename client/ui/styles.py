"""
UI样式表 - 现代化美观设计
"""

# 现代化美观主题样式
MODERN_STYLE = """
/* ========== 全局样式 ========== */
QWidget {
    background-color: #f8f9fa;
    color: #2c3e50;
    font-family: "Microsoft YaHei UI", "Segoe UI", "PingFang SC", Arial;
    font-size: 13px;
}

QMainWindow {
    background-color: #f8f9fa;
}

/* ========== 菜单栏 ========== */
QMenuBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2c3e50, stop:1 #34495e);
    color: white;
    padding: 6px;
    border-bottom: 2px solid #3498db;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: rgba(52, 152, 219, 0.3);
}

QMenuBar::item:pressed {
    background-color: #3498db;
}

QMenu {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 8px 0px;
}

QMenu::item {
    padding: 8px 40px 8px 25px;
    border-radius: 4px;
    margin: 2px 8px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

QMenu::separator {
    height: 1px;
    background: #e0e0e0;
    margin: 6px 16px;
}

/* ========== 工具栏 ========== */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffffff, stop:1 #f5f6fa);
    border-bottom: 2px solid #e1e4e8;
    spacing: 6px;
    padding: 10px;
}

QToolBar::separator {
    background: #d1d5db;
    width: 1px;
    margin: 6px 8px;
}

QToolButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
}

QToolButton:hover {
    background-color: #2980b9;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

QToolButton:pressed {
    background-color: #21618c;
    transform: translateY(1px);
}

/* ========== 按钮 ========== */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3498db, stop:1 #2980b9);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
    min-height: 28px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2980b9, stop:1 #21618c);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4);
}

QPushButton:pressed {
    background-color: #1c5380;
    padding-top: 11px;
    padding-bottom: 9px;
}

QPushButton:disabled {
    background: #bdc3c7;
    color: #7f8c8d;
}

QPushButton:focus {
    outline: none;
    border: 2px solid #5dade2;
}

/* ========== 输入框 ========== */
QLineEdit, QTextEdit {
    border: 2px solid #e1e4e8;
    border-radius: 6px;
    padding: 6px 12px;
    background-color: transparent;
    selection-background-color: #3498db;
    font-size: 13px;
    min-height: 18px;
}

QLineEdit:hover, QTextEdit:hover {
    border-color: #cbd5e0;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #3498db;
    background-color: #f8fbff;
}

QLineEdit:disabled, QTextEdit:disabled {
    background-color: rgba(245, 246, 250, 0.3);
    color: #95a5a6;
    border-color: #e1e4e8;
}

/* ========== 下拉框 ========== */
QComboBox {
    border: 2px solid #e1e4e8;
    border-radius: 6px;
    padding: 7px 12px;
    background-color: transparent;
    min-width: 120px;
    font-size: 13px;
}

QComboBox:hover {
    border-color: #cbd5e0;
}

QComboBox:focus {
    border: 2px solid #3498db;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #7f8c8d;
    margin-right: 8px;
}

QComboBox::down-arrow:hover {
    border-top-color: #3498db;
}

QComboBox QAbstractItemView {
    border: 2px solid #e1e4e8;
    border-radius: 6px;
    background-color: #ffffff;
    selection-background-color: #3498db;
    selection-color: white;
    padding: 4px;
}

/* ========== 表格 ========== */
QTableWidget {
    background-color: white;
    border: 2px solid #e1e4e8;
    border-radius: 8px;
    gridline-color: #f0f0f0;
    alternate-background-color: #f8f9fa;
}

QTableWidget::item {
    padding: 12px 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QTableWidget::item:hover {
    background-color: #e3f2fd;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #34495e, stop:1 #2c3e50);
    color: white;
    padding: 12px 8px;
    border: none;
    border-right: 1px solid #1a252f;
    font-weight: 600;
    font-size: 13px;
}

QHeaderView::section:first {
    border-top-left-radius: 6px;
}

QHeaderView::section:last {
    border-top-right-radius: 6px;
    border-right: none;
}

QHeaderView::section:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3d5a71, stop:1 #34495e);
}

/* ========== 标签页 ========== */
QTabWidget::pane {
    border: 2px solid #e1e4e8;
    background-color: white;
    border-radius: 8px;
    top: -2px;
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ecf0f1, stop:1 #d5dbdd);
    color: #2c3e50;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3498db, stop:1 #2980b9);
    color: white;
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #d5dbdd, stop:1 #bdc3c7);
}

/* ========== 状态栏 ========== */
QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f5f6fa, stop:1 #e8eaf0);
    color: #2c3e50;
    border-top: 2px solid #e1e4e8;
    font-size: 12px;
    padding: 4px 8px;
}

/* ========== 分组框 ========== */
QGroupBox {
    border: 2px solid #e1e4e8;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 18px;
    font-weight: 600;
    font-size: 14px;
    background-color: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 6px 14px;
    margin-left: 12px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3498db, stop:1 #2980b9);
    color: white;
    border-radius: 5px;
    font-weight: 600;
}

/* ========== 列表 ========== */
QListWidget {
    border: 2px solid #e1e4e8;
    border-radius: 8px;
    background-color: white;
    padding: 4px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QListWidget::item:hover:!selected {
    background-color: #e3f2fd;
}

/* ========== 滚动条 ========== */
QScrollBar:vertical {
    border: none;
    background-color: #f5f6fa;
    width: 14px;
    border-radius: 7px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e0;
    border-radius: 7px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0aec0;
}

QScrollBar::handle:vertical:pressed {
    background-color: #718096;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f5f6fa;
    height: 14px;
    border-radius: 7px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e0;
    border-radius: 7px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0aec0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========== 进度条 ========== */
QProgressBar {
    border: 2px solid #e1e4e8;
    border-radius: 6px;
    background-color: white;
    text-align: center;
    font-weight: 600;
    height: 24px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3498db, stop:1 #2ecc71);
    border-radius: 4px;
}

/* ========== 对话框 ========== */
QDialog {
    background-color: #f8f9fa;
}

/* ========== 标签 ========== */
QLabel {
    color: #2c3e50;
    background: transparent;
}
"""

# 浅色主题样式
LIGHT_STYLE = MODERN_STYLE

# 可以导出的样式
__all__ = ['MODERN_STYLE', 'LIGHT_STYLE']