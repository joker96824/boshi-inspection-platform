"""
博实智能巡检平台主应用
"""

from fastapi import FastAPI, WebSocket

from .core.app_factory import create_app, setup_lifespan_events
from .api.v1 import auth, users, ros2, system, logs, maps, mapnets, robots, points, items, point_items, itemhistories, tasks, taskschedules, taskhistories, taskresults, alarmrules, alarminfos
from .config.settings import settings
from .utils.response import ApiResponse

# 创建应用实例
app = create_app()

# 设置生命周期事件
setup_lifespan_events(app)


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return ApiResponse.success(
        data={
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.DEBUG else "文档已禁用",
        },
        message="欢迎使用博实智能巡检平台"
    )


# 注册API路由
def register_routes():
    """注册所有API路由"""
    # 业务API路由
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
    app.include_router(maps.router, prefix="/api/v1/maps", tags=["地图管理"])
    app.include_router(mapnets.router, prefix="/api/v1/mapnets", tags=["地图路网管理"])
    app.include_router(robots.router, prefix="/api/v1/robots", tags=["机器人管理"])
    app.include_router(points.router, prefix="/api/v1/points", tags=["巡检点管理"])
    app.include_router(items.router, prefix="/api/v1/items", tags=["巡检项目管理"])
    app.include_router(point_items.router, prefix="/api/v1/point-items", tags=["巡检中间表管理"])
    app.include_router(itemhistories.router, prefix="/api/v1/itemhistories", tags=["巡检记录管理"])
    app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["任务管理"])
    app.include_router(taskschedules.router, prefix="/api/v1/taskschedules", tags=["任务日程管理"])
    app.include_router(taskhistories.router, prefix="/api/v1/taskhistories", tags=["任务记录管理"])
    app.include_router(taskresults.router, prefix="/api/v1/taskresults", tags=["任务结果管理"])
    app.include_router(alarmrules.router, prefix="/api/v1/alarmrules", tags=["报警规则管理"])
    app.include_router(alarminfos.router, prefix="/api/v1/alarminfos", tags=["报警信息管理"])
    
    # 系统API路由
    app.include_router(system.router, prefix="/api/v1/system", tags=["系统"])
    app.include_router(logs.router, prefix="/api/v1/logs", tags=["日志管理"])
    
    # ROS2 API路由
    app.include_router(ros2.router, prefix="/api/v1/ros2", tags=["ROS2"])


# 注册路由
register_routes()

# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    websocket_handler = app.state.websocket_handler
    if websocket_handler:
        await websocket_handler.handle_websocket(websocket)
    else:
        await websocket.close(code=1011, reason="WebSocket处理器未初始化")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower(),
    )
