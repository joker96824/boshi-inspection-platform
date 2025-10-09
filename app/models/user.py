"""
用户模型
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
# MySQL不支持UUID类型，使用CHAR(36)
from .base import BaseModel


class User(BaseModel):
    """用户模型"""
    __tablename__ = "tb_users"
    
    username = Column(String(50), nullable=False, index=True, comment='用户名')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    mobile = Column(String(20), nullable=True, comment='手机号')
    email = Column(String(100), nullable=True, comment='邮箱')
    role = Column(String(20), default='user', nullable=False, comment='角色: super_admin/admin/operator/viewer/user')
    last_login_at = Column(DateTime, nullable=True, comment='最后登录时间')
    
    # 关系
    sessions = relationship("Session", back_populates="user")
    maps = relationship("Map", back_populates="user")
    robots = relationship("Robot", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(username={self.username}, role={self.role})>"