"""
UI样式表
"""

# 现代化深色主题样式
MODERN_STYLE = """
/* 全局样式 */
QWidget {
    background-color: #f5f5f5;
    color: #333333;
    font-family: "Microsoft YaHei UI", "Segoe UI", Arial;
    font-size: 12px;
}

/* 主窗口 */
QMainWindow {
    background-color: #ffffff;
}

/* 菜单栏 */
QMenuBar {
    background-color: #2c3e50;
    color: white;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background-color: #34495e;
    border-radius: 4px;
}

QMenu {
    background-color: white;
    border: 1px solid #ddd;
    padding: 5px;
}

QMenu::item {
    padding: 6px 30px 6px 20px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

/* 工具栏 */
QToolBar {
    background-color: #ecf0f1;
    border-bottom: 1px solid #bdc3c7;
    spacing: 8px;
    padding: 8px;
}

QToolButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QToolButton:hover {
    background-color: #2980b9;
}

QToolButton:pressed {
    background-color: #21618c;
}

/* 按钮 */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #95a5a6;
}

/* 输入框 */
QLineEdit, QTextEdit, QComboBox {
    border: 2px solid #ddd;
    border-radius: 4px;
    padding: 6px 12px;
    background-color: white;
    selection-background-color: #3498db;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 2px solid #3498db;
}

/* 下拉框 */
QComboBox {
    padding: 6px;
    min-width: 120px;
}

QComboBox::drop-down {
    border: none;
    width: 25px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #333;
    margin-right: 5px;
}

/* 表格 */
QTableWidget {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    gridline-color: #e0e0e0;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #f0f0f0;
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QHeaderView::section {
    background-color: #34495e;
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
}

QTableWidget::item:hover {
    background-color: #e8f4f8;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #ddd;
    background-color: white;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #ecf0f1;
    color: #333;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #3498db;
    color: white;
}

QTabBar::tab:hover {
    background-color: #bdc3c7;
}

/* 状态栏 */
QStatusBar {
    background-color: #ecf0f1;
    color: #333;
    border-top: 1px solid #bdc3c7;
}

/* 分组框 */
QGroupBox {
    border: 2px solid #ddd;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 10px;
    background-color: #3498db;
    color: white;
    border-radius: 4px;
}

/* 列表 */
QListWidget {
    border: 2px solid #ddd;
    border-radius: 4px;
    background-color: white;
}

QListWidget::item:selected {
    background-color: #3498db;
    color: white;
}

/* 滚动条 */
QScrollBar:vertical {
    border: none;
    background-color: #f0f0f0;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #95a5a6;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f0f0f0;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-width: 20px;
}
"""

# 浅色主题样式
LIGHT_STYLE = MODERN_STYLE

# 可以导出的样式
__all__ = ['MODERN_STYLE', 'LIGHT_STYLE']