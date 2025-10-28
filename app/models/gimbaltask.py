"""
云台任务数据模型
"""

from sqlalchemy import Column, String, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class GimbalTask(BaseModel):
    """云台任务模型"""
    
    __tablename__ = "tb_gimbaltask"
    
    # 基础字段
    task_name = Column(String(100), nullable=False, comment="云台任务名称")
    angle_params = Column(JSON, nullable=True, comment="角度参数")
    task_type = Column(String(20), nullable=False, comment="任务类别：image/video")
    gimbal_id = Column(String(36), ForeignKey("tb_gimbal.id", ondelete="CASCADE"), nullable=False, comment="所属云台ID")
    
    # 关系
    gimbal = relationship("Gimbal", back_populates="gimbal_tasks")
    schedules = relationship("GimbalSchedule", back_populates="gimbal_task", cascade="all, delete-orphan")
    histories = relationship("GimbalHistory", back_populates="gimbal_task", cascade="all, delete-orphan")
    
    # 创建索引
    __table_args__ = (
        Index('idx_task_name', 'task_name'),
        Index('idx_task_type', 'task_type'),
        Index('idx_gimbal_id', 'gimbal_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<GimbalTask(id='{self.id}', task_name='{self.task_name}', task_type='{self.task_type}')>"
