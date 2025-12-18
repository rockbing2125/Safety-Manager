"""
全局配置文件
"""
import os
import sys
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


def get_base_dir() -> Path:
    """获取程序根目录（支持打包后的环境）"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境：使用可执行文件所在目录
        # PyInstaller 会将所有文件放在 _internal 目录，但数据应该在可执行文件同级的 data 目录
        exe_dir = Path(sys.executable).parent
        # 如果当前在 _internal 目录，返回父目录
        if exe_dir.name == '_internal':
            return exe_dir.parent
        return exe_dir
    else:
        # 开发环境：使用项目根目录
        return Path(__file__).resolve().parent.parent


def get_resource_path(relative_path: str) -> Path:
    """获取资源文件路径（支持打包环境）

    在打包环境下，资源文件在 _MEIPASS 目录（即 _internal）
    在开发环境下，资源文件在项目根目录
    """
    if getattr(sys, 'frozen', False):
        # 打包后的环境：使用 PyInstaller 的临时目录
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境：使用项目根目录
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path


# 项目根目录
BASE_DIR = get_base_dir()

# 数据目录
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
CODES_DIR = DATA_DIR / "codes"
DATABASES_DIR = DATA_DIR / "databases"

# 确保目录存在
for directory in [DATA_DIR, DOCUMENTS_DIR, CODES_DIR, DATABASES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def ensure_database_exists():
    """确保数据库文件存在（首次运行时从打包资源复制）"""
    if not getattr(sys, 'frozen', False):
        # 开发环境不需要复制
        return

    # 打包环境：检查数据库是否存在
    target_db = DATABASES_DIR / "regulations.db"

    if target_db.exists():
        # 数据库已存在，不覆盖用户数据
        return

    # 数据库不存在，从打包资源复制
    source_db = get_resource_path("data/databases/regulations.db")

    if source_db.exists():
        import shutil
        # 确保目标目录存在
        target_db.parent.mkdir(parents=True, exist_ok=True)
        # 复制数据库
        shutil.copy2(source_db, target_db)
        print(f"✓ 已从打包资源复制数据库到: {target_db}")


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "并网法规管理系统"
    APP_VERSION: str = "1.1.8"
    APP_DESCRIPTION: str = "Grid Regulation Management System"

    # 数据库配置 - SQLite (本地)
    # 默认使用程序目录下的本地数据库，支持开箱即用
    # 高级用户可通过 .env 文件中的 DATABASE_PATH 指定网络共享路径
    # 例如: DATABASE_PATH=\\192.168.1.100\SafetyManager\regulations.db
    DATABASE_PATH: str = Field(default="", env="DATABASE_PATH")

    @property
    def SQLITE_DB_PATH(self) -> Path:
        """获取SQLite数据库路径（支持本地和网络共享）"""
        if self.DATABASE_PATH:
            return Path(self.DATABASE_PATH)
        return DATABASES_DIR / "regulations.db"

    # 数据库配置 - PostgreSQL (服务器)
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="regulations", env="POSTGRES_DB")

    @property
    def postgres_url(self) -> str:
        """PostgreSQL 连接 URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sqlite_url(self) -> str:
        """SQLite 连接 URL"""
        return f"sqlite:///{self.SQLITE_DB_PATH}"

    # 服务器配置
    SERVER_HOST: str = Field(default="http://localhost", env="SERVER_HOST")
    SERVER_PORT: int = Field(default=8000, env="SERVER_PORT")

    @property
    def server_url(self) -> str:
        """服务器 URL"""
        return f"{self.SERVER_HOST}:{self.SERVER_PORT}"

    # JWT 配置
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_DOCUMENT_EXTENSIONS: set = {".pdf", ".docx", ".doc"}
    ALLOWED_CODE_EXTENSIONS: set = {".c", ".h", ".cpp", ".hpp"}

    # 搜索配置
    SEARCH_INDEX_DIR: Path = DATA_DIR / "search_index"
    SEARCH_RESULTS_PER_PAGE: int = 20

    # 日志配置
    LOG_DIR: Path = DATA_DIR / "logs"
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # 离线模式配置
    OFFLINE_MODE: bool = Field(default=True, env="OFFLINE_MODE")
    AUTO_SYNC: bool = Field(default=True, env="AUTO_SYNC")
    SYNC_INTERVAL: int = 300  # 秒

    # 版本更新配置
    # 支持静态文件服务（推荐）或完整API服务器
    # 静态文件示例：将 version.json 上传到任意文件托管服务
    # - GitHub: https://raw.githubusercontent.com/rockbing2125/Safety-Manager/main/version.json
    # - 阿里云OSS: https://your-bucket.oss-cn-beijing.aliyuncs.com/version.json
    # - 腾讯云COS: https://your-bucket.cos.ap-beijing.myqcloud.com/version.json
    # - Gitee: https://gitee.com/your-username/your-repo/raw/master/version.json
    UPDATE_CHECK_URL: str = Field(
        default="https://raw.githubusercontent.com/rockbing2125/Safety-Manager/main/version.json",
        env="UPDATE_CHECK_URL"
    )
    AUTO_UPDATE: bool = Field(default=True, env="AUTO_UPDATE")

    # GitHub 自动推送配置（管理员功能）
    # GitHub Personal Access Token，用于自动推送版本更新
    # 获取方式：https://github.com/settings/tokens
    # 需要权限：repo（完整仓库访问权限）
    GITHUB_TOKEN: str = Field(default="", env="GITHUB_TOKEN")

    class Config:
        # .env文件是可选的，不存在时使用默认配置
        # 打包后从可执行文件目录读取，开发环境从项目根目录读取
        env_file = str(BASE_DIR / ".env") if BASE_DIR else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # 允许.env文件不存在
        extra = "allow"


# 创建全局配置实例
settings = Settings()

# 确保搜索索引目录存在
settings.SEARCH_INDEX_DIR.mkdir(parents=True, exist_ok=True)
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)