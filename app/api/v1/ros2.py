"""
ROS2相关API路由
"""

from fastapi import APIRouter, Depends
from typing import Dict

from ...ros import ROS2Bridge
from ...core.auth import get_current_user
from ...core.exceptions import ROS2Error, ParameterError
from ...utils.response import ApiResponse

router = APIRouter()


def get_ros2_bridge() -> ROS2Bridge:
    """获取ROS2 Bridge实例"""
    from fastapi import Request
    from ...main import app
    
    ros2_bridge = app.state.ros2_bridge
    if not ros2_bridge:
        raise ROS2Error("ROS2 Bridge未初始化")
    return ros2_bridge


@router.get("/topics")
async def get_ros2_topics(
    current_user = Depends(get_current_user)
):
    """获取ROS2话题列表"""
    ros2_bridge = get_ros2_bridge()
    topics = ros2_bridge.get_topic_list()
    return ApiResponse.success(
        data={"topics": topics},
        message="获取ROS2话题列表成功"
    )


@router.post("/publish/string")
async def publish_string_message(
    data: Dict[str, str],
    current_user = Depends(get_current_user)
):
    """发布字符串消息"""
    ros2_bridge = get_ros2_bridge()
    
    message = data.get("message", "")
    topic = data.get("topic")
    if not topic:
        raise ParameterError("缺少topic参数", "topic")
    
    ros2_bridge.publish_string(message, topic)
    return ApiResponse.success(
        message=f"已发布字符串: {message} 到话题: {topic}"
    )


@router.post("/publish/int")
async def publish_int_message(
    data: Dict[str, int],
    current_user = Depends(get_current_user)
):
    """发布整数消息"""
    ros2_bridge = get_ros2_bridge()
    
    message = data.get("message", 0)
    topic = data.get("topic")
    if not topic:
        raise ParameterError("缺少topic参数", "topic")
    
    ros2_bridge.publish_int(message, topic)
    return ApiResponse.success(
        message=f"已发布整数: {message} 到话题: {topic}"
    )


@router.post("/publish/float")
async def publish_float_message(
    data: Dict[str, float],
    current_user = Depends(get_current_user)
):
    """发布浮点数消息"""
    ros2_bridge = get_ros2_bridge()
    
    message = data.get("message", 0.0)
    topic = data.get("topic")
    if not topic:
        raise ParameterError("缺少topic参数", "topic")
    
    ros2_bridge.publish_float(message, topic)
    return ApiResponse.success(
        message=f"已发布浮点数: {message} 到话题: {topic}"
    )


@router.post("/publish/cmd_vel")
async def publish_cmd_vel_message(
    data: Dict[str, float],
    current_user = Depends(get_current_user)
):
    """发布速度命令"""
    ros2_bridge = get_ros2_bridge()
    
    linear_x = data.get("linear_x", 0.0)
    angular_z = data.get("angular_z", 0.0)
    
    ros2_bridge.publish_cmd_vel(linear_x, angular_z)
    return ApiResponse.success(
        message=f"已发布速度命令: linear={linear_x}, angular={angular_z}"
    )


@router.get("/status")
async def get_ros2_status(
    current_user = Depends(get_current_user)
):
    """获取ROS2状态"""
    ros2_bridge = get_ros2_bridge()
    
    return ApiResponse.success(
        data={
            "connected": ros2_bridge.is_ros2_available(),
            "topics_count": len(ros2_bridge.get_topic_list()),
            "publishers": list(ros2_bridge.bridge_publishers.keys()),
            "subscribers": list(ros2_bridge.bridge_subscribers.keys())
        },
        message="获取ROS2状态成功"
    )
