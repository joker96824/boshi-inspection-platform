"""
任务状态常量定义
"""

from enum import Enum


class TaskStatus(str, Enum):
    """任务执行状态枚举"""
    RUNNING = "running"      # 执行中
    PAUSED = "paused"        # 已暂停
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 执行失败
    CANCELLED = "cancelled"  # 已取消

    @classmethod
    def get_all_statuses(cls) -> list[str]:
        """获取所有状态值列表"""
        return [status.value for status in cls]

    @classmethod
    def is_valid(cls, status: str) -> bool:
        """检查状态值是否有效"""
        return status in cls.get_all_statuses()

    @classmethod
    def get_status_display(cls, status: str) -> str:
        """获取状态显示文本"""
        status_map = {
            cls.RUNNING: "执行中",
            cls.PAUSED: "已暂停",
            cls.COMPLETED: "已完成",
            cls.FAILED: "执行失败",
            cls.CANCELLED: "已取消",
        }
        return status_map.get(status, status)

