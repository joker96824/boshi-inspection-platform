"""
巡检中间表模型
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Index, ForeignKey
from sqlalchemy.sql import func
from .base import BaseModel


class PointItem(BaseModel):
    """巡检中间表模型"""
    
    __tablename__ = "tb_point_item"
    
    # 巡检点ID
    point_id = Column(String(36), ForeignKey("tb_point.id", ondelete="CASCADE"), nullable=False, comment="巡检点ID")
    
    # 巡检项目ID
    item_id = Column(String(36), ForeignKey("tb_item.id", ondelete="CASCADE"), nullable=False, comment="巡检项目ID")
    
    # 创建索引
    __table_args__ = (
        Index('idx_point_id', 'point_id'),
        Index('idx_item_id', 'item_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
