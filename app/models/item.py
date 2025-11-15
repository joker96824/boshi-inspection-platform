"""
巡检项目模型
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel


class Item(BaseModel):
    """巡检项目模型"""
    
    __tablename__ = "tb_item"
    
    # 基础字段
    item_name = Column(String(100), nullable=False, comment="巡检项目名称")
    item_info = Column(JSON, nullable=False, comment="巡检参数信息")
    device_id = Column(String(36), ForeignKey("tb_device.id", ondelete="CASCADE"), nullable=False, comment="所属设备ID")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    
    # 关系
    device = relationship("Device", back_populates="items")
    
    # 创建索引
    __table_args__ = (
        Index('idx_item_name', 'item_name'),
        Index('idx_device_id', 'device_id'),
        Index('idx_enabled', 'enabled'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
