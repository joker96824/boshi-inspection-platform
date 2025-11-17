"""
应用工厂函数
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError
import traceback

from ..config.settings import settings
from ..config.logging import setup_logging
from ..core.middleware import LoggingMiddleware, SecurityHeadersMiddleware
from ..core.exceptions import CustomException
from ..core.error_codes import ErrorCode

logger = setup_logging()


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="基于FastAPI和ROS2的机器人巡检系统",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # 添加中间件
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
        allow_credentials=True,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # 全局异常处理器
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        """自定义异常处理器"""
        logger.error(
            f"CustomException: {exc.code} - {exc.message}",
            extra={
                "request_id": getattr(request.state, 'request_id', None),
                "path": request.url.path,
                "method": request.method,
                "details": exc.details
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """FastAPI HTTPException处理器"""
        logger.warning(
            f"HTTPException: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": getattr(request.state, 'request_id', None),
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        # 将HTTPException转换为统一格式
        if exc.status_code == 401:
            code = ErrorCode.TOKEN_ERROR
        elif exc.status_code == 403:
            code = ErrorCode.PERMISSION_DENIED
        elif exc.status_code == 404:
            code = ErrorCode.RESOURCE_NOT_FOUND
        elif exc.status_code == 400:
            code = ErrorCode.PARAMETER_ERROR
        else:
            code = ErrorCode.SYSTEM_ERROR
            
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": code,
                "message": exc.detail,
                "details": {},
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求数据验证异常处理器"""
        # 提取第一个错误信息，简化显示
        first_error = exc.errors()[0] if exc.errors() else {}
        field_path = " -> ".join(str(loc) for loc in first_error.get("loc", []))
        error_msg = first_error.get("msg", "数据验证失败")
        
        # 简化错误信息
        if "时间格式必须为" in error_msg:
            error_message = f"{field_path}: 时间格式必须为 YYYY-MM-DDTHH:MM:SS"
        else:
            error_message = f"{field_path}: {error_msg}"
        
        logger.warning(
            f"ValidationError: {error_message}",
            extra={
                "request_id": getattr(request.state, 'request_id', None),
                "path": request.url.path,
                "method": request.method,
                "validation_errors": exc.errors()
            }
        )
        
        return JSONResponse(
            status_code=400,
            content={
                "code": ErrorCode.REQUEST_DATA_ERROR,
                "message": error_message,
                "details": {},
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """数据库异常处理器"""
        logger.error(
            f"Database Error: {str(exc)}",
            extra={
                "request_id": getattr(request.state, 'request_id', None),
                "path": request.url.path,
                "method": request.method,
            },
            exc_info=True
        )
        
        # 生产环境不暴露具体的数据库错误信息
        if settings.DEBUG:
            message = f"数据库错误: {str(exc)}"
        else:
            message = "数据库操作失败，请稍后重试"
        
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.SYSTEM_ERROR,
                "message": message,
                "details": {},
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器 - 兜底处理所有未捕获的异常"""
        logger.error(
            f"Unhandled Exception: {type(exc).__name__}: {str(exc)}",
            extra={
                "request_id": getattr(request.state, 'request_id', None),
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc() if settings.DEBUG else None
            },
            exc_info=True
        )
        
        # 生产环境不暴露具体的错误信息
        if settings.DEBUG:
            message = f"系统异常: {type(exc).__name__}: {str(exc)}"
            details = {"traceback": traceback.format_exc()}
        else:
            message = "系统异常，请稍后重试"
            details = {}
        
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.SYSTEM_ERROR,
                "message": message,
                "details": details,
            }
        )
    
    return app


def setup_lifespan_events(app: FastAPI):
    """设置应用生命周期事件"""
    from contextlib import asynccontextmanager
    from ..config.database import init_database, close_database
    from ..ros import ROS2Bridge
    from ..websocket import ConnectionManager, WebSocketHandler
    
    # 全局实例
    ros2_bridge = None
    connection_manager = None
    websocket_handler = None
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal ros2_bridge, connection_manager, websocket_handler
        
        # 启动时执行
        logger.info("应用启动中...")
        
        # 初始化数据库
        await init_database()
        logger.info("数据库初始化完成")
        
        # 初始化WebSocket连接管理器
        connection_manager = ConnectionManager()
        logger.info("WebSocket连接管理器初始化完成")
        
        # 初始化ROS2 Bridge
        try:
            import rclpy
            if not rclpy.ok():
                rclpy.init()
            ros2_bridge = ROS2Bridge()
            logger.info("ROS2 Bridge初始化完成")
        except Exception as e:
            logger.warning(f"ROS2 Bridge初始化失败: {e}")
            ros2_bridge = None
        
        # 初始化WebSocket处理器
        websocket_handler = WebSocketHandler(connection_manager, ros2_bridge)
        logger.info("WebSocket处理器初始化完成")
        
        # 将实例存储到app.state中，供其他模块使用
        app.state.ros2_bridge = ros2_bridge
        app.state.connection_manager = connection_manager
        app.state.websocket_handler = websocket_handler
        
        yield
        
        # 关闭时执行
        logger.info("应用关闭中...")
        
        # 关闭WebSocket连接
        if connection_manager:
            await connection_manager.broadcast_json({
                "type": "server_shutdown",
                "message": "服务器正在关闭"
            })
            logger.info("WebSocket连接已关闭")
        
        # 关闭ROS2 Bridge
        if ros2_bridge:
            try:
                ros2_bridge.stop_spin()  # 先停止spin线程
                ros2_bridge.destroy_node()
                if rclpy.ok():
                    rclpy.shutdown()
                logger.info("ROS2 Bridge已关闭")
            except Exception as e:
                logger.error(f"关闭ROS2 Bridge失败: {e}")
        
        # 关闭Redis连接（如果启用）
        try:
            from ..config.redis import close_redis_connection
            await close_redis_connection()
        except Exception as e:
            logger.warning(f"关闭Redis连接时出错: {e}")
        
        # 关闭数据库
        await close_database()
        logger.info("应用关闭完成")
    
    app.router.lifespan_context = lifespan
