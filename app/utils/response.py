"""
统一响应工具 - 使用统一错误码规范
"""

from typing import Any, Dict, List, Optional
from fastapi.responses import JSONResponse
from fastapi import status
from ..core.error_codes import ErrorCode, ErrorMessage


class ApiResponse:
    """API响应工具类"""
    
    @staticmethod
    def success(
        data: Optional[Any] = None, 
        message: Optional[str] = None,
        code: int = ErrorCode.SUCCESS
    ) -> Dict[str, Any]:
        """
        构建成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: 业务状态码
        
        Returns:
            标准格式的响应字典
        """
        response = {
            "code": code,
            "message": message or ErrorMessage.get_message(code),
        }
        
        if data is not None:
            response["data"] = data
            
        return response
    
    @staticmethod
    def error(
        code: int,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        构建错误响应
        
        Args:
            code: 错误码
            message: 错误消息
            details: 错误详情
        
        Returns:
            标准格式的错误响应字典
        """
        response = {
            "code": code,
            "message": message or ErrorMessage.get_message(code),
        }
        
        if details:
            response["details"] = details
            
        return response
    
    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int,
        size: int,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        构建分页响应
        
        Args:
            items: 数据列表
            total: 总数量
            page: 当前页码
            size: 每页大小
            message: 响应消息
        
        Returns:
            标准格式的分页响应
        """
        data = {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
                "has_next": (page * size) < total,
                "has_prev": page > 1,
            }
        }
        
        return ApiResponse.success(
            data=data,
            message=message or "获取成功"
        )


def success_response(
    data: Optional[Any] = None, 
    message: Optional[str] = None, 
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    构建一个标准的成功响应
    """
    content = ApiResponse.success(data=data, message=message)
    return JSONResponse(status_code=status_code, content=content)


def error_response(
    code: int,
    message: Optional[str] = None, 
    status_code: Optional[int] = None,
    details: Optional[Any] = None
) -> JSONResponse:
    """
    构建一个标准的错误响应
    """
    from ..core.error_codes import get_http_status_code
    
    if status_code is None:
        status_code = get_http_status_code(code)
    
    content = ApiResponse.error(code=code, message=message, details=details)
    return JSONResponse(status_code=status_code, content=content)


def pagination_response(
    items: List[Any], 
    total: int, 
    page: int, 
    size: int, 
    message: Optional[str] = None
) -> JSONResponse:
    """
    构建一个标准的分页响应
    """
    content = ApiResponse.paginated(
        items=items,
        total=total,
        page=page,
        size=size,
        message=message
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)