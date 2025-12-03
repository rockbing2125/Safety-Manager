"""
数据同步服务
用于检查和拉取远程仓库的数据更新
"""
import sys
from pathlib import Path
import subprocess
from typing import Tuple, Optional, List, Dict
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from shared.config import BASE_DIR


class DataSyncService:
    """数据同步服务"""

    def __init__(self):
        self.repo_path = self._find_git_repo_root()
        self.data_files = ['RDB/', 'data/', '*.db', '*.sqlite']  # 监控的数据相关文件

    def _find_git_repo_root(self) -> Path:
        """查找 Git 仓库根目录"""
        current = BASE_DIR
        max_levels = 5

        for _ in range(max_levels):
            if (current / ".git").exists():
                return current
            parent = current.parent
            if parent == current:
                break
            current = parent

        return BASE_DIR

    def check_git_available(self) -> Tuple[bool, str]:
        """检查 Git 是否可用"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=3,  # 减少超时时间
                cwd=str(self.repo_path),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            if result.returncode == 0:
                return True, "Git 可用"
            return False, "Git 未安装或不可用"
        except subprocess.TimeoutExpired:
            logger.warning("Git 检查超时")
            return False, "Git 检查超时，可能未安装"
        except FileNotFoundError:
            logger.warning("Git 未找到")
            return False, "Git 未安装，请先安装 Git"
        except Exception as e:
            logger.error(f"检查 Git 失败: {e}")
            return False, "Git 不可用"

    def fetch_remote_updates(self) -> Tuple[bool, str]:
        """从远程仓库获取更新（不合并）"""
        try:
            result = subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if "Could not resolve host" in error_msg or "Failed to connect" in error_msg:
                    return False, "网络连接失败，无法连接到远程仓库"
                return False, f"获取更新失败: {error_msg}"

            logger.info("成功从远程仓库获取更新")
            return True, "获取更新成功"

        except subprocess.TimeoutExpired:
            return False, "获取更新超时，请检查网络连接"
        except Exception as e:
            logger.error(f"获取更新失败: {e}")
            return False, f"获取更新失败: {str(e)}"

    def check_for_data_updates(self) -> Tuple[bool, Optional[Dict]]:
        """
        检查是否有数据更新

        Returns:
            (有更新, 更新信息)
        """
        try:
            # 先获取远程更新
            success, message = self.fetch_remote_updates()
            if not success:
                logger.warning(f"无法获取远程更新: {message}")
                return False, None

            # 获取当前分支
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, None

            branch = result.stdout.strip()

            # 比较本地和远程
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'HEAD..origin/{branch}'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, None

            commits_behind = int(result.stdout.strip())

            if commits_behind == 0:
                logger.info("本地已是最新版本")
                return False, None

            # 获取远程提交信息
            update_info = self._get_remote_commit_info(branch, commits_behind)
            logger.info(f"发现 {commits_behind} 个新提交")
            return True, update_info

        except Exception as e:
            logger.error(f"检查数据更新失败: {e}")
            return False, None

    def _get_remote_commit_info(self, branch: str, count: int = 5) -> Dict:
        """获取远程提交信息"""
        try:
            # 获取提交历史
            result = subprocess.run(
                ['git', 'log', f'HEAD..origin/{branch}',
                 '--pretty=format:%H|%an|%ae|%ai|%s',
                 f'-{count}'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )

            commits = []
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0][:8],
                            'author': parts[1],
                            'email': parts[2],
                            'date': parts[3],
                            'message': parts[4]
                        })

            # 获取变更的文件
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'HEAD..origin/{branch}'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )

            changed_files = []
            if result.returncode == 0:
                changed_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]

            # 判断是否包含数据文件
            has_data_changes = any(
                any(pattern in file for pattern in ['RDB/', 'data/', '.db', '.sqlite'])
                for file in changed_files
            )

            return {
                'branch': branch,
                'commits': commits,
                'total_commits': len(commits),
                'changed_files': changed_files,
                'has_data_changes': has_data_changes
            }

        except Exception as e:
            logger.error(f"获取提交信息失败: {e}")
            return {
                'branch': branch,
                'commits': [],
                'total_commits': 0,
                'changed_files': [],
                'has_data_changes': False
            }

    def pull_updates(self) -> Tuple[bool, str]:
        """拉取并应用远程更新"""
        try:
            # 检查本地是否有未提交的更改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.stdout.strip():
                # 有未提交的更改，需要先暂存
                logger.info("检测到本地有未提交的更改，尝试暂存...")
                stash_result = subprocess.run(
                    ['git', 'stash', 'push', '-m', f'Auto stash before pull {datetime.now()}'],
                    cwd=str(self.repo_path),
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if stash_result.returncode != 0:
                    return False, f"暂存本地更改失败: {stash_result.stderr}"

            # 执行 pull
            result = subprocess.run(
                ['git', 'pull', '--rebase'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                return False, f"拉取更新失败: {error_msg}"

            logger.info("成功拉取远程更新")
            return True, "数据更新成功"

        except subprocess.TimeoutExpired:
            return False, "拉取更新超时"
        except Exception as e:
            logger.error(f"拉取更新失败: {e}")
            return False, f"拉取更新失败: {str(e)}"

    def get_local_changes(self) -> List[str]:
        """获取本地未提交的更改"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                changes = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                return changes
            return []

        except Exception as e:
            logger.error(f"获取本地更改失败: {e}")
            return []

    def get_current_branch(self) -> str:
        """获取当前分支名"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception as e:
            logger.error(f"获取分支名失败: {e}")
            return "unknown"


# 测试代码
if __name__ == "__main__":
    service = DataSyncService()

    # 测试检查更新
    has_update, update_info = service.check_for_data_updates()
    print(f"有更新: {has_update}")
    if update_info:
        print(f"更新信息: {update_info}")
