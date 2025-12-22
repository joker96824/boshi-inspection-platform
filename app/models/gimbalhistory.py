"""
云台巡检记录数据模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class GimbalHistory(BaseModel):
    """云台巡检记录模型"""

    __tablename__ = "tb_gimbalhistory"

    project_preset_point_id = Column(
        String(36),
        ForeignKey("tb_gimbal_inspection_project_preset_point.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联云台巡检项目-预设点关联ID",
    )
    record_data = Column(JSON, nullable=True, comment="记录数据")
    media_url = Column(String(500), nullable=True, comment="图像/视频链接")
    view_status = Column(String(20), nullable=True, comment="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status = Column(String(20), nullable=True, comment="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")

    project_preset_point = relationship(
        "GimbalInspectionProjectPresetPoint", back_populates="histories"
    )

    __table_args__ = (
        Index("idx_project_preset_point_id", "project_preset_point_id"),
        Index("idx_view_status", "view_status"),
        Index("idx_inspection_result_status", "inspection_result_status"),
        Index("idx_created_at", "created_at"),
        Index("idx_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        return (
            f"<GimbalHistory(id='{self.id}', project_preset_point_id='{self.project_preset_point_id}')>"
        )
