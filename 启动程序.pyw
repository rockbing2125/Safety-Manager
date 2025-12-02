#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
静默启动脚本（无CMD窗口）
"""
import sys
import os

# 隐藏控制台窗口（Windows）
if sys.platform == 'win32':
    import ctypes
    import ctypes.wintypes

    # 获取控制台窗口句柄
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, 0)  # SW_HIDE = 0

# 重定向输出
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    from client import main as client_main
    sys.exit(client_main.main())
