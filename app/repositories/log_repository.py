"""
日志数据访问层
"""

import os
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Any
from ..config.logging import get_logger

logger = get_logger(__name__)


class LogRepository:
    """日志数据访问层"""
    
    def __init__(self):
        self.base_log_dir = Path("logs")
    
    def get_log_directories(self) -> List[str]:
        """获取所有日志目录（按日期）"""
        if not self.base_log_dir.exists():
            return []
        
        directories = []
        for item in self.base_log_dir.iterdir():
            if item.is_dir() and self._is_valid_date_dir(item.name):
                directories.append(item.name)
        
        return sorted(directories, reverse=True)  # 最新的在前面
    
    def get_log_files_by_date(self, log_date: date) -> Dict[str, Path]:
        """根据日期获取日志文件路径"""
        date_str = log_date.strftime("%Y-%m-%d")
        date_dir = self.base_log_dir / date_str
        
        if not date_dir.exists():
            return {}
        
        log_files = {}
        # 定义日志文件名映射
        log_file_mapping = {
            'app': 'app.log',
            'error': 'error.log', 
            'debug': 'debug.log'
        }
        
        for log_type in ['app', 'error', 'debug']:
            log_file = date_dir / log_file_mapping[log_type]
            if log_file.exists():
                log_files[log_type] = log_file
        
        return log_files
    
    def get_log_file_info(self, log_date: date, log_type: str) -> Optional[Dict[str, Any]]:
        """获取日志文件详细信息"""
        log_files = self.get_log_files_by_date(log_date)
        
        if log_type not in log_files:
            return None
        
        log_file = log_files[log_type]
        stat = log_file.stat()
        
        return {
            "filename": log_file.name,
            "file_path": str(log_file),
            "file_size": stat.st_size,
            "file_size_mb": round(stat.st_size / 1024 / 1024, 2),
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "log_type": log_type
        }
    
    def get_log_files_in_range(self, start_date: date, end_date: date, log_type: str = "all") -> List[Dict[str, Any]]:
        """获取日期范围内的日志文件"""
        files_info = []
        
        current_date = start_date
        while current_date <= end_date:
            if log_type == "all":
                # 获取所有类型的日志文件
                for file_type in ['app', 'error', 'debug']:
                    file_info = self.get_log_file_info(current_date, file_type)
                    if file_info:
                        files_info.append(file_info)
            else:
                # 获取指定类型的日志文件
                file_info = self.get_log_file_info(current_date, log_type)
                if file_info:
                    files_info.append(file_info)
            
            # 移动到下一天
            from datetime import timedelta
            current_date += timedelta(days=1)
        
        return files_info
    
    def read_log_content(self, log_date: date, log_type: str, start_line: int = 1, 
                        limit: int = 100, search_keyword: Optional[str] = None) -> Dict[str, Any]:
        """读取日志文件内容"""
        log_files = self.get_log_files_by_date(log_date)
        
        if log_type not in log_files:
            logger.warning(f"日志文件不存在: {log_date} - {log_type}")
            return {
                "content": [],
                "total_lines": 0,
                "current_start": start_line,
                "current_end": start_line,
                "has_more": False
            }
        
        log_file = log_files[log_type]
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            total_lines = len(all_lines)
            
            # 如果有搜索关键词，先过滤
            if search_keyword:
                filtered_lines = []
                for i, line in enumerate(all_lines, 1):
                    if search_keyword.lower() in line.lower():
                        filtered_lines.append(f"Line {i}: {line.rstrip()}")
                
                # 对过滤后的结果进行分页
                start_idx = max(0, start_line - 1)
                end_idx = min(len(filtered_lines), start_idx + limit)
                content = filtered_lines[start_idx:end_idx]
                
                return {
                    "content": content,
                    "total_lines": len(filtered_lines),
                    "current_start": start_line,
                    "current_end": start_idx + len(content),
                    "has_more": end_idx < len(filtered_lines),
                    "search_keyword": search_keyword,
                    "original_total_lines": total_lines
                }
            else:
                # 正常分页读取
                start_idx = max(0, start_line - 1)
                end_idx = min(total_lines, start_idx + limit)
                content = [line.rstrip() for line in all_lines[start_idx:end_idx]]
                
                return {
                    "content": content,
                    "total_lines": total_lines,
                    "current_start": start_line,
                    "current_end": start_idx + len(content),
                    "has_more": end_idx < total_lines
                }
        
        except Exception as e:
            logger.error(
                f"读取日志文件失败: {log_file}",
                extra={
                    "log_date": str(log_date),
                    "log_type": log_type,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def get_log_stats(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        if not self.base_log_dir.exists():
            return {
                "total_dirs": 0,
                "total_size_mb": 0,
                "date_range": {},
                "log_types": {}
            }
        
        total_dirs = 0
        total_size = 0
        log_types_stats = {"app": 0, "error": 0, "debug": 0}
        dates = []
        
        for date_dir in self.base_log_dir.iterdir():
            if date_dir.is_dir() and self._is_valid_date_dir(date_dir.name):
                total_dirs += 1
                dates.append(date_dir.name)
                
                for log_file in date_dir.glob("*.log*"):
                    if log_file.is_file():
                        total_size += log_file.stat().st_size
                        
                        # 统计各类型日志文件数量
                        if "error" in log_file.name:
                            log_types_stats["error"] += 1
                        elif "debug" in log_file.name:
                            log_types_stats["debug"] += 1
                        else:
                            log_types_stats["app"] += 1
        
        dates.sort()
        date_range = {}
        if dates:
            date_range = {
                "earliest": dates[0],
                "latest": dates[-1],
                "total_days": len(dates)
            }
        
        return {
            "total_dirs": total_dirs,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "date_range": date_range,
            "log_types": log_types_stats
        }
    
    def _is_valid_date_dir(self, dirname: str) -> bool:
        """检查是否为有效的日期目录名"""
        try:
            datetime.strptime(dirname, "%Y-%m-%d")
            return True
        except ValueError:
            return False
