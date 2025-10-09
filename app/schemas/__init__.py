"""
Pydantic模式模块
"""

from .base import BaseSchema, TimestampMixin
from .user import UserCreate, UserUpdate, UserPasswordUpdate, UserResponse, UserLogin, UserListResponse
from .session import SessionCreate, SessionResponse
from .map import MapCreate, MapUpdate, MapResponse, MapQuery, MapListResponse
from .mapnet import MapNetType, MapNetCreate, MapNetUpdate, MapNetResponse, MapNetQuery, MapNetListResponse
from .robot import RobotCreate, RobotUpdate, RobotResponse, RobotQuery, RobotListResponse
from .point import PointCreate, PointUpdate, PointResponse, PointQuery, PointListResponse
from .task import TaskCreate, TaskUpdate, TaskResponse, TaskQuery, TaskListResponse
from .taskschedule import TaskScheduleCreate, TaskScheduleUpdate, TaskScheduleResponse, TaskScheduleQuery, TaskScheduleListResponse
from .taskhistory import TaskHistoryCreate, TaskHistoryUpdate, TaskHistoryResponse, TaskHistoryQuery, TaskHistoryListResponse

__all__ = [
    "BaseSchema",
    "TimestampMixin",
    "UserCreate",
    "UserUpdate",
    "UserPasswordUpdate",
    "UserResponse",
    "UserLogin",
    "UserListResponse",
    "SessionCreate",
    "SessionResponse",
    "MapCreate",
    "MapUpdate",
    "MapResponse",
    "MapQuery",
    "MapListResponse",
    "MapNetType",
    "MapNetCreate",
    "MapNetUpdate",
    "MapNetResponse",
    "MapNetQuery",
    "MapNetListResponse",
    "RobotCreate",
    "RobotUpdate",
    "RobotResponse",
    "RobotQuery",
    "RobotListResponse",
    "PointCreate",
    "PointUpdate",
    "PointResponse",
    "PointQuery",
    "PointListResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskQuery",
    "TaskListResponse",
    "TaskScheduleCreate",
    "TaskScheduleUpdate",
    "TaskScheduleResponse",
    "TaskScheduleQuery",
    "TaskScheduleListResponse",
    "TaskHistoryCreate",
    "TaskHistoryUpdate",
    "TaskHistoryResponse",
    "TaskHistoryQuery",
    "TaskHistoryListResponse",
]