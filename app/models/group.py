"""
分组数据模型
"""

from sqlalchemy import Column, String, Index
from .base import BaseModel


class Group(BaseModel):
    """分组模型"""
    
    __tablename__ = "tb_group"
    
    # 基础字段
    group_name = Column(String(100), nullable=False, comment="分组名称")
    group_description = Column(String(500), nullable=True, comment="分组描述")
    
    # 创建索引
    __table_args__ = (
        Index('idx_group_name', 'group_name'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Group(id='{self.id}', group_name='{self.group_name}')>"

