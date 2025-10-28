"""
电机状态配置数据模型
"""

from sqlalchemy import Column, String, Integer, JSON, Index
from .base import BaseModel


class MotorStatus(BaseModel):
    """电机状态配置模型"""
    
    __tablename__ = "cfg_motor_status"
    
    # 电机参数
    motor_id = Column(Integer, nullable=False, comment="电机ID(0-255)")
    baud_rate = Column(Integer, nullable=False, comment="波特率(9600-115200)")
    tpdo_config = Column(JSON, nullable=True, comment="TPDO配置参数")
    rpdo_config = Column(JSON, nullable=True, comment="RPDO配置参数")
    
    # 创建索引
    __table_args__ = (
        Index('idx_motor_id', 'motor_id'),
        Index('idx_baud_rate', 'baud_rate'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<MotorStatus(id='{self.id}', motor_id={self.motor_id}, baud_rate={self.baud_rate})>"

