#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速启动脚本
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """检查依赖"""
    print("正在检查依赖...")
    try:
        import PyQt6
        import sqlalchemy
        import bcrypt
        import loguru
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("\n请运行: pip install -r requirements.txt")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("并网法规管理系统")
    print("=" * 60)

    if not check_dependencies():
        print("\n按回车键退出...")
        input()
        return 1

    print("\n正在启动程序...")
    try:
        from client import main as client_main
        return client_main.main()
    except Exception as e:
        print(f"\n程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n按回车键退出...")
        input()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n致命错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n按回车键退出...")
        input()
        sys.exit(1)