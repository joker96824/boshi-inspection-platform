"""
WebSocket 工具函数
用于在业务逻辑层中发送 WebSocket 消息
"""

from typing import Dict, Any, Optional
from fastapi import Request
from ..websocket import ConnectionManager
from ..config.logging import get_logger

logger = get_logger(__name__)


async def send_websocket_message(
    request: Request,
    message: Dict[str, Any],
    message_type: str
) -> None:
    """发送 WebSocket 消息到订阅了对应类型的连接
    
    使用示例：
    ```python
    from ..utils.websocket_helper import send_websocket_message
    
    # 在业务逻辑中发送消息
    await send_websocket_message(
        request,
        {
            "type": "alarm_info",
            "data": {
                "alarm_id": "123",
                "alarm_message": "设备异常"
            },
            "timestamp": time.time()
        },
        "alarm_info"
    )
    ```
    
    Args:
        request: FastAPI Request 对象
        message: 要发送的消息字典，必须包含 'type' 字段
        message_type: 消息类型，用于订阅过滤
    """
    try:
        connection_manager: Optional[ConnectionManager] = getattr(
            request.app.state, 'connection_manager', None
        )
        
        if connection_manager:
            await connection_manager.broadcast_by_type(message, message_type)
            logger.debug(f"已发送 WebSocket 消息: {message_type}")
        else:
            logger.warning("ConnectionManager 未初始化，无法发送 WebSocket 消息")
            
    except Exception as e:
        logger.error(f"发送 WebSocket 消息失败: {e}", exc_info=True)


def get_connection_manager(request: Request) -> Optional[ConnectionManager]:
    """获取 ConnectionManager 实例
    
    Args:
        request: FastAPI Request 对象
    
    Returns:
        ConnectionManager 实例，如果未初始化则返回 None
    """
    return getattr(request.app.state, 'connection_manager', None)

