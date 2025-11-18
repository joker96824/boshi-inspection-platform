"""
任务记录模型
"""

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship

from .base import BaseModel


class TaskHistory(BaseModel):
    """任务记录模型"""
    
    __tablename__ = "tb_taskhistory"
    
    # 基础字段
    task_id = Column(String(36), ForeignKey("tb_task.id", ondelete="CASCADE"), nullable=False, comment="关联任务ID")
    record_start_time = Column(DateTime, nullable=False, comment="任务开始时间")
    record_end_time = Column(DateTime, nullable=True, comment="任务结束时间")
    record_status = Column(String(20), nullable=False, comment="任务状态：running-执行中, paused-已暂停, completed-已完成, failed-执行失败, cancelled-已取消")
    record_batch = Column(Integer, nullable=False, comment="任务批次号")
    
    # 执行进度字段
    current_point_id = Column(String(36), ForeignKey("tb_point.id", ondelete="SET NULL"), nullable=True, comment="当前执行的巡检点ID")
    current_item_id = Column(String(36), ForeignKey("tb_item.id", ondelete="SET NULL"), nullable=True, comment="当前执行的巡检项目ID")
    
    # 关系
    task = relationship("Task", back_populates="taskhistories")
    current_point = relationship("Point", foreign_keys=[current_point_id])
    current_item = relationship("Item", foreign_keys=[current_item_id])
    
    def __repr__(self) -> str:
        return f"<TaskHistory(task_id={self.task_id}, record_status={self.record_status}, record_batch={self.record_batch})>"