"""
报警规则关联模型
"""

from sqlalchemy import Column, String, Integer, Enum, Index, UniqueConstraint, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..models.base import Base


class AlarmRuleRelation(Base):
    """报警规则关联模型（不使用软删除）"""
    __tablename__ = "tb_alarm_rule_relation"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    alarm_rule_id = Column(String(36), ForeignKey("tb_alarm_rule.id", ondelete="CASCADE"), nullable=False, comment="报警规则ID")
    relation_type = Column(Enum('item', 'gimbal', 'sensor', name='relation_type'),
                          nullable=False, comment="关联类型")
    relation_id = Column(String(36), nullable=False, comment="关联对象ID")
    sort_order = Column(Integer, nullable=False, default=0, comment="顺序，用于多数据源规则")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    created_by = Column(String(100), nullable=True, comment="创建人")
    updated_by = Column(String(100), nullable=True, comment="更新人")

    # 关系
    alarm_rule = relationship("AlarmRule", back_populates="relations")

    __table_args__ = (
        Index('idx_alarm_rule_id', 'alarm_rule_id'),
        Index('idx_relation_type_id', 'relation_type', 'relation_id'),
        Index('idx_sort_order', 'alarm_rule_id', 'sort_order'),
        UniqueConstraint('alarm_rule_id', 'relation_type', 'relation_id', name='uk_rule_relation')
    )

