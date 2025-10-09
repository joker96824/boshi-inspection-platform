"""
WebSocket连接管理器
"""

import json
from typing import List, Dict, Any
from fastapi import WebSocket

from ..config.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None, connection_type: str = "default"):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            "user_id": user_id,
            "connection_type": connection_type,
            "connected_at": None
        }
        
        logger.info(f"WebSocket连接已建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        
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