"""
云台巡检项目-预设点关联模型（多对多中间表）
"""

from sqlalchemy import Column, String, ForeignKey, Integer, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class GimbalInspectionProjectPresetPoint(BaseModel):
    """云台巡检项目-预设点关联模型（多对多中间表）"""

    __tablename__ = "tb_gimbal_inspection_project_preset_point"

    # 基础字段
    inspection_project_id = Column(
        String(36),
        ForeignKey("tb_gimbal_inspection_project.id", ondelete="CASCADE"),
        nullable=False,
        comment="云台巡检项目ID",
    )
    preset_point_id = Column(
        String(36),
        ForeignKey("tb_gimbal_preset_point.id", ondelete="CASCADE"),
        nullable=False,
        comment="云台预设点ID",
    )
    
    # 检测类型和拍摄时长
    detection_type = Column(
        String(20),
        nullable=False,
        comment="检测类型：可见光视频/可见光图片/热成像图片/热成像视频",
    )
    video_duration = Column(
        Integer,
        nullable=True,
        comment="拍摄时长（秒），当detection_type为可见光视频或热成像视频时使用",
    )

    # 关系
    inspection_project = relationship(
        "GimbalInspectionProject",
        back_populates="preset_points",
    )
    preset_point = relationship(
        "GimbalPresetPoint",
        back_populates="inspection_projects",
    )
    histories = relationship(
        "GimbalHistory",
        back_populates="project_preset_point",
        cascade="all, delete-orphan",
    )

    # 创建索引和唯一约束
    __table_args__ = (
        Index("idx_inspection_project_id", "inspection_project_id"),
        Index("idx_preset_point_id", "preset_point_id"),
        Index("idx_detection_type", "detection_type"),
        Index("idx_created_at", "created_at"),
        Index("idx_is_deleted", "is_deleted"),
        # 确保未删除的 inspection_project_id + preset_point_id + detection_type 组合是唯一的
        UniqueConstraint(
            "inspection_project_id",
            "preset_point_id",
            "detection_type",
            "is_deleted",
            name="uk_project_preset_detection_active",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<GimbalInspectionProjectPresetPoint("
            f"inspection_project_id='{self.inspection_project_id}', "
            f"preset_point_id='{self.preset_point_id}', "
            f"detection_type='{self.detection_type}')>"
        )

