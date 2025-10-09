"""
日志业务逻辑层
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

from ..repositories.log_repository import LogRepository
from ..schemas.log import LogQuery, LogContentQuery, LogDownloadRequest
from ..core.exceptions import ResourceNotFoundError, ValidationError, SystemError
from ..utils.response import ApiResponse
from ..config.logging import get_logger

logger = get_logger(__name__)


class LogService:
    """日志业务逻辑服务"""
    
    def __init__(self):
        self.log_repo = LogRepository()
    
    async def get_log_files(self, query: LogQuery) -> Dict[str, Any]:
        """获取日志文件列表"""
        try:
            # 设置默认日期范围（如果未提供）
            end_date = query.end_date or date.today()
            start_date = query.start_date or (end_date - timedelta(days=7))  # 默认查询最近7天
            
            logger.info(
                "查询日志文件列表",
                extra={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "log_type": query.log_type,
                    "page": query.page,
                    "size": query.size
                }
            )
            
            # 获取日期范围内的日志文件
            all_files = self.log_repo.get_log_files_in_range(start_date, end_date, query.log_type)
            
            # 分页处理
            total = len(all_files)
            start_idx = (query.page - 1) * query.size
            end_idx = start_idx + query.size
            files = all_files[start_idx:end_idx]
            
            return ApiResponse.paginated(
                items=files,
                total=total,
                page=query.page,
                size=query.size
            )
        
        except Exception as e:
            logger.error(
                f"获取日志文件列表失败: {str(e)}",
                extra={
                    "query": query.dict(),
                    "error": str(e)
                },
                exc_info=True
            )
            raise SystemError(f"获取日志文件列表失败: {str(e)}")
    
    async def get_log_content(self, query: LogContentQuery) -> Dict[str, Any]:
        """获取日志文件内容"""
        try:
            logger.info(
                "读取日志文件内容",
                extra={
                    "log_date": str(query.log_date),
                    "log_type": query.log_type,
                    "start_line": query.start_line,
                    "limit": query.limit,
                    "search_keyword": query.search_keyword
                }
            )
            
            content_data = self.log_repo.read_log_content(
                query.log_date,
                query.log_type,
                query.start_line,
                query.limit,
                query.search_keyword
            )
            
            if not content_data["content"]:
                raise ResourceNotFoundError(f"日志文件不存在或无内容: {query.log_date} - {query.log_type}")
            
            return ApiResponse.success(
                data=content_data,
                message="日志内容获取成功"
            )
        
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"读取日志内容失败: {str(e)}",
                extra={
                    "query": query.dict(),
                    "error": str(e)
                },
                exc_info=True
            )
            raise SystemError(f"读取日志内容失败: {str(e)}")
    
    async def get_log_file_path(self, request: LogDownloadRequest) -> Dict[str, Any]:
        """获取日志文件路径和信息用于下载"""
        try:
            log_files = self.log_repo.get_log_files_by_date(request.log_date)
            
            if request.log_type not in log_files:
                raise ResourceNotFoundError(f"日志文件不存在: {request.log_date} - {request.log_type}")
            
            file_path = log_files[request.log_type]
            
            # 检查文件是否可读
            if not file_path.exists() or not file_path.is_file():
                raise ResourceNotFoundError(f"日志文件不可访问: {file_path}")
            
            file_stat = file_path.stat()
            
            logger.info(
                "准备下载日志文件",
                extra={
                    "log_date": str(request.log_date),
                    "log_type": request.log_type,
                    "file_path": str(file_path),
                    "file_size": file_stat.st_size
                }
            )
            
            return {
                "file_path": file_path,
                "file_size": file_stat.st_size,
                "filename": file_path.name
            }
        
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"获取日志文件路径失败: {str(e)}",
                extra={
                    "request": request.dict(),
                    "error": str(e)
                },
                exc_info=True
            )
            raise SystemError(f"获取日志文件路径失败: {str(e)}")
    
    async def get_log_stats(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        try:
            logger.info("获取日志统计信息")
            
            stats = self.log_repo.get_log_stats()
            
            return ApiResponse.success(
                data=stats,
                message="日志统计信息获取成功"
            )
        
        except Exception as e:
            logger.error(
                f"获取日志统计信息失败: {str(e)}",
                extra={"error": str(e)},
                exc_info=True
            )
            raise SystemError(f"获取日志统计信息失败: {str(e)}")
    
    async def search_logs_by_keyword(self, keyword: str, start_date: date, 
                                   end_date: date, log_type: str = "app") -> Dict[str, Any]:
        """在指定日期范围内搜索日志内容"""
        try:
            if not keyword or not keyword.strip():
                raise ValidationError("搜索关键词不能为空")
            
            keyword = keyword.strip()
            
            logger.info(
                "搜索日志内容",
                extra={
                    "keyword": keyword,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "log_type": log_type
                }
            )
            
            search_results = []
            current_date = start_date
            
            while current_date <= end_date:
                content_data = self.log_repo.read_log_content(
                    current_date, log_type, 1, 10000, keyword  # 大范围搜索
                )
                
                if content_data["content"]:
                    search_results.append({
                        "date": str(current_date),
                        "matches": len(content_data["content"]),
                        "content": content_data["content"][:50]  # 限制返回前50条匹配
                    })
                
                current_date += timedelta(days=1)
            
            total_matches = sum(result["matches"] for result in search_results)
            
            return ApiResponse.success(
                data={
                    "keyword": keyword,
                    "search_results": search_results,
                    "total_matches": total_matches,
                    "search_dates": f"{start_date} 到 {end_date}"
                },
                message=f"搜索完成，共找到 {total_matches} 条匹配记录"
            )
        
        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                f"搜索日志失败: {str(e)}",
                extra={
                    "keyword": keyword,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "log_type": log_type,
                    "error": str(e)
                },
                exc_info=True
            )
            raise SystemError(f"搜索日志失败: {str(e)}")
    
    async def cleanup_old_logs(self, days_to_keep: int, operator: dict) -> Dict[str, Any]:
        """清理旧日志文件"""
        try:
            if days_to_keep < 1:
                raise ValidationError("保留天数必须大于0")
            
            logger.info(
                "开始清理旧日志",
                extra={
                    "days_to_keep": days_to_keep,
                    "operator": operator["username"]
                }
            )
            
            from ..config.logging import cleanup_old_logs
            
            # 执行清理
            cleanup_old_logs(days_to_keep)
            
            # 获取清理后的统计信息
            stats = self.log_repo.get_log_stats()
            
            logger.info(
                "日志清理完成",
                extra={
                    "days_to_keep": days_to_keep,
                    "remaining_dirs": stats["total_dirs"],
                    "remaining_size_mb": stats["total_size_mb"],
                    "operator": operator["username"]
                }
            )
            
            return ApiResponse.success(
                data={
                    "days_to_keep": days_to_keep,
                    "remaining_stats": stats
                },
                message=f"日志清理完成，保留最近 {days_to_keep} 天的日志"
            )
        
        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                f"清理日志失败: {str(e)}",
                extra={
                    "days_to_keep": days_to_keep,
                    "operator": operator["username"],
                    "error": str(e)
                },
                exc_info=True
            )
            raise SystemError(f"清理日志失败: {str(e)}")
