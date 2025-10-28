"""
激光雷达配置数据模型
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Index
from .base import BaseModel


class Lidar(BaseModel):
    """激光雷达配置模型"""
    
    __tablename__ = "cfg_lidar"
    
    # 网络配置
    lidar_ip = Column(String(15), nullable=False, comment="激光雷达IP地址")
    subnet_mask = Column(String(15), nullable=False, default="255.255.255.0", comment="子网掩码")
    gateway = Column(String(15), nullable=False, default="192.168.1.1", comment="网关地址")
    lidar_port = Column(Integer, nullable=False, comment="激光雷达端口(1-65535)")
    
    # 雷达参数
    scan_frequency_rpm = Column(Integer, nullable=False, default=2000, comment="雷达扫描频率/转速Rpm")
    x_coordinate = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="X坐标")
    y_coordinate = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="Y坐标")
    z_coordinate = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="Z坐标")
    scan_range_min = Column(DECIMAL(5, 2), nullable=False, default=0.00, comment="扫描范围最小值(度)")
    scan_range_max = Column(DECIMAL(5, 2), nullable=False, default=360.00, comment="扫描范围最大值(度)")
    scan_distance_min = Column(DECIMAL(8, 2), nullable=False, default=0.00, comment="扫描距离最小值(米)")
    scan_distance_max = Column(DECIMAL(8, 2), nullable=False, default=100.00, comment="扫描距离最大值(米)")
    
    # 创建索引
    __table_args__ = (
        Index('idx_lidar_ip', 'lidar_ip'),
        Index('idx_lidar_port', 'lidar_port'),
        Index('idx_scan_frequency', 'scan_frequency_rpm'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Lidar(id='{self.id}', lidar_ip='{self.lidar_ip}', port={self.lidar_port})>"
