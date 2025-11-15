"""
云台日程数据模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Boolean, Integer, Index, Date, Time
from sqlalchemy.orm import relationship
from .base import BaseModel


class GimbalSchedule(BaseModel):
    """云台日程模型（格式与 TaskSchedule 统一）"""
    
    __tablename__ = "tb_gimbalschedule"
    
    # 基础字段
    gimbaltask_id = Column(String(50), ForeignKey("tb_gimbaltask.id", ondelete="CASCADE"), nullable=False, comment="关联的云台任务ID")
    schedule_name = Column(String(200), nullable=False, comment="日程名称")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    
    # 执行周期配置
    cycle_type = Column(String(20), nullable=False, comment="周期类型：daily/monthly_days/weekly/interval")
    cycle_config = Column(JSON, nullable=True, comment="周期详细配置（JSON格式）")
    
    # 执行时间配置
    time_mode = Column(String(20), nullable=False, comment="时间模式：custom/interval")
    time_config = Column(JSON, nullable=False, comment="时间详细配置（JSON格式）")
    
    # 用于显示的简化字段（便于查询和展示）
    frequency_display = Column(String(200), nullable=True, comment="周期显示文本，例如：每天、每月1/5/10日")
    time_display_start = Column(Time, nullable=True, comment="开始时间（用于时间轴显示）")
    time_display_end = Column(Time, nullable=True, comment="结束时间（用于时间轴显示）")
    
    # 关系
    gimbal_task = relationship("GimbalTask", back_populates="schedules")
    
    # 创建索引
    __table_args__ = (
        Index('idx_gimbaltask_id', 'gimbaltask_id'),
        Index('idx_cycle_type', 'cycle_type'),
        Index('idx_enabled', 'enabled'),
        Index('idx_date_range', 'start_date', 'end_date'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self) -> str:
        return f"<GimbalSchedule(id='{self.id}', schedule_name='{self.schedule_name}', gimbaltask_id='{self.gimbaltask_id}', cycle_type='{self.cycle_type}')>"
