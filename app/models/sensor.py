"""
智能传感器数据模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Index, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Sensor(BaseModel):
    """智能传感器模型"""
    
    __tablename__ = "tb_sensor"
    
    # 基础字段
    device_id = Column(String(36), ForeignKey("tb_device.id", ondelete="CASCADE"), nullable=False, comment="关联设备ID")
    sensor_name = Column(String(100), nullable=False, comment="传感器名称")
    sensor_params = Column(JSON, nullable=True, comment="传感器参数")
    group_id = Column(String(36), ForeignKey("tb_group.id", ondelete="SET NULL"), nullable=True, index=True, comment="分组ID")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    
    # 关系
    device = relationship("Device", back_populates="sensors")
    group = relationship("Group", foreign_keys=[group_id])
    histories = relationship("SensorHistory", back_populates="sensor", cascade="all, delete-orphan")
    
    # 创建索引
    __table_args__ = (
        Index('idx_device_id', 'device_id'),
        Index('idx_sensor_name', 'sensor_name'),
        Index('idx_group_id', 'group_id'),
        Index('idx_enabled', 'enabled'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Sensor(id='{self.id}', sensor_name='{self.sensor_name}', device_id='{self.device_id}')>"
