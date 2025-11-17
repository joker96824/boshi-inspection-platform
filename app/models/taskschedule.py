"""
任务日程模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Boolean, DateTime, Integer, Date, Time
from sqlalchemy.orm import relationship

from .base import BaseModel


class TaskSchedule(BaseModel):
    """任务日程模型"""
    
    __tablename__ = "tb_taskschedule"
    
    # 基础字段
    task_id = Column(String(50), ForeignKey("tb_task.id", ondelete="CASCADE"), nullable=False, comment="关联的任务ID")
    schedule_name = Column(String(200), nullable=False, comment="日程名称")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    item_count = Column(Integer, nullable=False, default=0, comment="关联的巡检项目数量")
    
    # 执行周期配置
    cycle_type = Column(String(20), nullable=False, comment="周期类型：daily/monthly_days/weekly")
    cycle_config = Column(JSON, nullable=True, comment="周期详细配置（JSON格式）")
    
    # 执行时间配置
    time_mode = Column(String(20), nullable=False, comment="时间模式：custom/interval")
    time_config = Column(JSON, nullable=False, comment="时间详细配置（JSON格式）")
    
    # 用于显示的简化字段（便于查询和展示）
    time_display_start = Column(Time, nullable=True, comment="开始时间（用于时间轴显示）")
    time_display_end = Column(Time, nullable=True, comment="结束时间（用于时间轴显示）")
    
    # 关系
    task = relationship("Task", back_populates="schedules")
    
    def __repr__(self) -> str:
        return f"<TaskSchedule(id='{self.id}', schedule_name='{self.schedule_name}', task_id='{self.task_id}', cycle_type='{self.cycle_type}')>"
