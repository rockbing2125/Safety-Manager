"""
Git 自动推送服务
用于自动推送版本更新到 GitHub
"""
import sys
from pathlib import Path
import subprocess
import json
import requests
from typing import Tuple, Optional
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from shared.config import settings, BASE_DIR


class GitService:
    """Git 自动推送服务"""

    def __init__(self):
        self.repo_path = self._find_git_repo_root()
        self.version_file = self.repo_path / "version.json"
        self.config_file = self.repo_path / "shared" / "config.py"

    def _find_git_repo_root(self) -> Path:
        """查找 Git 仓库根目录"""
        # 从 BASE_DIR 开始向上查找 .git 目录
        current = BASE_DIR
        max_levels = 5  # 最多向上查找5级

        for _ in range(max_levels):
            if (current / ".git").exists():
                return current
            parent = current.parent
            if parent == current:  # 到达根目录
                break
            current = parent

        # 如果没找到，返回 BASE_DIR（开发环境）
        return BASE_DIR

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

    def _get_repo_info(self) -> Optional[Tuple[str, str]]:
        """
        获取仓库信息（owner/repo）

        Returns:
            (owner, repo) 或 None
        """
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            url = result.stdout.strip()

            # 解析 GitHub URL
            # https://github.com/owner/repo.git
            # git@github.com:owner/repo.git
            if 'github.com' in url:
                if url.startswith('https://'):
                    # https://github.com/owner/repo.git
                    parts = url.replace('https://github.com/', '').replace('.git', '').split('/')
                elif url.startswith('git@'):
                    # git@github.com:owner/repo.git
                    parts = url.replace('git@github.com:', '').replace('.git', '').split('/')
                else:
                    return None

                if len(parts) >= 2:
                    return parts[0], parts[1]

            return None

        except Exception as e:
            logger.error(f"获取仓库信息失败: {e}")
            return None

    def create_github_release(self, version: str, changelog: list,
                             github_token: str, release_file: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        创建 GitHub Release 并上传文件

        Args:
            version: 版本号（如 "1.1.4"）
            changelog: 更新日志列表
            github_token: GitHub Token
            release_file: 要上传的文件路径（可选）

        Returns:
            (成功, 消息, 下载链接)
        """
        try:
            # 获取仓库信息
            repo_info = self._get_repo_info()
            if not repo_info:
                return False, "无法获取仓库信息，请检查是否配置了 GitHub 远程仓库", None

            owner, repo = repo_info
            tag_name = f"v{version}"

            # 构建 Release 描述
            changelog_text = "\n".join([f"- {item}" for item in changelog])
            release_body = f"""## 更新内容

{changelog_text}

## 下载说明
1. 下载下方的压缩包
2. 解压到任意目录
3. 运行程序即可自动更新

---
🤖 自动发布 via Safety Manager"""

            # 创建 Release
            logger.info(f"正在创建 GitHub Release: {tag_name}")

            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            release_data = {
                'tag_name': tag_name,
                'name': f"SafetyManager v{version}",
                'body': release_body,
                'draft': False,
                'prerelease': False
            }

            response = requests.post(api_url, headers=headers, json=release_data, timeout=30)

            if response.status_code == 201:
                release_info = response.json()
                release_id = release_info['id']
                logger.info(f"Release 创建成功: {release_id}")

                # 如果提供了文件，上传文件
                if release_file and Path(release_file).exists():
                    success, message, download_url = self.upload_release_asset(
                        release_id, release_file, github_token
                    )
                    if success:
                        return True, f"Release 创建成功并上传文件完成", download_url
                    else:
                        return False, f"Release 创建成功但上传文件失败: {message}", None
                else:
                    # 没有文件，返回成功
                    return True, "Release 创建成功", None

            elif response.status_code == 422:
                # Release 已存在，尝试获取
                logger.warning(f"Release {tag_name} 已存在，尝试更新...")
                return self._update_existing_release(owner, repo, tag_name, changelog, github_token, release_file)
            else:
                error_msg = response.json().get('message', '未知错误')
                return False, f"创建 Release 失败: {error_msg}", None

        except requests.exceptions.Timeout:
            return False, "创建 Release 超时，请检查网络连接", None
        except Exception as e:
            logger.error(f"创建 GitHub Release 失败: {e}")
            return False, f"创建失败: {str(e)}", None

    def _update_existing_release(self, owner: str, repo: str, tag_name: str,
                                changelog: list, github_token: str,
                                release_file: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """更新已存在的 Release"""
        try:
            # 获取已存在的 Release
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag_name}"
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code != 200:
                return False, f"获取已存在的 Release 失败", None

            release_info = response.json()
            release_id = release_info['id']

            # 上传文件（如果提供）
            if release_file and Path(release_file).exists():
                success, message, download_url = self.upload_release_asset(
                    release_id, release_file, github_token
                )
                if success:
                    return True, "已更新现有 Release 并上传文件", download_url
                else:
                    return False, f"上传文件失败: {message}", None
            else:
                return True, "Release 已存在", None

        except Exception as e:
            logger.error(f"更新 Release 失败: {e}")
            return False, f"更新失败: {str(e)}", None

    def upload_release_asset(self, release_id: int, file_path: str,
                            github_token: str) -> Tuple[bool, str, Optional[str]]:
        """
        上传文件到 GitHub Release

        Args:
            release_id: Release ID
            file_path: 文件路径
            github_token: GitHub Token

        Returns:
            (成功, 消息, 下载链接)
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return False, f"文件不存在: {file_path}", None

            # 获取仓库信息
            repo_info = self._get_repo_info()
            if not repo_info:
                return False, "无法获取仓库信息", None

            owner, repo = repo_info
            file_name = file_path_obj.name

            logger.info(f"正在上传文件: {file_name} ({file_path_obj.stat().st_size / 1024 / 1024:.2f} MB)")

            # 上传文件
            upload_url = f"https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets"
            headers = {
                'Authorization': f'token {github_token}',
                'Content-Type': 'application/zip'
            }
            params = {'name': file_name}

            with open(file_path, 'rb') as f:
                response = requests.post(
                    upload_url,
                    headers=headers,
                    params=params,
                    data=f,
                    timeout=300  # 5分钟超时
                )

            if response.status_code == 201:
                asset_info = response.json()
                download_url = asset_info['browser_download_url']
                logger.info(f"文件上传成功: {download_url}")
                return True, "文件上传成功", download_url
            else:
                error_msg = response.json().get('message', '未知错误')
                return False, f"上传失败: {error_msg}", None

        except requests.exceptions.Timeout:
            return False, "上传超时，文件可能太大或网络不稳定", None
        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            return False, f"上传失败: {str(e)}", None

    def push_release_with_file(self, version: str, changelog: list,
                               github_token: str, release_file: str,
                               update_app_version: bool = True,
                               required: bool = False) -> Tuple[bool, str]:
        """
        完整的发布流程：创建 Release、上传文件、更新 version.json

        Args:
            version: 版本号
            changelog: 更新日志
            github_token: GitHub Token
            release_file: 发布文件路径
            update_app_version: 是否更新 config.py
            required: 是否强制更新

        Returns:
            (成功, 消息)
        """
        try:
            logger.info("开始完整发布流程...")

            # 1. 检查文件
            if not Path(release_file).exists():
                return False, f"发布文件不存在: {release_file}"

            # 2. 创建 Release 并上传文件
            logger.info("创建 GitHub Release 并上传文件...")
            success, message, download_url = self.create_github_release(
                version, changelog, github_token, release_file
            )

            if not success or not download_url:
                return False, f"创建 Release 失败: {message}"

            logger.info(f"Release 创建成功，下载链接: {download_url}")

            # 3. 更新 version.json
            logger.info("更新 version.json...")
            success, msg = self.update_version_json(
                version=version,
                download_url=download_url,
                changelog=changelog,
                required=required
            )

            if not success:
                return False, f"更新 version.json 失败: {msg}"

            files_to_add = ['version.json']

            # 4. 更新 config.py（可选）
            if update_app_version:
                logger.info("更新 shared/config.py...")
                success, msg = self.update_app_version(version)
                if success:
                    files_to_add.append('shared/config.py')

            # 5. Git 提交和推送
            logger.info("提交并推送到 GitHub...")
            success, msg = self.git_add_files(files_to_add)
            if not success:
                return False, f"添加文件失败: {msg}"

            commit_message = self._generate_commit_message(version, changelog)
            success, msg = self.git_commit(commit_message)
            if not success and "nothing to commit" not in msg:
                return False, f"提交失败: {msg}"

            success, msg = self.git_push(github_token)
            if not success:
                return False, f"推送失败: {msg}"

            logger.info(f"版本 {version} 发布成功！")
            return True, f"版本 {version} 发布成功！\n下载链接: {download_url}"

        except Exception as e:
            logger.error(f"发布流程失败: {e}")
            return False, f"发布失败: {str(e)}"


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
