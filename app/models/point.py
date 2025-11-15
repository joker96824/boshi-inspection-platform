"""
巡检点数据模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Float, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Point(BaseModel):
    """巡检点模型"""
    
    __tablename__ = "tb_point"
    
    # 基础字段
    point_name = Column(String(100), nullable=False, comment="巡检点名称")
    map_id = Column(String(36), ForeignKey("tb_map.id", ondelete="CASCADE"), nullable=False, comment="所属地图ID")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    x_coordinate = Column(Float, nullable=True, comment="X坐标（地图横坐标）")
    y_coordinate = Column(Float, nullable=True, comment="Y坐标（地图纵坐标）")
    
    # 关系
    map = relationship("Map", back_populates="points")
    devices = relationship("Device", back_populates="point", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_point_name', 'point_name'),
        Index('idx_map_id', 'map_id'),
        Index('idx_enabled', 'enabled'),
        Index('idx_is_deleted', 'is_deleted'),
        Index('idx_point_coordinates', 'map_id', 'x_coordinate', 'y_coordinate'),
    )
    
    def __repr__(self):
        return (
            f"<Point(id='{self.id}', point_name='{self.point_name}', map_id='{self.map_id}', "
            f"x={self.x_coordinate}, y={self.y_coordinate})>"
        )
