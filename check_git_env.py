"""
Git环境诊断工具
用于检查Git是否正确安装和配置
"""
import subprocess
import sys
from pathlib import Path

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def check_git():
    """检查Git环境"""
    print("=" * 60)
    print("Git 环境诊断")
    print("=" * 60)
    print()

    # 1. 检查Git是否在PATH中
    print("1. 检查 Git 是否在 PATH 中...")
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"   [成功] Git 已安装: {result.stdout.strip()}")
        else:
            print(f"   [失败] Git 命令执行失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   [失败] Git 命令超时（可能未安装或响应很慢）")
        return False
    except FileNotFoundError:
        print("   [失败] Git 未找到，请安装 Git")
        print("   下载地址: https://git-scm.com/downloads")
        return False
    except Exception as e:
        print(f"   [失败] 检查失败: {e}")
        return False

    print()

    # 2. 检查是否在Git仓库中
    print("2. 检查当前目录是否是 Git 仓库...")
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"   [成功] 是 Git 仓库，.git 位于: {result.stdout.strip()}")
        else:
            print("   [失败] 当前目录不是 Git 仓库")
            return False
    except Exception as e:
        print(f"   [失败] 检查失败: {e}")
        return False

    print()

    # 3. 检查远程仓库
    print("3. 检查远程仓库配置...")
    try:
        result = subprocess.run(
            ['git', 'remote', '-v'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout.strip():
            print("   [成功] 远程仓库配置:")
            for line in result.stdout.strip().split('\n'):
                print(f"      {line}")
        else:
            print("   [警告] 未配置远程仓库")
    except Exception as e:
        print(f"   [失败] 检查失败: {e}")

    print()

    # 4. 检查当前分支
    print("4. 检查当前分支...")
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            print(f"   [成功] 当前分支: {branch}")
        else:
            print("   [失败] 获取分支失败")
    except Exception as e:
        print(f"   [失败] 检查失败: {e}")

    print()

    # 5. 检查本地和远程的差异
    print("5. 检查本地和远程的差异...")
    try:
        # 先fetch
        print("   正在获取远程更新...")
        subprocess.run(
            ['git', 'fetch', 'origin'],
            capture_output=True,
            timeout=10
        )

        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD..origin/main'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            behind = int(result.stdout.strip())
            if behind > 0:
                print(f"   [警告] 本地落后远程 {behind} 个提交")
            else:
                print(f"   [成功] 本地是最新的")
        else:
            print("   [警告] 无法比较本地和远程")
    except Exception as e:
        print(f"   [失败] 检查失败: {e}")

    print()
    print("=" * 60)
    print("诊断完成！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    check_git()
    print()
    input("按回车键退出...")
