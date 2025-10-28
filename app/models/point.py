"""
巡检点数据模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Point(BaseModel):
    """巡检点模型"""
    
    __tablename__ = "tb_point"
    
    # 基础字段
    point_name = Column(String(100), nullable=False, comment="巡检点名称")
    map_id = Column(String(36), ForeignKey("tb_map.id", ondelete="CASCADE"), nullable=False, comment="所属地图ID")
    point_actions = Column(JSON, nullable=True, comment="巡检点动作")
    
    # 关系
    map = relationship("Map", back_populates="points")
    items = relationship("Item", back_populates="point", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Point(id='{self.id}', point_name='{self.point_name}', map_id='{self.map_id}')>"
