"""
设备数据模型
"""

from sqlalchemy import Column, String, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Device(BaseModel):
    """设备模型"""
    
    __tablename__ = "tb_device"
    
    # 基础字段
    device_name = Column(String(100), nullable=False, comment="设备名称")
    device_params = Column(JSON, nullable=True, comment="设备参数")
    map_id = Column(String(36), ForeignKey("tb_map.id", ondelete="SET NULL"), nullable=True, index=True, comment="地图ID")
    
    # 关系
    map = relationship("Map", foreign_keys=[map_id])
    sensors = relationship("Sensor", back_populates="device", cascade="all, delete-orphan")
    
    # 创建索引
    __table_args__ = (
        Index('idx_device_name', 'device_name'),
        Index('idx_map_id', 'map_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Device(id='{self.id}', device_name='{self.device_name}')>"
