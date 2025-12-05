"""
WebSocket连接管理器
"""

import json
from typing import List, Dict, Any, Set
from fastapi import WebSocket

from ..config.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
        # 每个连接的订阅集合，key为WebSocket，value为Set[str]（订阅的消息类型）
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None, connection_type: str = "default"):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            "user_id": user_id,
            "connection_type": connection_type,
            "connected_at": None
        }
        # 默认订阅所有消息类型（使用 '*' 表示全局订阅）
        self.subscriptions[websocket] = {"*"}
        
        logger.info(f"WebSocket连接已建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        
        # 清理订阅信息
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        
        logger.info(f"WebSocket连接已断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"发送个人消息失败: {e}")
            self.disconnect(websocket)
    
    async def send_json_message(self, message: dict, websocket: WebSocket):
        """发送JSON消息"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"发送JSON消息失败: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """广播消息到所有连接"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.append(connection)
        
        # 移除断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, message: dict):
        """广播JSON消息到所有连接"""
        await self.broadcast(json.dumps(message))
    
    async def broadcast_to_type(self, message: dict, connection_type: str):
        """广播消息到指定类型的连接"""
        disconnected = []
        for connection in self.active_connections:
            if connection in self.connection_data:
                if self.connection_data[connection].get("connection_type") == connection_type:
                    try:
                        await connection.send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"广播消息到类型 {connection_type} 失败: {e}")
                        disconnected.append(connection)
        
        # 移除断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_user(self, message: dict, user_id: str):
        """广播消息到指定用户"""
        disconnected = []
        for connection in self.active_connections:
            if connection in self.connection_data:
                if self.connection_data[connection].get("user_id") == user_id:
                    try:
                        await connection.send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"广播消息到用户 {user_id} 失败: {e}")
                        disconnected.append(connection)
        
        # 移除断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_count(self) -> int:
        """获取连接数量"""
        return len(self.active_connections)
    
    def get_connections_by_type(self, connection_type: str) -> List[WebSocket]:
        """获取指定类型的连接"""
        connections = []
        for connection in self.active_connections:
            if connection in self.connection_data:
                if self.connection_data[connection].get("connection_type") == connection_type:
                    connections.append(connection)
        return connections
    
    def get_connections_by_user(self, user_id: str) -> List[WebSocket]:
        """获取指定用户的连接"""
        connections = []
        for connection in self.active_connections:
            if connection in self.connection_data:
                if self.connection_data[connection].get("user_id") == user_id:
                    connections.append(connection)
        return connections
    
    async def subscribe(self, websocket: WebSocket, message_types: List[str]):
        """订阅消息类型
        
        Args:
            websocket: WebSocket连接
            message_types: 要订阅的消息类型列表
        """
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()
        
        self.subscriptions[websocket].update(message_types)
        logger.info(
            f"连接已订阅消息类型: {message_types}，当前订阅: {list(self.subscriptions[websocket])}",
            extra={"user_id": self.connection_data.get(websocket, {}).get("user_id")}
        )
    
    async def unsubscribe(self, websocket: WebSocket, message_types: List[str]):
        """取消订阅消息类型
        
        Args:
            websocket: WebSocket连接
            message_types: 要取消订阅的消息类型列表
        """
        if websocket in self.subscriptions:
            self.subscriptions[websocket].difference_update(message_types)
            # 如果订阅集合为空，则重新订阅所有消息（防止完全无订阅）
            if not self.subscriptions[websocket]:
                self.subscriptions[websocket].add("*")
            
            logger.info(
                f"连接已取消订阅: {message_types}，当前订阅: {list(self.subscriptions[websocket])}",
                extra={"user_id": self.connection_data.get(websocket, {}).get("user_id")}
            )
        else:
            logger.warning(f"连接不存在订阅信息，无法取消订阅")
    
    async def broadcast_by_type(self, message: dict, message_type: str):
        """按消息类型广播（只发送给订阅了该类型的连接）
        
        Args:
            message: 要广播的消息字典
            message_type: 消息类型
        """
        if not message_type:
            logger.warning("消息类型为空，跳过广播")
            return
        
        disconnected = []
        sent_count = 0
        total_connections = len(self.active_connections)
        
        for connection in self.active_connections:
            # 检查连接是否订阅了该消息类型
            if connection in self.subscriptions:
                subscribed_types = self.subscriptions[connection]
                # 如果订阅了该类型或者是全局订阅（'*'），则发送
                if message_type in subscribed_types or "*" in subscribed_types:
                    try:
                        await connection.send_text(json.dumps(message))
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"广播消息失败: {e}")
                        disconnected.append(connection)
            else:
                # 如果没有订阅信息，默认发送（兼容旧连接）
                try:
                    await connection.send_text(json.dumps(message))
                    sent_count += 1
                except Exception as e:
                    logger.error(f"广播消息失败: {e}")
                    disconnected.append(connection)
        
        # 记录发送统计（仅在发送成功时记录）
        if sent_count > 0:
            logger.debug(
                f"消息广播完成: 类型={message_type}, 发送={sent_count}/{total_connections}连接"
            )
        
        # 移除断开的连接
        for connection in disconnected:
            self.disconnect(connection)