"""
云台巡检项目数据模型
"""

from sqlalchemy import Column, String, Index, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class GimbalInspectionProject(BaseModel):
    """云台巡检项目模型"""

    __tablename__ = "tb_gimbal_inspection_project"

    task_name = Column(String(100), nullable=False, comment="巡检项目名称")
    gimbaltask_id = Column(
        String(36),
        ForeignKey("tb_gimbaltask.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联云台任务ID",
    )
    sort_order = Column(Integer, nullable=False, default=0, comment="排序值，数字越小越靠前")

    gimbal_task = relationship("GimbalTask", back_populates="inspection_projects")
    preset_points = relationship(
        "GimbalInspectionProjectPresetPoint",
        back_populates="inspection_project",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_project_name", "task_name"),
        Index("idx_gimbaltask_id", "gimbaltask_id"),
        Index("idx_gimbaltask_sort_order", "gimbaltask_id", "sort_order"),
        Index("idx_created_at", "created_at"),
        Index("idx_is_deleted", "is_deleted"),
        Index(
            "uk_project_name_per_task",
            "gimbaltask_id",
            "task_name",
            "is_deleted",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<GimbalInspectionProject(id='{self.id}', task_name='{self.task_name}', "
            f"gimbaltask_id='{self.gimbaltask_id}', sort_order='{self.sort_order}')>"
        )

