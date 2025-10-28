"""
环境传感器数据模型
"""

from sqlalchemy import Column, String, Integer, Index
from .base import BaseModel


class EnvironmentSensor(BaseModel):
    """环境传感器模型"""
    
    __tablename__ = "cfg_environment_sensor"
    
    # 环境传感器参数
    station_number = Column(Integer, nullable=False, comment="站号(1-255)")
    baud_rate = Column(Integer, nullable=False, comment="波特率(9600-115200)")
    
    # 创建索引
    __table_args__ = (
        Index('idx_station_number', 'station_number'),
        Index('idx_baud_rate', 'baud_rate'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<EnvironmentSensor(id='{self.id}', station_number={self.station_number}, baud_rate={self.baud_rate})>"


