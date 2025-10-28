"""
云台记录数据模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class GimbalHistory(BaseModel):
    """云台记录模型"""
    
    __tablename__ = "tb_gimbalhistory"
    
    # 基础字段
    gimbaltask_id = Column(String(36), ForeignKey("tb_gimbaltask.id", ondelete="CASCADE"), nullable=False, comment="关联云台任务ID")
    record_data = Column(JSON, nullable=True, comment="记录数据")
    media_url = Column(String(500), nullable=True, comment="图像/视频链接")
    
    # 关系
    gimbal_task = relationship("GimbalTask", back_populates="histories")
    
    # 创建索引
    __table_args__ = (
        Index('idx_gimbaltask_id', 'gimbaltask_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self) -> str:
        return f"<GimbalHistory(id='{self.id}', gimbaltask_id='{self.gimbaltask_id}')>"
