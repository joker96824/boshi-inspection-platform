"""
WebSocket处理器
"""

import asyncio
import json
import time
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

from .connection_manager import ConnectionManager
from ..ros import ROS2Bridge
from ..config.logging import get_logger

logger = get_logger(__name__)


class WebSocketHandler:
    """WebSocket消息处理器"""
    
    def __init__(self, connection_manager: ConnectionManager, ros2_bridge: ROS2Bridge = None):
        self.connection_manager = connection_manager
        self.ros2_bridge = ros2_bridge
        
        # 注册 ROS2 消息回调，实现实时数据转发
        if self.ros2_bridge:
            self.ros2_bridge.add_message_callback(self._handle_ros2_message)
    
    def _handle_ros2_message(self, message: Dict[str, Any]):
        """处理ROS2消息并转发到所有WebSocket连接"""
        try:
            # 添加时间戳
            message["timestamp"] = time.time()
            
            # 使用线程安全的方式广播消息
            import asyncio
            import threading
            
            def broadcast_sync():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.connection_manager.broadcast_json(message))
                    loop.close()
                except Exception as e:
                    logger.error(f"异步广播失败: {e}")
            
            # 在新线程中执行广播
            thread = threading.Thread(target=broadcast_sync)
            thread.daemon = True
            thread.start()
            
            logger.debug(f"ROS2消息已转发: {message['type']} -> {message.get('topic', 'unknown')}")
            
        except Exception as e:
            logger.error(f"转发ROS2消息失败: {e}")
    
    async def handle_websocket(self, websocket: WebSocket, user_id: str = None):
        """处理WebSocket连接"""
        await self.connection_manager.connect(websocket, user_id, "frontend_client")
        
        try:
            while True:
                # 接收客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 处理不同类型的消息
                await self._process_message(message, websocket)
                
        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket处理错误: {e}")
            self.connection_manager.disconnect(websocket)
    
    async def _process_message(self, message: Dict[str, Any], websocket: WebSocket):
        """处理WebSocket消息"""
        message_type = message.get("type")
        
        if message_type == "ping":
            await self._handle_ping(websocket)
        elif message_type == "get_ros2_topics":
            await self._handle_get_ros2_topics(websocket)
        elif message_type == "publish_ros2_string":
            await self._handle_publish_ros2_string(message, websocket)
        elif message_type == "publish_ros2_int":
            await self._handle_publish_ros2_int(message, websocket)
        elif message_type == "publish_ros2_float":
            await self._handle_publish_ros2_float(message, websocket)
        elif message_type == "publish_ros2_cmd_vel":
            await self._handle_publish_ros2_cmd_vel(message, websocket)
        elif message_type == "get_connection_status":
            await self._handle_get_connection_status(websocket)
        else:
            await self._send_error_response(websocket, f"未知消息类型: {message_type}")
    
    async def _handle_ping(self, websocket: WebSocket):
        """处理ping请求"""
        await self.connection_manager.send_json_message({
            "type": "pong",
            "timestamp": time.time()
        }, websocket)
    
    async def _handle_get_ros2_topics(self, websocket: WebSocket):
        """处理获取ROS2话题列表请求"""
        if not self.ros2_bridge:
            await self.connection_manager.send_json_message({
                "type": "ros2_topics_response",
                "topics": [],
                "error": "ROS2 Bridge未初始化"
            }, websocket)
            return
        
        topics = self.ros2_bridge.get_topic_list()
        await self.connection_manager.send_json_message({
            "type": "ros2_topics_response",
            "topics": topics
        }, websocket)
    
    async def _handle_publish_ros2_string(self, message: Dict[str, Any], websocket: WebSocket):
        """处理ROS2字符串发布请求"""
        if not self.ros2_bridge:
            await self._send_error_response(websocket, "ROS2 Bridge未初始化")
            return
        
        data = message.get("data", "")
        topic = message.get("topic")
        
        self.ros2_bridge.publish_string(data, topic)
        
        # 发送确认响应
        await self.connection_manager.send_json_message({
            "type": "response",
            "status": "success",
            "message": f"已发布字符串: {data}"
        }, websocket)
    
    async def _handle_publish_ros2_int(self, message: Dict[str, Any], websocket: WebSocket):
        """处理ROS2整数发布请求"""
        if not self.ros2_bridge:
            await self._send_error_response(websocket, "ROS2 Bridge未初始化")
            return
        
        data = message.get("data", 0)
        topic = message.get("topic")
        
        self.ros2_bridge.publish_int(data, topic)
        
        # 发送确认响应
        await self.connection_manager.send_json_message({
            "type": "response",
            "status": "success",
            "message": f"已发布整数: {data}"
        }, websocket)
    
    async def _handle_publish_ros2_float(self, message: Dict[str, Any], websocket: WebSocket):
        """处理ROS2浮点数发布请求"""
        if not self.ros2_bridge:
            await self._send_error_response(websocket, "ROS2 Bridge未初始化")
            return
        
        data = message.get("data", 0.0)
        topic = message.get("topic")
        
        self.ros2_bridge.publish_float(data, topic)
        
        # 发送确认响应
        await self.connection_manager.send_json_message({
            "type": "response",
            "status": "success",
            "message": f"已发布浮点数: {data}"
        }, websocket)
    
    async def _handle_publish_ros2_cmd_vel(self, message: Dict[str, Any], websocket: WebSocket):
        """处理ROS2速度命令发布请求"""
        if not self.ros2_bridge:
            await self._send_error_response(websocket, "ROS2 Bridge未初始化")
            return
        
        data = message.get("data", {})
        linear_x = data.get("linear_x", 0.0)
        angular_z = data.get("angular_z", 0.0)
        
        self.ros2_bridge.publish_cmd_vel(linear_x, angular_z)
        
        # 发送确认响应
        await self.connection_manager.send_json_message({
            "type": "response",
            "status": "success",
            "message": f"已发布速度命令: linear={linear_x}, angular={angular_z}"
        }, websocket)
    
    async def _handle_get_connection_status(self, websocket: WebSocket):
        """处理获取连接状态请求"""
        status = {
            "type": "connection_status",
            "total_connections": self.connection_manager.get_connection_count(),
            "ros2_available": self.ros2_bridge.is_ros2_available() if self.ros2_bridge else False,
            "timestamp": time.time()
        }
        await self.connection_manager.send_json_message(status, websocket)
    
    async def _send_error_response(self, websocket: WebSocket, error_message: str):
        """发送错误响应"""
        await self.connection_manager.send_json_message({
            "type": "error",
            "message": error_message
        }, websocket)