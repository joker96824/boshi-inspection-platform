"""
检测类型模型
"""

from sqlalchemy import Column, String, Integer, Boolean, Index
from .base import BaseModel


class DetectionType(BaseModel):
    """检测类型模型"""
    
    __tablename__ = "tb_detection_type"
    
    # 基础字段
    type_name = Column(String(50), nullable=False, unique=True, comment="检测类型名称")
    type_code = Column(String(20), nullable=False, unique=True, comment="检测类型代码")
    description = Column(String(200), nullable=True, comment="检测类型描述")
    sort_order = Column(Integer, nullable=False, default=0, comment="排序顺序")
    enabled = Column(Boolean, nullable=False, default=True, comment="启用状态：0-禁用，1-启用")
    
    # 创建索引
    __table_args__ = (
        Index('idx_type_name', 'type_name'),
        Index('idx_type_code', 'type_code'),
        Index('idx_sort_order', 'sort_order'),
        Index('idx_enabled', 'enabled'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self) -> str:
        return f"<DetectionType(id='{self.id}', type_name='{self.type_name}', type_code='{self.type_code}')>"

