"""
机器人-地图关联模型（多对多中间表）
"""

from sqlalchemy import Column, String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class RobotMap(BaseModel):
    """机器人-地图关联模型（多对多中间表）"""
    
    __tablename__ = "tb_robot_map"
    
    # 基础字段
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="CASCADE"), nullable=False, comment="机器人ID")
    map_id = Column(String(36), ForeignKey("tb_map.id", ondelete="CASCADE"), nullable=False, comment="地图ID")
    
    # 关系
    robot = relationship("Robot", back_populates="maps")
    map = relationship("Map", back_populates="robots")
    
    # 创建索引和唯一约束
    __table_args__ = (
        Index('idx_robot_id', 'robot_id'),
        Index('idx_map_id', 'map_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
        # 确保未删除的 robot_id + map_id 组合是唯一的
        UniqueConstraint('robot_id', 'map_id', 'is_deleted', name='uk_robot_map_active')
    )
    
    def __repr__(self):
        return f"<RobotMap(robot_id='{self.robot_id}', map_id='{self.map_id}')>"

