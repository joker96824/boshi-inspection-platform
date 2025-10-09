"""
会话模型
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
# MySQL不支持UUID类型，使用CHAR(36)
from sqlalchemy.orm import relationship
from .base import BaseModel


class Session(BaseModel):
    """用户会话模型"""
    __tablename__ = "tb_sessions"
    
    user_id = Column(String(36), ForeignKey("tb_users.id"), nullable=False, index=True, comment='用户ID')
    token = Column(String(500), unique=True, nullable=False, index=True, comment='会话令牌')
    expires_at = Column(DateTime, nullable=False, comment='过期时间')
    
    # 关系
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<Session(user_id={self.user_id}, token={self.token[:20]}...)>"