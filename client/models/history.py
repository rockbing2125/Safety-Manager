"""
历史变更记录模型
"""
import sys
from pathlib import Path
from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from .database import Base
from shared.constants import ChangeType, EntityType


class ChangeHistory(Base):
    """历史变更记录表"""

    __tablename__ = "change_history"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    change_type = Column(Enum(ChangeType), nullable=False)
    change_data = Column(Text, nullable=True)
    change_summary = Column(String(500), nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="changes")

    def set_change_data(self, data: dict):
        """设置变更数据"""
        self.change_data = json.dumps(data, ensure_ascii=False)

    def get_change_data(self) -> dict:
        """获取变更数据"""
        if self.change_data:
            return json.loads(self.change_data)
        return {}

    @staticmethod
    def create_change_record(db, entity_type, entity_id, change_type, 
                           change_data, change_summary, changed_by):
        """创建变更记录"""
        history = ChangeHistory(
            entity_type=entity_type,
            entity_id=entity_id,
            change_type=change_type,
            change_summary=change_summary,
            changed_by=changed_by
        )
        history.set_change_data(change_data)
        db.add(history)
        db.commit()
        return history