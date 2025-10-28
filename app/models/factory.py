"""
厂区模型
"""

from sqlalchemy import Column, String, Index
from .base import BaseModel


class Factory(BaseModel):
    """厂区模型"""
    
    __tablename__ = "tb_factory"
    
    # 厂区基本信息
    factory_name = Column(String(100), nullable=False, comment="厂区名称")
    
    # 创建索引
    __table_args__ = (
        Index('idx_factory_name', 'factory_name'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Factory(id='{self.id}', factory_name='{self.factory_name}')>"

