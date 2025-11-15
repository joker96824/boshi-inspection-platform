"""
设备数据模型
"""

from sqlalchemy import Column, String, JSON, Index, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Device(BaseModel):
    """设备模型"""
    
    __tablename__ = "tb_device"
    
    # 基础字段
    device_name = Column(String(100), nullable=False, comment="设备名称")
    device_params = Column(JSON, nullable=True, comment="设备参数")
    point_id = Column(String(36), ForeignKey("tb_point.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属巡检点ID")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    x_coordinate = Column(Float, nullable=True, comment="X坐标（地图横坐标）")
    y_coordinate = Column(Float, nullable=True, comment="Y坐标（地图纵坐标）")
    
    # 关系
    point = relationship("Point", back_populates="devices")
    sensors = relationship("Sensor", back_populates="device", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="device", cascade="all, delete-orphan")
    
    # 创建索引
    __table_args__ = (
        Index('idx_device_name', 'device_name'),
        Index('idx_point_id', 'point_id'),
        Index('idx_enabled', 'enabled'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return (
            f"<Device(id='{self.id}', device_name='{self.device_name}', "
            f"x={self.x_coordinate}, y={self.y_coordinate})>"
        )
