"""
法规相关模型
"""
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from .database import Base
from shared.constants import RegulationStatus, DocumentType


class Regulation(Base):
    """法规表"""

    __tablename__ = "regulations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    country = Column(String(50), nullable=True, index=True)
    category = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(RegulationStatus), nullable=False, default=RegulationStatus.DRAFT)
    version = Column(String(20), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    creator = relationship("User", back_populates="regulations", foreign_keys=[created_by])
    documents = relationship("RegulationDocument", back_populates="regulation", cascade="all, delete-orphan")
    code_files = relationship("CodeFile", back_populates="regulation", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="regulation_tags", back_populates="regulations")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "country": self.country,
            "category": self.category,
            "description": self.description,
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tags": [tag.name for tag in self.tags],
        }


class RegulationDocument(Base):
    """法规文档表"""

    __tablename__ = "regulation_documents"

    id = Column(Integer, primary_key=True, index=True)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    doc_type = Column(Enum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    upload_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    upload_at = Column(DateTime, default=datetime.utcnow)

    regulation = relationship("Regulation", back_populates="documents")
    uploader = relationship("User", back_populates="documents")


class CodeFile(Base):
    """C代码文件表"""

    __tablename__ = "code_files"

    id = Column(Integer, primary_key=True, index=True)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    usage_guide = Column(Text, nullable=True)
    version = Column(String(20), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    regulation = relationship("Regulation", back_populates="code_files")
    creator = relationship("User", back_populates="code_files")


class Tag(Base):
    """标签表"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    regulations = relationship("Regulation", secondary="regulation_tags", back_populates="tags")


class RegulationTag(Base):
    """法规标签关联表"""

    __tablename__ = "regulation_tags"

    regulation_id = Column(Integer, ForeignKey("regulations.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)