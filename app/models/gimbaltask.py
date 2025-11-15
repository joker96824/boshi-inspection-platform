"""
云台任务数据模型
"""

from sqlalchemy import Column, String, Index, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class GimbalTask(BaseModel):
    """云台任务模型（基础信息）"""

    __tablename__ = "tb_gimbaltask"

    task_name = Column(String(100), nullable=False, comment="云台任务名称")
    gimbal_id = Column(
        String(36),
        ForeignKey("tb_gimbal.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属云台ID",
    )

    gimbal = relationship("Gimbal", back_populates="gimbal_tasks")
    inspection_projects = relationship(
        "GimbalInspectionProject",
        back_populates="gimbal_task",
        cascade="all, delete-orphan",
        order_by="GimbalInspectionProject.sort_order",
    )
    schedules = relationship(
        "GimbalSchedule",
        back_populates="gimbal_task",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_task_name", "task_name"),
        Index("idx_gimbal_id", "gimbal_id"),
        Index("idx_created_at", "created_at"),
        Index("idx_is_deleted", "is_deleted"),
        Index("uk_task_name_active", "task_name", "is_deleted", unique=True),
    )

    def __repr__(self) -> str:
        return (
            f"<GimbalTask(id='{self.id}', task_name='{self.task_name}', "
            f"gimbal_id='{self.gimbal_id}')>"
        )
