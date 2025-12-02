"""
法规参数模型
"""
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, LargeBinary, DateTime
from sqlalchemy.orm import relationship

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from .database import Base


class RegulationParameter(Base):
    """法规参数表"""
    
    __tablename__ = "regulation_parameters"
    
    id = Column(Integer, primary_key=True)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    category = Column(String(100))
    parameter_name = Column(String(200), nullable=False)
    default_value = Column(String(100))
    upper_limit = Column(String(100))
    lower_limit = Column(String(100))
    unit = Column(String(50))
    remark = Column(Text)
    remark_image = Column(LargeBinary)
    row_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    regulation = relationship("Regulation", backref="parameters")