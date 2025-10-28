"""
传感器记录数据模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class SensorHistory(BaseModel):
    """传感器记录模型"""
    
    __tablename__ = "tb_sensorhistory"
    
    # 基础字段
    sensor_id = Column(String(36), ForeignKey("tb_sensor.id", ondelete="CASCADE"), nullable=False, comment="关联传感器ID")
    record_data = Column(JSON, nullable=True, comment="记录数据")
    file_url = Column(String(500), nullable=True, comment="相关文件链接")
    
    # 关系
    sensor = relationship("Sensor", back_populates="histories")
    
    # 创建索引
    __table_args__ = (
        Index('idx_sensor_id', 'sensor_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self) -> str:
        return f"<SensorHistory(id='{self.id}', sensor_id='{self.sensor_id}')>"
