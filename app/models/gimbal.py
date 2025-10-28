"""
云台数据模型
"""

from sqlalchemy import Column, String, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Gimbal(BaseModel):
    """云台模型"""
    
    __tablename__ = "tb_gimbal"
    
    # 基础字段
    gimbal_name = Column(String(100), nullable=False, comment="云台名称")
    gimbal_params = Column(JSON, nullable=True, comment="云台参数")
    map_id = Column(String(36), ForeignKey("tb_map.id", ondelete="SET NULL"), nullable=True, index=True, comment="地图ID")
    
    # 关系
    map = relationship("Map", foreign_keys=[map_id])
    gimbal_tasks = relationship("GimbalTask", back_populates="gimbal", cascade="all, delete-orphan")
    
    # 创建索引
    __table_args__ = (
        Index('idx_gimbal_name', 'gimbal_name'),
        Index('idx_map_id', 'map_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Gimbal(id='{self.id}', gimbal_name='{self.gimbal_name}')>"
