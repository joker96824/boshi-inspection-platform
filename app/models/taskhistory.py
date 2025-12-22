"""
任务记录模型
"""

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Index
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
    
    # 查看状态字段
    view_status = Column(String(20), nullable=True, comment="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    
    # 巡检结果状态字段
    inspection_result_status = Column(String(20), nullable=True, comment="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    # 关系
    task = relationship("Task", back_populates="taskhistories")
    current_point = relationship("Point", foreign_keys=[current_point_id])
    current_item = relationship("Item", foreign_keys=[current_item_id])
    
    __table_args__ = (
        Index('idx_task_id', 'task_id'),
        Index('idx_record_status', 'record_status'),
        Index('idx_record_batch', 'record_batch'),
        Index('idx_view_status', 'view_status'),
        Index('idx_inspection_result_status', 'inspection_result_status'),
    )
    
    def __repr__(self) -> str:
        return f"<TaskHistory(task_id={self.task_id}, record_status={self.record_status}, record_batch={self.record_batch})>"