"""
UI界面模块
"""
from .main_window import MainWindow
from .login_dialog import LoginDialog
from .regulation_dialog import RegulationDialog
from .regulation_detail_dialog import RegulationDetailDialog

__all__ = [
    "MainWindow",
    "LoginDialog",
    "RegulationDialog",
    "RegulationDetailDialog",
]