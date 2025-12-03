"""
云台数据模型
"""

from sqlalchemy import Column, String, Index, ForeignKey, Float, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Gimbal(BaseModel):
    """云台模型"""
    
    __tablename__ = "tb_gimbal"
    
    # 基础字段
    gimbal_name = Column(String(100), nullable=False, comment="云台名称")
    map_id = Column(String(36), ForeignKey("tb_map.id", ondelete="SET NULL"), nullable=True, index=True, comment="地图ID")
    group_id = Column(String(36), ForeignKey("tb_group.id", ondelete="SET NULL"), nullable=True, index=True, comment="分组ID")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    ip_address = Column(String(45), nullable=False, comment="云台IP地址")
    port = Column(Integer, nullable=False, comment="云台端口")
    username = Column(String(100), nullable=False, comment="登录用户名")
    password = Column(String(255), nullable=False, comment="登录密码")
    rtsp_main_url = Column(String(255), nullable=False, comment="RTSP主码流地址")
    rtsp_sub_url = Column(String(255), nullable=True, comment="RTSP子码流地址")
    channel = Column(Integer, nullable=False, default=1, comment="通道号：1或2")
    x_coordinate = Column(Float, nullable=True, comment="X坐标（地图横坐标）")
    y_coordinate = Column(Float, nullable=True, comment="Y坐标（地图纵坐标）")
    p_coordinate = Column(Float, nullable=True, comment="P坐标")
    t_coordinate = Column(Float, nullable=True, comment="T坐标")
    z_coordinate = Column(Float, nullable=True, comment="Z坐标")
    f_coordinate = Column(Float, nullable=True, comment="F坐标")
    preview_url = Column(String(500), nullable=True, comment="预览地址")
    control_url = Column(String(500), nullable=True, comment="控制地址")
    
    # 关系
    map = relationship("Map", foreign_keys=[map_id])
    group = relationship("Group", foreign_keys=[group_id])
    gimbal_tasks = relationship("GimbalTask", back_populates="gimbal", cascade="all, delete-orphan")
    preset_points = relationship("GimbalPresetPoint", back_populates="gimbal", cascade="all, delete-orphan")
    
    # 创建索引
    __table_args__ = (
        Index('idx_gimbal_name', 'gimbal_name'),
        Index('idx_map_id', 'map_id'),
        Index('idx_group_id', 'group_id'),
        Index('idx_enabled', 'enabled'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
        Index('idx_gimbal_coordinates', 'map_id', 'x_coordinate', 'y_coordinate'),
        Index('idx_gimbal_channel', 'channel'),
    )
    
    def __repr__(self):
        return (
            f"<Gimbal(id='{self.id}', gimbal_name='{self.gimbal_name}', ip='{self.ip_address}', "
            f"channel={self.channel}, x={self.x_coordinate}, y={self.y_coordinate})>"
        )
