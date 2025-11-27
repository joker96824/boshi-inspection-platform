"""
巡检项目模型
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel


class Item(BaseModel):
    """巡检项目模型"""
    
    __tablename__ = "tb_item"
    
    # 基础字段
    item_name = Column(String(100), nullable=False, comment="巡检项目名称")
    item_info = Column(JSON, nullable=False, comment="巡检参数信息")
    device_id = Column(String(36), ForeignKey("tb_device.id", ondelete="CASCADE"), nullable=False, comment="所属设备ID")
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="SET NULL"), nullable=True, comment="关联机器人ID")
    detection_type_id = Column(String(36), ForeignKey("tb_detection_type.id", ondelete="SET NULL"), nullable=True, comment="检测类型ID")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    
    # 关系
    device = relationship("Device", back_populates="items")
    robot = relationship("Robot", foreign_keys=[robot_id])
    detection_type = relationship("DetectionType", foreign_keys=[detection_type_id])
    
    # 创建索引
    __table_args__ = (
        Index('idx_item_name', 'item_name'),
        Index('idx_device_id', 'device_id'),
        Index('idx_robot_id', 'robot_id'),
        Index('idx_detection_type_id', 'detection_type_id'),
        Index('idx_enabled', 'enabled'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
