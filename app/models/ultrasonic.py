"""
超声波状态配置数据模型
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Ultrasonic(BaseModel):
    """超声波状态配置模型"""
    
    __tablename__ = "cfg_ultrasonic"
    
    # 关联机器人
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联机器人ID")
    
    # 超声波参数
    ultrasonic_id = Column(Integer, nullable=False, comment="超声波ID(0-255)")
    obstacle_avoidance_distance = Column(DECIMAL(8, 2), nullable=False, default=800.00, comment="超声波避障距离(mm)")
    deceleration_distance = Column(DECIMAL(8, 2), nullable=False, default=1500.00, comment="超声波减速距离(mm)")
    baud_rate = Column(Integer, nullable=False, default=9600, comment="超声波波特率(9600-115200)")
    
    # 关系
    robot = relationship("Robot", foreign_keys=[robot_id])
    
    # 创建索引
    __table_args__ = (
        Index('idx_robot_id', 'robot_id'),
        Index('idx_ultrasonic_id', 'ultrasonic_id'),
        Index('idx_baud_rate', 'baud_rate'),
        Index('idx_obstacle_distance', 'obstacle_avoidance_distance'),
        Index('idx_deceleration_distance', 'deceleration_distance'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Ultrasonic(id='{self.id}', ultrasonic_id={self.ultrasonic_id}, baud_rate={self.baud_rate}, robot_id='{self.robot_id}')>"
