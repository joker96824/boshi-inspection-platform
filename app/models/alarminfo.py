"""
报警信息模型
"""

from sqlalchemy import Column, String, ForeignKey, Index, JSON, Text
from ..models.base import BaseModel


class AlarmInfo(BaseModel):
    """报警信息模型"""
    __tablename__ = "tb_alarminfo"

    alarmrule_id = Column(String(36), ForeignKey("tb_alarmrule.id", ondelete="CASCADE"), nullable=False, comment="报警规则ID")
    itemhistory_id = Column(String(36), ForeignKey("tb_itemhistory.id", ondelete="CASCADE"), nullable=False, comment="巡检记录ID")
    alarm_data = Column(JSON, nullable=True, comment="触发数据")
    alarm_info = Column(Text, nullable=True, comment="报警信息")

    __table_args__ = (
        Index('idx_alarmrule_id', 'alarmrule_id'),
        Index('idx_itemhistory_id', 'itemhistory_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )

