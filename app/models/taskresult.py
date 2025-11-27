"""
任务结果模型
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Index, DateTime
from ..models.base import BaseModel


class TaskResult(BaseModel):
    """任务结果模型"""
    __tablename__ = "tb_taskresult"

    taskhistory_id = Column(String(36), ForeignKey("tb_taskhistory.id", ondelete="CASCADE"), nullable=False, unique=True, comment="任务记录ID")
    record_batch = Column(Integer, nullable=False, comment="任务批次")
    result_status = Column(String(20), nullable=True, comment="结果状态：success-成功, failed-失败, partial-部分成功, warning-警告")
    process_status = Column(String(20), nullable=True, comment="处理状态：pending-待处理, processing-处理中, processed-已处理, failed-处理失败")
    result_point_id = Column(String(36), nullable=True, comment="任务结束点ID")
    result_item_id = Column(String(36), nullable=True, comment="任务结束巡检项目ID")
    result_file_url = Column(String(500), nullable=True, comment="任务结果文件地址")
    result_collect_time = Column(DateTime, nullable=True, comment="结果采集时间")

    __table_args__ = (
        Index('idx_taskhistory_id', 'taskhistory_id'),
        Index('idx_record_batch', 'record_batch'),
        Index('idx_result_status', 'result_status'),
        Index('idx_process_status', 'process_status'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
