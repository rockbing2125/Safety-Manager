"""
用户模型
"""
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
import bcrypt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from .database import Base
from shared.constants import UserRole


class User(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    regulations = relationship("Regulation", back_populates="creator", foreign_keys="Regulation.created_by")
    documents = relationship("RegulationDocument", back_populates="uploader")
    code_files = relationship("CodeFile", back_populates="creator")
    changes = relationship("ChangeHistory", back_populates="user")

    def set_password(self, password: str):
        """设置密码"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def has_permission(self, permission: str) -> bool:
        """检查权限"""
        from shared.constants import ROLE_PERMISSIONS
        return ROLE_PERMISSIONS.get(self.role, {}).get(permission, False)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"