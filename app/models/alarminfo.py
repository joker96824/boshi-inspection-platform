"""
报警信息模型
"""

from sqlalchemy import Column, String, Integer, Enum, JSON, Text, Index, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from ..models.base import BaseModel


class AlarmInfo(BaseModel):
    """报警信息模型"""
    __tablename__ = "tb_alarm_info"

    alarm_rule_id = Column(String(36), ForeignKey("tb_alarm_rule.id", ondelete="CASCADE"), nullable=False, comment="报警规则ID")
    alarm_category = Column(Enum('robot', 'inspection', 'gimbal', 'sensor', 'other', name='alarm_category'),
                          nullable=False, comment="报警分类")
    alarm_level = Column(Integer, nullable=False, comment="报警等级 1-10")
    alarm_status = Column(Enum('unviewed', 'unprocessed', 'processed', name='alarm_status'),
                         nullable=False, default='unviewed', comment="报警状态")
    source_type = Column(Enum('itemhistory', 'gimbalhistory', 'sensorhistory', 'robot_status', name='source_type'),
                        nullable=False, comment="数据源类型")
    source_ids = Column(JSON, nullable=False, comment="数据源ID列表，按关联表顺序排列")
    relation_type = Column(Enum('item', 'gimbal', 'sensor', 'robot', 'none', name='relation_type'),
                          nullable=True, comment="关联对象类型")
    relation_ids = Column(JSON, nullable=True, comment="关联对象ID列表")
    trigger_item_ids = Column(JSON, nullable=True, comment="触发源对应的巡检项目ID列表")
    trigger_project_ids = Column(JSON, nullable=True, comment="触发源对应的云台巡检项目ID列表")
    trigger_data = Column(JSON, nullable=True, comment="触发时的完整数据快照")
    calculated_value = Column(JSON, nullable=True, comment="计算后的值（如平均值、和值等）")
    alarm_message = Column(Text, nullable=True, comment="报警信息")
    processed_by = Column(String(100), nullable=True, comment="处理人")
    processed_at = Column(String(19), nullable=True, comment="处理时间")
    process_remark = Column(Text, nullable=True, comment="处理备注")

    # 关系
    alarm_rule = relationship("AlarmRule", back_populates="alarm_infos")

    __table_args__ = (
        Index('idx_alarm_rule_id', 'alarm_rule_id'),
        Index('idx_alarm_category', 'alarm_category'),
        Index('idx_alarm_level', 'alarm_level'),
        Index('idx_alarm_status', 'alarm_status'),
        Index('idx_source_type', 'source_type'),
        Index('idx_relation_type', 'relation_type'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
        # 去重索引：同一个报警规则id，同一组source_ids只能有一个报警信息
        # 注意：MySQL的JSON字段不能直接用于唯一索引，需要使用生成列或函数索引
        # 这里使用JSON_UNQUOTE(JSON_EXTRACT(source_ids, '$'))来创建唯一约束
        # 但MySQL 5.7+支持虚拟列，我们可以创建一个虚拟列
    )
