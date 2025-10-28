"""
报警规则模型
"""

from sqlalchemy import Column, String, ForeignKey, Index, UniqueConstraint, JSON, Enum
from ..models.base import BaseModel


class AlarmRule(BaseModel):
    """报警规则模型"""
    __tablename__ = "tb_alarmrule"

    rule_name = Column(String(100), nullable=False, comment="规则名称")
    business_type = Column(Enum('inspection_item', 'gimbal_history', 'sensor_history', name='business_type'), 
                          nullable=False, default='inspection_item', comment="业务类型")
    business_id = Column(String(36), nullable=False, comment="业务对象ID")
    alarm_param = Column(JSON, nullable=True, comment="报警参数")

    __table_args__ = (
        Index('idx_rule_name', 'rule_name'),
        Index('idx_business_type', 'business_type'),
        Index('idx_business_id', 'business_id'),
        Index('idx_business_type_id', 'business_type', 'business_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
        UniqueConstraint('rule_name', 'is_deleted', name='uk_rule_name_active')
    )

