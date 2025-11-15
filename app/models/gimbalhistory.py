"""
云台巡检记录数据模型
"""

from sqlalchemy import Column, String, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class GimbalHistory(BaseModel):
    """云台巡检记录模型"""

    __tablename__ = "tb_gimbalhistory"

    inspection_project_id = Column(
        String(36),
        ForeignKey("tb_gimbal_inspection_project.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联云台巡检项目ID",
    )
    record_data = Column(JSON, nullable=True, comment="记录数据")
    media_url = Column(String(500), nullable=True, comment="图像/视频链接")

    inspection_project = relationship(
        "GimbalInspectionProject", back_populates="histories"
    )

    __table_args__ = (
        Index("idx_inspection_project_id", "inspection_project_id"),
        Index("idx_created_at", "created_at"),
        Index("idx_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        return (
            f"<GimbalHistory(id='{self.id}', inspection_project_id='{self.inspection_project_id}')>"
        )
