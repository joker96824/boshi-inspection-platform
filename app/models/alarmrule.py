"""
报警规则模型
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, JSON, Enum, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from ..models.base import BaseModel


class AlarmRule(BaseModel):
    """报警规则模型"""
    __tablename__ = "tb_alarm_rule"

    rule_name = Column(String(100), nullable=False, comment="规则名称")
    alarm_category = Column(Enum('robot', 'inspection', 'gimbal', 'sensor', 'other', name='alarm_category'),
                          nullable=False, comment="报警分类")
    alarm_level = Column(Integer, nullable=False, comment="报警等级 1-10")
    rule_type = Column(Enum('value_range', 'bool_value', 'sum_value', 'diff_value', 'avg_range', 'complex', name='rule_type'),
                      nullable=False, comment="规则类型")
    rule_config = Column(JSON, nullable=True, comment="规则配置（JSON格式）")
    enabled = Column(Boolean, nullable=False, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="规则描述")
    is_global = Column(Boolean, nullable=False, default=False, comment="是否全局规则")

    # 关系
    relations = relationship("AlarmRuleRelation", back_populates="alarm_rule", cascade="all, delete-orphan")
    alarm_infos = relationship("AlarmInfo", back_populates="alarm_rule")

    __table_args__ = (
        Index('idx_rule_name', 'rule_name'),
        Index('idx_alarm_category', 'alarm_category'),
        Index('idx_alarm_level', 'alarm_level'),
        Index('idx_rule_type', 'rule_type'),
        Index('idx_enabled', 'enabled'),
        Index('idx_is_global', 'is_global'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
        UniqueConstraint('rule_name', 'is_deleted', name='uk_rule_name_active')
    )
