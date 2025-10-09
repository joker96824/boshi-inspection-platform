"""
地图模型
"""

from sqlalchemy import Column, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Map(BaseModel):
    """地图模型"""
    __tablename__ = "tb_map"
    
    user_id = Column(String(36), ForeignKey("tb_users.id"), nullable=False, index=True, comment='所属用户ID')
    map_name = Column(String(100), nullable=False, index=True, comment='地图名称')
    map_image_url = Column(String(500), nullable=True, comment='图片地址')
    map_scale = Column(DECIMAL(10, 6), nullable=True, comment='比例尺')
    map_center_x = Column(DECIMAL(15, 6), nullable=True, comment='中心点横坐标')
    map_center_y = Column(DECIMAL(15, 6), nullable=True, comment='中心点纵坐标')
    
    # 关系
    user = relationship("User", back_populates="maps")
    mapnets = relationship("MapNet", back_populates="map")
    points = relationship("Point", back_populates="map")
    tasks = relationship("Task", back_populates="map")
    
    def __repr__(self) -> str:
        return f"<Map(map_name={self.map_name}, user_id={self.user_id})>"
