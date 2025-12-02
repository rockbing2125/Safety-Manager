"""
系统常量定义
"""
from enum import Enum


class UserRole(str, Enum):
    """用户角色"""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class RegulationStatus(str, Enum):
    """法规状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class DocumentType(str, Enum):
    """文档类型"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"


class ChangeType(str, Enum):
    """变更类型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class EntityType(str, Enum):
    """实体类型"""
    REGULATION = "regulation"
    DOCUMENT = "document"
    CODE = "code"
    USER = "user"


class SyncStatus(str, Enum):
    """同步状态"""
    PENDING = "pending"
    SYNCING = "syncing"
    SUCCESS = "success"
    FAILED = "failed"


# 用户角色权限映射
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        "read": True,
        "write": True,
        "delete": True,
        "manage_users": True,
        "manage_settings": True,
    },
    UserRole.EDITOR: {
        "read": True,
        "write": True,
        "delete": False,
        "manage_users": False,
        "manage_settings": False,
    },
    UserRole.VIEWER: {
        "read": True,
        "write": False,
        "delete": False,
        "manage_users": False,
        "manage_settings": False,
    },
}


# 国家/地区列表
COUNTRIES = [
    "中国", "美国", "欧盟", "英国", "德国", "法国", "日本",
    "韩国", "澳大利亚", "加拿大", "印度", "巴西", "其他"
]


# 法规分类
REGULATION_CATEGORIES = [
    "电压等级要求",
    "频率响应",
    "功率因数",
    "谐波限制",
    "电压波动",
    "孤岛保护",
    "低电压穿越",
    "高电压穿越",
    "功率控制",
    "通信协议",
    "并网检测",
    "其他"
]


# UI 配置
UI_CONFIG = {
    "window": {
        "min_width": 1200,
        "min_height": 800,
        "default_width": 1400,
        "default_height": 900,
    },
    "colors": {
        "primary": "#1976D2",
        "secondary": "#424242",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
        "info": "#2196F3",
    },
}


# 日志配置
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)