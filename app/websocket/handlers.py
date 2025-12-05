"""
WebSocket处理器
"""

import asyncio
import json
import time
import threading
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
        
        # 测试任务控制
        self._test_tasks_running = False
        self._test_alarm_counter = 0
        self._test_robot_counter = 0
        self._test_alarm_task = None
        self._test_robot_task = None
    
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
        elif message_type == "subscribe":
            await self._handle_subscribe(message, websocket)
        elif message_type == "unsubscribe":
            await self._handle_unsubscribe(message, websocket)
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
        elif message_type == "start_test":
            await self._handle_start_test(websocket)
        elif message_type == "stop_test":
            await self._handle_stop_test(websocket)
        else:
            await self._send_error_response(websocket, f"未知消息类型: {message_type}")
    
    async def _handle_ping(self, websocket: WebSocket):
        """处理ping请求"""
        await self.connection_manager.send_json_message({
            "type": "pong",
            "timestamp": time.time()
        }, websocket)
    
    async def _handle_subscribe(self, message: Dict[str, Any], websocket: WebSocket):
        """处理订阅请求
        
        前端发送格式:
        {
            "type": "subscribe",
            "message_types": ["laser_scan", "robot_status", "alarm_info"]
        }
        """
        message_types = message.get("message_types", [])
        if not isinstance(message_types, list):
            await self._send_error_response(websocket, "message_types 必须是列表")
            return
        
        if not message_types:
            await self._send_error_response(websocket, "message_types 不能为空")
            return
        
        await self.connection_manager.subscribe(websocket, message_types)
        
        # 获取用户信息用于日志
        user_id = self.connection_manager.connection_data.get(websocket, {}).get("user_id")
        
        logger.info(
            f"收到订阅请求: {message_types}，当前连接数: {self.connection_manager.get_connection_count()}",
            extra={"user_id": user_id, "message_types": message_types}
        )
        
        await self.connection_manager.send_json_message({
            "type": "subscribe_ack",
            "message_types": message_types,
            "timestamp": time.time()
        }, websocket)
    
    async def _handle_unsubscribe(self, message: Dict[str, Any], websocket: WebSocket):
        """处理取消订阅请求
        
        前端发送格式:
        {
            "type": "unsubscribe",
            "message_types": ["laser_scan"]
        }
        """
        message_types = message.get("message_types", [])
        if not isinstance(message_types, list):
            await self._send_error_response(websocket, "message_types 必须是列表")
            return
        
        await self.connection_manager.unsubscribe(websocket, message_types)
        await self.connection_manager.send_json_message({
            "type": "unsubscribe_ack",
            "message_types": message_types,
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
    
    async def start_test_tasks(self):
        """启动测试任务（后台运行）"""
        if self._test_tasks_running:
            return
        
        self._test_tasks_running = True
        self._test_alarm_counter = 0
        self._test_robot_counter = 0
        
        # 启动报警信息测试任务（每10秒）
        self._test_alarm_task = asyncio.create_task(self._test_alarm_task_loop())
        
        # 启动机器人信息测试任务（每2秒）
        self._test_robot_task = asyncio.create_task(self._test_robot_task_loop())
        
        logger.info("WebSocket测试任务已启动：报警信息每10秒，机器人信息每2秒")
    
    def _stop_test_tasks(self):
        """停止测试任务"""
        if not self._test_tasks_running:
            return
        
        self._test_tasks_running = False
        
        if self._test_alarm_task and not self._test_alarm_task.done():
            self._test_alarm_task.cancel()
        
        if self._test_robot_task and not self._test_robot_task.done():
            self._test_robot_task.cancel()
        
        logger.info("WebSocket测试任务已停止")
    
    async def _test_alarm_task_loop(self):
        """报警信息测试任务循环（每10秒发送一次）"""
        try:
            while self._test_tasks_running:
                await asyncio.sleep(10)
                
                if not self._test_tasks_running:
                    break
                
                self._test_alarm_counter += 1
                alarm_message = {
                    "type": "alarm_info",
                    "data": {
                        "alarm_id": f"test_alarm_{self._test_alarm_counter}",
                        "alarm_type": "测试报警",
                        "alarm_level": "warning",
                        "alarm_message": f"这是第 {self._test_alarm_counter} 条测试报警信息",
                        "robot_id": "test_robot_001",
                        "robot_name": "测试机器人",
                        "location": "测试区域A",
                        "timestamp": time.time()
                    },
                    "timestamp": time.time()
                }
                
                await self.connection_manager.broadcast_by_type(alarm_message, "alarm_info")
                logger.debug(f"已发送测试报警信息 #{self._test_alarm_counter}")
                
        except asyncio.CancelledError:
            logger.info("报警信息测试任务已取消")
        except Exception as e:
            logger.error(f"报警信息测试任务错误: {e}", exc_info=True)
    
    async def _test_robot_task_loop(self):
        """机器人信息测试任务循环（每2秒发送一次）"""
        try:
            while self._test_tasks_running:
                await asyncio.sleep(2)
                
                if not self._test_tasks_running:
                    break
                
                self._test_robot_counter += 1
                robot_message = {
                    "type": "robot_status",
                    "data": {
                        "robot_id": "test_robot_001",
                        "robot_name": "测试机器人",
                        "status": "running" if self._test_robot_counter % 2 == 0 else "idle",
                        "battery": max(20, 100 - (self._test_robot_counter % 80)),
                        "position": {
                            "x": round(1.0 + (self._test_robot_counter * 0.1) % 10, 2),
                            "y": round(2.0 + (self._test_robot_counter * 0.15) % 10, 2),
                            "theta": round((self._test_robot_counter * 5) % 360, 2)
                        },
                        "velocity": {
                            "linear": round(0.5 + (self._test_robot_counter % 3) * 0.2, 2),
                            "angular": round((self._test_robot_counter % 5) * 0.1, 2)
                        },
                        "task_id": f"task_{self._test_robot_counter % 5}" if self._test_robot_counter % 2 == 0 else None,
                        "timestamp": time.time()
                    },
                    "timestamp": time.time()
                }
                
                await self.connection_manager.broadcast_by_type(robot_message, "robot_status")
                logger.debug(f"已发送测试机器人信息 #{self._test_robot_counter}")
                
        except asyncio.CancelledError:
            logger.info("机器人信息测试任务已取消")
        except Exception as e:
            logger.error(f"机器人信息测试任务错误: {e}", exc_info=True)
    
    async def _handle_start_test(self, websocket: WebSocket):
        """处理启动测试任务请求"""
        if not self._test_tasks_running:
            await self.start_test_tasks()
            await self.connection_manager.send_json_message({
                "type": "test_started",
                "message": "测试任务已启动",
                "timestamp": time.time()
            }, websocket)
        else:
            await self.connection_manager.send_json_message({
                "type": "test_started",
                "message": "测试任务已在运行中",
                "timestamp": time.time()
            }, websocket)
    
    async def _handle_stop_test(self, websocket: WebSocket):
        """处理停止测试任务请求"""
        if self._test_tasks_running:
            self._stop_test_tasks()
            await self.connection_manager.send_json_message({
                "type": "test_stopped",
                "message": "测试任务已停止",
                "timestamp": time.time()
            }, websocket)
        else:
            await self.connection_manager.send_json_message({
                "type": "test_stopped",
                "message": "测试任务未运行",
                "timestamp": time.time()
            }, websocket)