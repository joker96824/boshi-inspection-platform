"""
ROS2 Bridge - 提供WebSocket和HTTP接口与ROS2通信
"""

import asyncio
import json
from typing import Dict, List, Optional, Callable
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32, Float32
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

from ..config.logging import get_logger

logger = get_logger(__name__)


class ROS2Bridge(Node):
    """ROS2桥接节点"""
    
    def __init__(self):
        super().__init__('ros2_bridge_node')
        
        # 发布器 - 使用不同的属性名避免与父类冲突
        self.bridge_publishers: Dict[str, any] = {}
        self.bridge_subscribers: Dict[str, any] = {}
        
        # 消息回调
        self._message_callbacks: List[Callable] = []
        
        # 初始化基础话题
        self._init_default_topics()
        
        logger.info("ROS2 Bridge节点已启动")
    
    def _init_default_topics(self):
        """初始化默认话题"""
        # 字符串话题
        self.bridge_publishers['string'] = self.create_publisher(String, '/bridge/string', 10)
        self.bridge_subscribers['string'] = self.create_subscription(
            String, '/bridge/string_out', self._string_callback, 10
        )
        
        # 整数话题
        self.bridge_publishers['int'] = self.create_publisher(Int32, '/bridge/int', 10)
        self.bridge_subscribers['int'] = self.create_subscription(
            Int32, '/bridge/int_out', self._int_callback, 10
        )
        
        # 浮点数话题
        self.bridge_publishers['float'] = self.create_publisher(Float32, '/bridge/float', 10)
        self.bridge_subscribers['float'] = self.create_subscription(
            Float32, '/bridge/float_out', self._float_callback, 10
        )
        
        # 速度命令话题
        self.bridge_publishers['cmd_vel'] = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 激光雷达话题
        self.bridge_subscribers['laser'] = self.create_subscription(
            LaserScan, '/scan', self._laser_callback, 10
        )
    
    def _string_callback(self, msg):
        """字符串消息回调"""
        self._broadcast_message({
            "type": "string_message",
            "topic": "/bridge/string_out",
            "data": msg.data
        })
    
    def _int_callback(self, msg):
        """整数消息回调"""
        self._broadcast_message({
            "type": "int_message",
            "topic": "/bridge/int_out",
            "data": msg.data
        })
    
    def _float_callback(self, msg):
        """浮点数消息回调"""
        self._broadcast_message({
            "type": "float_message",
            "topic": "/bridge/float_out",
            "data": msg.data
        })
    
    def _laser_callback(self, msg):
        """激光雷达消息回调"""
        self._broadcast_message({
            "type": "laser_scan",
            "topic": "/scan",
            "data": {
                "ranges": list(msg.ranges),
                "angle_min": msg.angle_min,
                "angle_max": msg.angle_max,
                "angle_increment": msg.angle_increment,
                "range_min": msg.range_min,
                "range_max": msg.range_max
            }
        })
    
    def _broadcast_message(self, message: dict):
        """广播消息到所有回调"""
        if not isinstance(self._message_callbacks, list):
            self._message_callbacks = []
        for callback in self._message_callbacks:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"消息回调错误: {e}")
    
    def add_message_callback(self, callback: Callable):
        """添加消息回调"""
        if not isinstance(self._message_callbacks, list):
            self._message_callbacks = []
        self._message_callbacks.append(callback)
    
    def remove_message_callback(self, callback: Callable):
        """移除消息回调"""
        if not isinstance(self._message_callbacks, list):
            self._message_callbacks = []
        if callback in self._message_callbacks:
            self._message_callbacks.remove(callback)
    
    def publish_string(self, data: str, topic: str = None):
        """发布字符串消息"""
        if topic is None:
            topic = 'string'
        
        if topic in self.bridge_publishers:
            msg = String()
            msg.data = data
            self.bridge_publishers[topic].publish(msg)
            logger.info(f"发布字符串消息到 {topic}: {data}")
        else:
            logger.warning(f"话题 {topic} 不存在")
    
    def publish_int(self, data: int, topic: str = None):
        """发布整数消息"""
        if topic is None:
            topic = 'int'
        
        if topic in self.bridge_publishers:
            msg = Int32()
            msg.data = data
            self.bridge_publishers[topic].publish(msg)
            logger.info(f"发布整数消息到 {topic}: {data}")
        else:
            logger.warning(f"话题 {topic} 不存在")
    
    def publish_float(self, data: float, topic: str = None):
        """发布浮点数消息"""
        if topic is None:
            topic = 'float'
        
        if topic in self.bridge_publishers:
            msg = Float32()
            msg.data = data
            self.bridge_publishers[topic].publish(msg)
            logger.info(f"发布浮点数消息到 {topic}: {data}")
        else:
            logger.warning(f"话题 {topic} 不存在")
    
    def publish_cmd_vel(self, linear_x: float, angular_z: float):
        """发布速度命令"""
        if 'cmd_vel' in self.bridge_publishers:
            msg = Twist()
            msg.linear.x = linear_x
            msg.angular.z = angular_z
            self.bridge_publishers['cmd_vel'].publish(msg)
            logger.info(f"发布速度命令: linear={linear_x}, angular={angular_z}")
        else:
            logger.warning("cmd_vel话题不存在")
    
    def get_topic_list(self) -> List[str]:
        """获取话题列表"""
        try:
            import subprocess
            result = subprocess.run(['ros2', 'topic', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            else:
                return []
        except Exception as e:
            logger.error(f"获取话题列表失败: {e}")
            return []
    
    def is_ros2_available(self) -> bool:
        """检查ROS2是否可用"""
        return rclpy.ok()