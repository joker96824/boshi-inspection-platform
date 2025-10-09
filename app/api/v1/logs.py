"""
日志管理API接口
"""

from datetime import date
from pathlib import Path
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io
import tempfile
import shutil
import logging

from ...core.deps import get_db
from ...core.permissions import require_admin, get_current_user
from ...services.log_service import LogService
from ...schemas.log import LogQuery, LogContentQuery, LogDownloadRequest
from ...core.exceptions import ValidationError
from ...config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/files", response_model=dict)
async def get_log_files(
    start_date: date = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: date = Query(None, description="结束日期 (YYYY-MM-DD)"),
    log_type: str = Query("app", description="日志类型: app/error/debug/all"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(require_admin)
):
    """获取日志文件列表
    
    权限要求：admin 及以上
    
    Args:
        start_date: 开始日期，默认为7天前
        end_date: 结束日期，默认为今天
        log_type: 日志类型
        page: 页码
        size: 每页数量
        current_user: 当前用户
    
    Returns:
        日志文件列表
    """
    query_data = LogQuery(
        start_date=start_date,
        end_date=end_date,
        log_type=log_type,
        page=page,
        size=size
    )
    
    log_service = LogService()
    return await log_service.get_log_files(query_data)


@router.get("/content", response_model=dict)
async def get_log_content(
    log_date: date = Query(..., description="日志日期 (YYYY-MM-DD)"),
    log_type: str = Query("app", description="日志类型: app/error/debug"),
    start_line: int = Query(1, ge=1, description="开始行号"),
    limit: int = Query(100, ge=1, le=1000, description="读取行数"),
    search_keyword: str = Query(None, description="搜索关键词"),
    current_user: dict = Depends(require_admin)
):
    """获取日志文件内容
    
    权限要求：admin 及以上
    
    Args:
        log_date: 日志日期
        log_type: 日志类型
        start_line: 开始行号
        limit: 读取行数
        search_keyword: 搜索关键词（可选）
        current_user: 当前用户
    
    Returns:
        日志文件内容
    """
    query_data = LogContentQuery(
        log_date=log_date,
        log_type=log_type,
        start_line=start_line,
        limit=limit,
        search_keyword=search_keyword
    )
    
    log_service = LogService()
    return await log_service.get_log_content(query_data)


@router.get("/download")
async def download_log_file(
    log_date: date = Query(..., description="日志日期 (YYYY-MM-DD)"),
    log_type: str = Query("app", description="日志类型: app/error/debug"),
    current_user: dict = Depends(require_admin)
):
    """下载日志文件
    
    权限要求：admin 及以上
    
    策略：创建文件快照副本避免下载过程中文件被修改
    
    Args:
        log_date: 日志日期
        log_type: 日志类型
        current_user: 当前用户
    
    Returns:
        日志文件下载
    """
    download_request = LogDownloadRequest(
        log_date=log_date,
        log_type=log_type
    )
    
    log_service = LogService()
    file_info = await log_service.get_log_file_path(download_request)
    
    file_path = file_info["file_path"]
    
    # 构建下载文件名
    filename = f"boshi_inspection_{log_date}_{log_type}.log"
    
    # 创建文件快照副本，避免下载过程中文件被修改
    with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as temp_file:
        temp_path = Path(temp_file.name)
        
        # 复制文件到临时位置（原子操作）
        shutil.copy2(file_path, temp_path)
    
    # 使用快照文件进行下载
    def file_generator():
        try:
            with open(temp_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            # 这里不能使用logger，因为可能导致递归问题
            print(f"读取快照文件失败: {e}")
            raise
        finally:
            # 清理临时文件
            try:
                temp_path.unlink()
            except:
                pass
    
    return StreamingResponse(
        file_generator(),
        media_type='text/plain',
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )


@router.get("/stats", response_model=dict)
async def get_log_stats(
    current_user: dict = Depends(require_admin)
):
    """获取日志统计信息
    
    权限要求：admin 及以上
    
    Args:
        current_user: 当前用户
    
    Returns:
        日志统计信息
    """
    log_service = LogService()
    return await log_service.get_log_stats()


@router.post("/search", response_model=dict)
async def search_logs(
    keyword: str = Query(..., description="搜索关键词"),
    start_date: date = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="结束日期 (YYYY-MM-DD)"),
    log_type: str = Query("app", description="日志类型: app/error/debug"),
    current_user: dict = Depends(require_admin)
):
    """在日志中搜索关键词
    
    权限要求：admin 及以上
    
    Args:
        keyword: 搜索关键词
        start_date: 开始日期
        end_date: 结束日期
        log_type: 日志类型
        current_user: 当前用户
    
    Returns:
        搜索结果
    """
    log_service = LogService()
    return await log_service.search_logs_by_keyword(keyword, start_date, end_date, log_type)


@router.post("/cleanup", response_model=dict)
async def cleanup_old_logs(
    days_to_keep: int = Query(7, ge=1, le=365, description="保留天数"),
    current_user: dict = Depends(require_admin)
):
    """清理旧日志文件
    
    权限要求：admin 及以上
    
    Args:
        days_to_keep: 保留最近几天的日志
        current_user: 当前用户
    
    Returns:
        清理结果
    """
    log_service = LogService()
    return await log_service.cleanup_old_logs(days_to_keep, current_user)
