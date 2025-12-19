"""
ROS2集成模块
"""

try:
    from .ros2_bridge import ROS2Bridge
    ROS2_AVAILABLE = True
except ImportError as e:
    ROS2_AVAILABLE = False
    ROS2Bridge = None
    import sys
    from ..config.logging import get_logger
    logger = get_logger(__name__)
    logger.warning(f"ROS2模块不可用: {e}，ROS2功能将被禁用")

__all__ = [
    "ROS2Bridge",
    "ROS2_AVAILABLE",
]