"""
巡检记录模型
"""

from sqlalchemy import Column, String, Boolean, Index, UniqueConstraint, ForeignKey, JSON
from ..models.base import BaseModel


class ItemHistory(BaseModel):
    """巡检记录模型"""
    __tablename__ = "tb_itemhistory"

    taskhistory_id = Column(String(36), ForeignKey("tb_taskhistory.id", ondelete="CASCADE"), nullable=False, comment="任务记录ID")
    item_id = Column(String(36), ForeignKey("tb_item.id", ondelete="CASCADE"), nullable=False, comment="巡检项目ID")
    item_result = Column(JSON, nullable=True, comment="巡检结果")

    __table_args__ = (
        Index('idx_taskhistory_id', 'taskhistory_id'),
        Index('idx_item_id', 'item_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
        # 确保未删除的 taskhistory_id + item_id 组合是唯一的
        UniqueConstraint('taskhistory_id', 'item_id', 'is_deleted', name='uk_taskhistory_item_active')
    )
