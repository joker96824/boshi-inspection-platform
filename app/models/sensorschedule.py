"""
传感器日程数据模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Boolean, Integer, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class SensorSchedule(BaseModel):
    """传感器日程模型"""
    
    __tablename__ = "tb_sensorschedule"
    
    # 基础字段
    schedule_type = Column(String(50), nullable=False, comment="传感器日程类型")
    schedule_is_active = Column(Boolean, nullable=False, default=True, comment="传感器日程是否激活")
    sensor_id = Column(String(36), ForeignKey("tb_sensor.id", ondelete="CASCADE"), nullable=False, comment="关联传感器ID")
    schedule_param = Column(JSON, nullable=True, comment="日程参数")
    set_time = Column(Integer, nullable=False, comment="设置时间（Unix时间戳）")
    
    # 关系
    sensor = relationship("Sensor", back_populates="schedules")
    
    # 创建索引
    __table_args__ = (
        Index('idx_schedule_type', 'schedule_type'),
        Index('idx_schedule_is_active', 'schedule_is_active'),
        Index('idx_sensor_id', 'sensor_id'),
        Index('idx_set_time', 'set_time'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self) -> str:
        return f"<SensorSchedule(schedule_type={self.schedule_type}, sensor_id={self.sensor_id}, is_active={self.schedule_is_active})>"
