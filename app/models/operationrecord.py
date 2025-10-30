"""
操作记录数据模型
"""

from sqlalchemy import Column, String, DateTime, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class OperationRecord(BaseModel):
    """操作记录模型"""

    __tablename__ = "tb_operation_record"

    # 基础字段
    user_id = Column(String(36), nullable=False, index=True, comment="用户ID")
    username = Column(String(50), nullable=False, index=True, comment="用户名")
    operation_time = Column(DateTime, nullable=False, index=True, comment="操作时间")
    operation_content = Column(JSON, nullable=False, comment="操作内容JSON")

    # 创建索引
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_username', 'username'),
        Index('idx_operation_time', 'operation_time'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )

    def __repr__(self):
        return f"<OperationRecord(id='{self.id}', username='{self.username}', operation_time='{self.operation_time}')>"
