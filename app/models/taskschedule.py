"""
任务日程模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class TaskSchedule(BaseModel):
    """任务日程模型"""
    
    __tablename__ = "tb_taskschedule"
    
    # 基础字段
    schedule_type = Column(String(50), nullable=False, comment="任务日程类型")
    schedule_is_active = Column(Boolean, nullable=False, default=True, comment="任务日程是否激活")
    task_id = Column(String(36), ForeignKey("tb_task.id", ondelete="CASCADE"), nullable=False, comment="关联任务ID")
    schedule_param = Column(JSON, nullable=True, comment="日程参数")
    set_time = Column(Integer, nullable=False, comment="设置时间（Unix时间戳）")
    cnt = Column(Integer, nullable=False, default=1, comment="需要执行的次数")
    
    # 关系
    task = relationship("Task", back_populates="schedules")
    
    def __repr__(self) -> str:
        return f"<TaskSchedule(schedule_type={self.schedule_type}, task_id={self.task_id}, is_active={self.schedule_is_active})>"
