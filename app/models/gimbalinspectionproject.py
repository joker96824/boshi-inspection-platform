"""
云台巡检项目数据模型
"""

from sqlalchemy import Column, String, Index, ForeignKey, Float, Integer, Boolean
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
    x_coordinate = Column(Float, nullable=True, comment="镜头X轴旋转参数")
    y_coordinate = Column(Float, nullable=True, comment="镜头Y轴旋转参数")
    zoom_level = Column(Float, nullable=True, comment="倍率")
    focus = Column(Float, nullable=True, comment="聚焦")
    aperture = Column(Integer, nullable=True, comment="光圈（0-100）")
    shutter = Column(Integer, nullable=True, comment="快门分母")
    backlight_compensation = Column(Boolean, nullable=False, default=False, comment="背光补偿")
    wide_dynamic = Column(Boolean, nullable=False, default=False, comment="宽动态")
    strong_light_suppression = Column(Boolean, nullable=False, default=False, comment="强光抑制")
    fill_light = Column(Boolean, nullable=False, default=False, comment="补光")
    detection_type = Column(
        String(20),
        nullable=False,
        comment="检测类型：可见光视频/可见光图片/热成像图片/热成像视频",
    )

    gimbal_task = relationship("GimbalTask", back_populates="inspection_projects")
    histories = relationship(
        "GimbalHistory",
        back_populates="inspection_project",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_project_name", "task_name"),
        Index("idx_gimbaltask_id", "gimbaltask_id"),
        Index("idx_detection_type", "detection_type"),
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
            "<GimbalInspectionProject(id='{id}', task_name='{name}', gimbaltask_id='{task_id}', "
            "detection_type='{dtype}', sort_order='{order}')>".format(
                id=self.id,
                name=self.task_name,
                task_id=self.gimbaltask_id,
                dtype=self.detection_type,
                order=self.sort_order,
            )
        )

