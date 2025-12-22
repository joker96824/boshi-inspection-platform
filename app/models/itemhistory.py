"""
巡检记录模型
"""

from sqlalchemy import Column, String, Boolean, Index, UniqueConstraint, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..models.base import BaseModel


class ItemHistory(BaseModel):
    """巡检记录模型"""
    __tablename__ = "tb_itemhistory"

    taskhistory_id = Column(String(36), ForeignKey("tb_taskhistory.id", ondelete="CASCADE"), nullable=False, comment="任务记录ID")
    item_id = Column(String(36), ForeignKey("tb_item.id", ondelete="CASCADE"), nullable=False, comment="巡检项目ID")
    item_result = Column(JSON, nullable=True, comment="巡检结果")
    process_status = Column(String(20), nullable=True, comment="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status = Column(String(20), nullable=True, comment="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    # 关系
    item = relationship("Item", foreign_keys=[item_id])

    __table_args__ = (
        Index('idx_taskhistory_id', 'taskhistory_id'),
        Index('idx_item_id', 'item_id'),
        Index('idx_process_status', 'process_status'),
        Index('idx_inspection_result_status', 'inspection_result_status'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
        # 确保未删除的 taskhistory_id + item_id 组合是唯一的
        UniqueConstraint('taskhistory_id', 'item_id', 'is_deleted', name='uk_taskhistory_item_active')
    )
