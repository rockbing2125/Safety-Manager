"""
Git 自动推送服务
用于自动推送版本更新到 GitHub
"""
import sys
from pathlib import Path
import subprocess
import json
from typing import Tuple, Optional
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from shared.config import settings


class GitService:
    """Git 自动推送服务"""

    def __init__(self):
        self.repo_path = settings.BASE_DIR
        self.version_file = self.repo_path / "version.json"
        self.config_file = self.repo_path / "shared" / "config.py"

    def check_git_available(self) -> Tuple[bool, str]:
        """检查 Git 是否可用"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, "Git 未安装或不可用"
        except Exception as e:
            logger.error(f"检查 Git 失败: {e}")
            return False, f"检查失败: {str(e)}"

    def check_repo_status(self) -> Tuple[bool, str]:
        """检查 Git 仓库状态"""
        try:
            # 检查是否是 Git 仓库
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return False, "当前目录不是 Git 仓库"

            # 检查是否有远程仓库
            result = subprocess.run(
                ['git', 'remote', '-v'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            if not result.stdout.strip():
                return False, "未配置远程仓库"

            return True, "仓库状态正常"

        except Exception as e:
            logger.error(f"检查仓库状态失败: {e}")
            return False, f"检查失败: {str(e)}"

    def get_current_version(self) -> Optional[str]:
        """获取当前版本号"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version')
            return None
        except Exception as e:
            logger.error(f"读取版本文件失败: {e}")
            return None

    def update_version_json(self, version: str, download_url: str,
                           changelog: list, required: bool = False,
                           min_version: str = "1.0.0") -> Tuple[bool, str]:
        """更新 version.json 文件"""
        try:
            version_data = {
                "version": version,
                "release_date": datetime.now().strftime("%Y-%m-%d"),
                "download_url": download_url,
                "changelog": changelog,
                "required": required,
                "min_version": min_version
            }

            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, ensure_ascii=False, indent=2)

            logger.info(f"更新 version.json 成功: {version}")
            return True, "版本文件更新成功"

        except Exception as e:
            logger.error(f"更新 version.json 失败: {e}")
            return False, f"更新失败: {str(e)}"

    def update_app_version(self, version: str) -> Tuple[bool, str]:
        """更新 shared/config.py 中的版本号"""
        try:
            if not self.config_file.exists():
                return False, "配置文件不存在"

            # 读取文件内容
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找并替换版本号
            import re
            pattern = r'APP_VERSION:\s*str\s*=\s*["\']([^"\']+)["\']'

            if not re.search(pattern, content):
                return False, "未找到 APP_VERSION 配置"

            new_content = re.sub(
                pattern,
                f'APP_VERSION: str = "{version}"',
                content
            )

            # 写回文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"更新 APP_VERSION 成功: {version}")
            return True, "应用版本号更新成功"

        except Exception as e:
            logger.error(f"更新 APP_VERSION 失败: {e}")
            return False, f"更新失败: {str(e)}"

    def git_add_files(self, files: list) -> Tuple[bool, str]:
        """添加文件到 Git 暂存区"""
        try:
            result = subprocess.run(
                ['git', 'add'] + files,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False, f"添加文件失败: {result.stderr}"

            return True, "文件添加成功"

        except Exception as e:
            logger.error(f"Git add 失败: {e}")
            return False, f"添加失败: {str(e)}"

    def git_commit(self, message: str) -> Tuple[bool, str]:
        """提交更改"""
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                # 检查是否没有更改
                if "nothing to commit" in result.stdout:
                    return True, "没有需要提交的更改"
                return False, f"提交失败: {result.stderr}"

            return True, "提交成功"

        except Exception as e:
            logger.error(f"Git commit 失败: {e}")
            return False, f"提交失败: {str(e)}"

    def git_push(self, github_token: Optional[str] = None) -> Tuple[bool, str]:
        """推送到远程仓库"""
        try:
            # 如果提供了 GitHub Token，配置远程仓库 URL
            if github_token:
                # 获取当前远程仓库 URL
                result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    cwd=str(self.repo_path),
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    origin_url = result.stdout.strip()

                    # 如果是 HTTPS URL，添加 token
                    if origin_url.startswith('https://github.com/'):
                        # 提取仓库路径
                        repo_path = origin_url.replace('https://github.com/', '')
                        # 构建带 token 的 URL
                        auth_url = f'https://{github_token}@github.com/{repo_path}'

                        # 临时设置远程 URL
                        subprocess.run(
                            ['git', 'remote', 'set-url', 'origin', auth_url],
                            cwd=str(self.repo_path),
                            timeout=5
                        )

            # 执行推送
            result = subprocess.run(
                ['git', 'push'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            # 恢复原始 URL（如果使用了 token）
            if github_token:
                subprocess.run(
                    ['git', 'remote', 'set-url', 'origin', origin_url],
                    cwd=str(self.repo_path),
                    timeout=5
                )

            if result.returncode != 0:
                return False, f"推送失败: {result.stderr}"

            return True, "推送成功"

        except Exception as e:
            logger.error(f"Git push 失败: {e}")
            return False, f"推送失败: {str(e)}"

    def push_version_update(self, version: str, download_url: str,
                           changelog: list, required: bool = False,
                           github_token: Optional[str] = None,
                           update_app_version: bool = True) -> Tuple[bool, str]:
        """
        推送版本更新到 GitHub

        完整流程：
        1. 检查 Git 环境
        2. 更新 version.json
        3. 更新 shared/config.py（可选）
        4. Git add
        5. Git commit
        6. Git push
        """
        try:
            # 1. 检查 Git
            logger.info("开始推送版本更新...")

            success, message = self.check_git_available()
            if not success:
                return False, f"Git 检查失败: {message}"

            success, message = self.check_repo_status()
            if not success:
                return False, f"仓库检查失败: {message}"

            # 2. 更新 version.json
            logger.info("更新 version.json...")
            success, message = self.update_version_json(
                version=version,
                download_url=download_url,
                changelog=changelog,
                required=required
            )
            if not success:
                return False, f"更新版本文件失败: {message}"

            files_to_add = ['version.json']

            # 3. 更新 config.py（可选）
            if update_app_version:
                logger.info("更新 shared/config.py...")
                success, message = self.update_app_version(version)
                if not success:
                    logger.warning(f"更新应用版本号失败: {message}")
                else:
                    files_to_add.append('shared/config.py')

            # 4. Git add
            logger.info("添加文件到 Git...")
            success, message = self.git_add_files(files_to_add)
            if not success:
                return False, f"添加文件失败: {message}"

            # 5. Git commit
            commit_message = self._generate_commit_message(version, changelog)
            logger.info("提交更改...")
            success, message = self.git_commit(commit_message)
            if not success:
                return False, f"提交失败: {message}"

            # 6. Git push
            logger.info("推送到 GitHub...")
            success, message = self.git_push(github_token)
            if not success:
                return False, f"推送失败: {message}"

            logger.info(f"版本 {version} 推送成功！")
            return True, f"版本 {version} 已成功推送到 GitHub！"

        except Exception as e:
            logger.error(f"推送版本更新失败: {e}")
            return False, f"推送失败: {str(e)}"

    def _generate_commit_message(self, version: str, changelog: list) -> str:
        """生成 Git 提交信息"""
        message = f"发布 v{version} 版本\n\n"
        message += "更新内容:\n"
        for item in changelog:
            message += f"- {item}\n"
        message += "\n🤖 自动推送 via Safety Manager\n"
        return message

    def test_github_connection(self, github_token: Optional[str] = None) -> Tuple[bool, str]:
        """测试 GitHub 连接"""
        try:
            # 获取远程仓库信息
            result = subprocess.run(
                ['git', 'ls-remote', '--heads', 'origin'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True, "GitHub 连接正常"
            else:
                return False, f"连接失败: {result.stderr}"

        except Exception as e:
            logger.error(f"测试连接失败: {e}")
            return False, f"测试失败: {str(e)}"


# 测试代码
if __name__ == "__main__":
    service = GitService()

    # 测试 Git 可用性
    success, message = service.check_git_available()
    print(f"Git 可用性: {success} - {message}")

    # 测试仓库状态
    success, message = service.check_repo_status()
    print(f"仓库状态: {success} - {message}")

    # 获取当前版本
    version = service.get_current_version()
    print(f"当前版本: {version}")
