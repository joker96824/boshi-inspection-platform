"""
云台预设点数据模型
"""

from sqlalchemy import Column, String, Index, ForeignKey, Float, Integer, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel


class GimbalPresetPoint(BaseModel):
    """云台预设点模型"""

    __tablename__ = "tb_gimbal_preset_point"

    # 基础字段
    preset_name = Column(String(100), nullable=False, comment="预设点名称")
    gimbal_id = Column(
        String(36),
        ForeignKey("tb_gimbal.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联云台ID",
    )
    
    # PTZF 坐标参数
    p_coordinate = Column(Float, nullable=True, comment="P坐标（水平旋转）")
    t_coordinate = Column(Float, nullable=True, comment="T坐标（垂直旋转）")
    z_coordinate = Column(Float, nullable=True, comment="Z坐标（变焦）")
    f_coordinate = Column(Float, nullable=True, comment="F坐标（聚焦）")
    
    # 相机拍摄参数
    aperture = Column(Integer, nullable=True, comment="光圈（0-100）")
    shutter = Column(Integer, nullable=True, comment="快门分母")
    
    # 图像处理参数
    backlight_compensation = Column(Boolean, nullable=False, default=False, comment="背光补偿")
    wide_dynamic = Column(Boolean, nullable=False, default=False, comment="宽动态")
    strong_light_suppression = Column(Boolean, nullable=False, default=False, comment="强光抑制")
    fill_light = Column(Boolean, nullable=False, default=False, comment="补光")
    
    # 图片链接
    image_url = Column(String(500), nullable=True, comment="图片链接")

    # 关系
    gimbal = relationship("Gimbal", back_populates="preset_points")
    inspection_projects = relationship(
        "GimbalInspectionProjectPresetPoint",
        back_populates="preset_point",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_preset_name", "preset_name"),
        Index("idx_gimbal_id", "gimbal_id"),
        Index("idx_created_at", "created_at"),
        Index("idx_is_deleted", "is_deleted"),
        Index(
            "uk_preset_name_per_gimbal",
            "gimbal_id",
            "preset_name",
            "is_deleted",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<GimbalPresetPoint(id='{self.id}', preset_name='{self.preset_name}', "
            f"gimbal_id='{self.gimbal_id}')>"
        )

