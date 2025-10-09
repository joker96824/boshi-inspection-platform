"""
中间件
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse

from ..config.settings import settings
from ..config.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> StarletteResponse:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息（只记录非健康检查请求）
        if not request.url.path.endswith('/health'):
            logger.info(
                "请求开始",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": request.client.host if request.client else None,
                }
            )
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息（只记录非健康检查请求）
            if not request.url.path.endswith('/health'):
                logger.info(
                    "请求完成",
                    extra={
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "process_time": round(process_time, 4),
                    }
                )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录错误信息
            logger.error(
                "请求失败",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": round(process_time, 4),
                },
                exc_info=True
            )
            
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests = {}
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> StarletteResponse:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 清理过期的请求记录
        self.requests = {
            ip: requests for ip, requests in self.requests.items()
            if any(req_time > current_time - self.period for req_time in requests)
        }
        
        # 检查当前IP的请求次数
        if client_ip in self.requests:
            recent_requests = [
                req_time for req_time in self.requests[client_ip]
                if req_time > current_time - self.period
            ]
            if len(recent_requests) >= self.calls:
                logger.warning(
                    "请求频率过高",
                    extra={
                        "client_ip": client_ip,
                        "request_count": len(recent_requests),
                        "limit": self.calls,
                    }
                )
                return StarletteResponse(
                    content="请求频率过高，请稍后再试",
                    status_code=429,
                    headers={"Retry-After": str(self.period)}
                )
        else:
            self.requests[client_ip] = []
        
        # 记录当前请求
        self.requests[client_ip].append(current_time)
        
        # 处理请求
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> StarletteResponse:
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 根据环境设置不同的 CSP 策略
        if settings.DEBUG:
            # 开发模式：允许外部资源（用于 Swagger UI）
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' https://cdn.jsdelivr.net"
            )
        else:
            # 生产模式：严格的 CSP
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


# CORS中间件配置
def get_cors_middleware():
    """获取CORS中间件"""
    return FastAPICORSMiddleware(
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )
