"""
地图路网模型
"""

from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class MapNet(BaseModel):
    """地图路网模型"""
    __tablename__ = "tb_mapnet"
    
    map_id = Column(String(36), ForeignKey("tb_map.id"), nullable=False, index=True, comment='所属地图ID')
    map_net_type = Column(String(50), nullable=False, index=True, comment='元素类型')
    map_net_properties = Column(JSON, nullable=True, comment='路网元素属性')
    map_net_geometry = Column(JSON, nullable=True, comment='路网元素地理信息')
    
    # 关系
    map = relationship("Map", back_populates="mapnets")
    
    def __repr__(self) -> str:
        return f"<MapNet(type={self.map_net_type}, map_id={self.map_id})>"
