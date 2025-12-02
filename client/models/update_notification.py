"""
更新通知模型
"""
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from .database import Base
from enum import Enum as PyEnum


class NotificationType(str, PyEnum):
    """通知类型"""
    SOFTWARE = "software"  # 软件版本更新
    REGULATION = "regulation"  # 法规内容更新


class UpdateNotification(Base):
    """更新通知表"""

    __tablename__ = "update_notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # software 或 regulation
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)  # 版本号（软件更新时使用）
    regulation_id = Column(Integer, nullable=True)  # 法规ID（法规更新时使用）
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "version": self.version,
            "regulation_id": self.regulation_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<UpdateNotification(id={self.id}, type='{self.type}', title='{self.title}')>"
