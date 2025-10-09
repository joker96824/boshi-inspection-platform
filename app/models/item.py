"""
巡检项目模型
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Index
from sqlalchemy.sql import func
from .base import BaseModel


class Item(BaseModel):
    """巡检项目模型"""
    
    __tablename__ = "tb_item"
    
    # 巡检项目名称
    item_name = Column(String(100), nullable=False, comment="巡检项目名称")
    
    # 巡检参数信息（JSON格式）
    item_info = Column(JSON, nullable=False, comment="巡检参数信息")
    
    # 创建索引
    __table_args__ = (
        Index('idx_item_name', 'item_name'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
