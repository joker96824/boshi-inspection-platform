"""
机器人数据模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Robot(BaseModel):
    """机器人模型"""
    
    __tablename__ = "tb_robot"
    
    # 基础字段
    robot_name = Column(String(100), nullable=False, comment="机器人名称")
    robot_info = Column(JSON, nullable=True, comment="机器人信息")
    map_id = Column(String(36), ForeignKey("tb_map.id", ondelete="SET NULL"), nullable=False, index=True, comment="地图ID")
    
    # 关系
    map = relationship("Map", foreign_keys=[map_id])
    tasks = relationship("Task", back_populates="robot")
    
    def __repr__(self):
        return f"<Robot(id='{self.id}', robot_name='{self.robot_name}')>"
