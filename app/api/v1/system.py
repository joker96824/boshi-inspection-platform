"""
系统相关API路由
"""

from fastapi import APIRouter
from ...config.settings import settings
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    from ...main import app
    
    ros2_bridge = app.state.ros2_bridge
    connection_manager = app.state.connection_manager
    
    return ApiResponse.success(
        data={
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "ros2_connected": ros2_bridge.is_ros2_available() if ros2_bridge else False,
            "websocket_connections": connection_manager.get_connection_count() if connection_manager else 0,
        },
        message="系统健康检查成功"
    )


@router.get("/info")
async def get_system_info():
    """获取系统信息"""
    return ApiResponse.success(
        data={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "docs_url": "/docs" if settings.DEBUG else None,
        },
        message="获取系统信息成功"
    )
