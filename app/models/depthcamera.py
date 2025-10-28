"""
深度相机配置数据模型
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Enum, Index
from .base import BaseModel


class DepthCamera(BaseModel):
    """深度相机配置模型"""
    
    __tablename__ = "cfg_depth_camera"
    
    # 相机基本信息
    camera_type = Column(Enum('RGB-D', 'ToF', 'Stereo', 'Structured_Light', name='camera_type'), nullable=False, default='RGB-D', comment="深度相机类型")
    resolution_width = Column(Integer, nullable=False, default=640, comment="分辨率宽度")
    resolution_height = Column(Integer, nullable=False, default=480, comment="分辨率高度")
    frame_rate = Column(Integer, nullable=False, default=30, comment="帧率(fps)")
    
    # 深度参数
    depth_range_min = Column(DECIMAL(8, 2), nullable=False, default=0.10, comment="最小深度范围(m)")
    depth_range_max = Column(DECIMAL(8, 2), nullable=False, default=10.00, comment="最大深度范围(m)")
    depth_accuracy = Column(DECIMAL(8, 4), nullable=False, default=0.0010, comment="深度精度(m)")
    
    # 网络配置
    camera_ip = Column(String(15), nullable=True, comment="相机IP地址")
    camera_port = Column(Integer, nullable=True, comment="相机端口号")
    protocol = Column(Enum('USB', 'Ethernet', 'WiFi', 'Serial', name='protocol'), nullable=False, default='USB', comment="连接协议")
    
    # 相机参数
    exposure_time = Column(Integer, nullable=True, comment="曝光时间(μs)")
    gain = Column(DECIMAL(5, 2), nullable=True, comment="增益值")
    white_balance = Column(Enum('Auto', 'Manual', 'Daylight', 'Fluorescent', 'Tungsten', name='white_balance'), nullable=False, default='Auto', comment="白平衡模式")
    
    # 创建索引
    __table_args__ = (
        Index('idx_camera_type', 'camera_type'),
        Index('idx_camera_ip', 'camera_ip'),
        Index('idx_protocol', 'protocol'),
        Index('idx_frame_rate', 'frame_rate'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<DepthCamera(id='{self.id}', type='{self.camera_type}')>"

