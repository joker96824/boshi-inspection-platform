"""
任务日程Pydantic模式
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import date, time
from pydantic import Field, validator
from .base import BaseSchema, BaseResponse


class TaskScheduleBase(BaseSchema):
    """任务日程基础模式"""
    task_id: str = Field(..., description="关联的任务ID")
    schedule_name: str = Field(..., min_length=1, max_length=200, description="日程名称")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    enabled: bool = Field(True, description="启用状态：0-禁用，1-启用")
    item_count: int = Field(0, ge=0, description="关联的巡检项目数量")
    
    # 执行周期配置
    cycle_type: str = Field(..., description="周期类型：daily/monthly_days/weekly/interval")
    cycle_config: Optional[Dict[str, Any]] = Field(None, description="周期详细配置（JSON格式）")
    
    # 执行时间配置
    time_mode: str = Field(..., description="时间模式：custom/interval")
    time_config: Dict[str, Any] = Field(..., description="时间详细配置（JSON格式）")
    
    # 用于显示的简化字段
    frequency_display: Optional[str] = Field(None, max_length=200, description="周期显示文本")
    time_display_start: Optional[time] = Field(None, description="开始时间（用于时间轴显示）")
    time_display_end: Optional[time] = Field(None, description="结束时间（用于时间轴显示）")
    
    @validator('cycle_type')
    def validate_cycle_type(cls, v):
        """验证周期类型"""
        allowed_types = ['daily', 'monthly_days', 'weekly', 'interval']
        if v not in allowed_types:
            raise ValueError(f'cycle_type must be one of {allowed_types}')
        return v
    
    @validator('time_mode')
    def validate_time_mode(cls, v):
        """验证时间模式"""
        allowed_modes = ['custom', 'interval']
        if v not in allowed_modes:
            raise ValueError(f'time_mode must be one of {allowed_modes}')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """验证结束日期必须大于等于开始日期"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be greater than or equal to start_date')
        return v
    
    @validator('time_config')
    def validate_time_config(cls, v, values):
        """验证时间配置"""
        if 'time_mode' not in values:
            return v
        
        time_mode = values['time_mode']
        if time_mode == 'custom':
            if 'customTimes' not in v or not isinstance(v['customTimes'], list):
                raise ValueError('custom mode requires customTimes list in time_config')
        elif time_mode == 'interval':
            if 'intervalTimeRange' not in v or 'intervalMinutes' not in v:
                raise ValueError('interval mode requires intervalTimeRange and intervalMinutes in time_config')
        return v


class TaskScheduleCreate(TaskScheduleBase):
    """任务日程创建模式"""
    pass


class TaskScheduleUpdate(BaseSchema):
    """任务日程更新模式"""
    schedule_name: Optional[str] = Field(None, min_length=1, max_length=200, description="日程名称")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    enabled: Optional[bool] = Field(None, description="启用状态：0-禁用，1-启用")
    item_count: Optional[int] = Field(None, ge=0, description="关联的巡检项目数量")
    cycle_type: Optional[str] = Field(None, description="周期类型：daily/monthly_days/weekly/interval")
    cycle_config: Optional[Dict[str, Any]] = Field(None, description="周期详细配置（JSON格式）")
    time_mode: Optional[str] = Field(None, description="时间模式：custom/interval")
    time_config: Optional[Dict[str, Any]] = Field(None, description="时间详细配置（JSON格式）")
    frequency_display: Optional[str] = Field(None, max_length=200, description="周期显示文本")
    time_display_start: Optional[time] = Field(None, description="开始时间（用于时间轴显示）")
    time_display_end: Optional[time] = Field(None, description="结束时间（用于时间轴显示）")


class TaskScheduleResponse(BaseResponse):
    """任务日程响应模式"""
    task_id: str = Field(..., description="关联的任务ID")
    schedule_name: str = Field(..., description="日程名称")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    enabled: bool = Field(..., description="启用状态：0-禁用，1-启用")
    item_count: int = Field(..., description="关联的巡检项目数量")
    cycle_type: str = Field(..., description="周期类型：daily/monthly_days/weekly/interval")
    cycle_config: Optional[Dict[str, Any]] = Field(None, description="周期详细配置（JSON格式）")
    time_mode: str = Field(..., description="时间模式：custom/interval")
    time_config: Dict[str, Any] = Field(..., description="时间详细配置（JSON格式）")
    frequency_display: Optional[str] = Field(None, description="周期显示文本")
    time_display_start: Optional[time] = Field(None, description="开始时间（用于时间轴显示）")
    time_display_end: Optional[time] = Field(None, description="结束时间（用于时间轴显示）")


class TaskScheduleQuery(BaseSchema):
    """任务日程查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    task_id: Optional[str] = Field(None, description="任务ID")
    cycle_type: Optional[str] = Field(None, description="周期类型")
    enabled: Optional[bool] = Field(None, description="启用状态")


class TaskScheduleListResponse(BaseSchema):
    """任务日程列表响应模式"""
    items: List[TaskScheduleResponse] = Field(..., description="任务日程列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class TaskScheduleFrontendCreate(BaseSchema):
    """前端任务日程创建模式（前端格式）"""
    task_id: str = Field(..., description="关联的任务ID")
    schedule_name: str = Field(..., min_length=1, max_length=200, description="日程名称")
    dateRange: List[str] = Field(..., min_items=2, max_items=2, description="日期范围：[开始日期, 结束日期]")
    enabled: bool = Field(True, description="启用状态")
    item_count: int = Field(0, ge=0, description="关联的巡检项目数量")
    
    # 周期配置（前端格式）
    cycle: str = Field(..., description="周期类型：每天/日/周/间隔")
    selectedDays: Optional[List[int]] = Field(None, description="选中的日期（日模式）")
    selectedWeeks: Optional[List[int]] = Field(None, description="选中的星期（周模式，1-7）")
    intervalDays: Optional[int] = Field(None, ge=1, description="间隔天数（间隔模式）")
    
    # 时间配置（前端格式）
    timeMode: str = Field(..., description="时间模式：自定义/间隔")
    customTimes: Optional[List[str]] = Field(None, description="自定义时间列表（自定义模式）")
    intervalTimeRange: Optional[List[str]] = Field(None, min_items=2, max_items=2, description="时间范围（间隔模式）：[开始时间, 结束时间]")
    intervalMinutes: Optional[int] = Field(None, ge=1, description="间隔分钟数（间隔模式）")
    
    @validator('cycle')
    def validate_cycle(cls, v):
        """验证周期类型"""
        allowed_cycles = ['每天', '日', '周', '间隔']
        if v not in allowed_cycles:
            raise ValueError(f'cycle must be one of {allowed_cycles}')
        return v
    
    @validator('timeMode')
    def validate_time_mode(cls, v):
        """验证时间模式"""
        allowed_modes = ['自定义', '间隔']
        if v not in allowed_modes:
            raise ValueError(f'timeMode must be one of {allowed_modes}')
        return v
    
    def to_backend_format(self) -> Dict[str, Any]:
        """将前端格式转换为后端格式"""
        from datetime import date, time as time_type
        
        # 转换周期类型
        cycle_mapping = {
            '每天': 'daily',
            '日': 'monthly_days',
            '周': 'weekly',
            '间隔': 'interval'
        }
        cycle_type = cycle_mapping[self.cycle]
        
        # 构建 cycle_config
        cycle_config = None
        if cycle_type == 'monthly_days' and self.selectedDays:
            cycle_config = {"selectedDays": self.selectedDays}
        elif cycle_type == 'weekly' and self.selectedWeeks:
            cycle_config = {"selectedWeeks": self.selectedWeeks}
        elif cycle_type == 'interval' and self.intervalDays:
            cycle_config = {"intervalDays": self.intervalDays}
        
        # 转换时间模式
        time_mode_mapping = {
            '自定义': 'custom',
            '间隔': 'interval'
        }
        time_mode = time_mode_mapping[self.timeMode]
        
        # 构建 time_config
        time_config = {}
        if time_mode == 'custom' and self.customTimes:
            time_config = {"customTimes": self.customTimes}
        elif time_mode == 'interval' and self.intervalTimeRange and self.intervalMinutes:
            time_config = {
                "intervalTimeRange": self.intervalTimeRange,
                "intervalMinutes": self.intervalMinutes
            }
        
        # 解析日期范围
        start_date = date.fromisoformat(self.dateRange[0]) if self.dateRange and len(self.dateRange) > 0 else None
        end_date = date.fromisoformat(self.dateRange[1]) if self.dateRange and len(self.dateRange) > 1 else None
        
        # 计算显示字段
        frequency_display = self._calculate_frequency_display(cycle_type, cycle_config)
        time_display_start, time_display_end = self._calculate_time_display(time_config)
        
        return {
            "task_id": self.task_id,
            "schedule_name": self.schedule_name,
            "start_date": start_date,
            "end_date": end_date,
            "enabled": self.enabled,
            "item_count": self.item_count,
            "cycle_type": cycle_type,
            "cycle_config": cycle_config,
            "time_mode": time_mode,
            "time_config": time_config,
            "frequency_display": frequency_display,
            "time_display_start": time_display_start,
            "time_display_end": time_display_end,
        }
    
    @staticmethod
    def _calculate_frequency_display(cycle_type: str, cycle_config: Optional[Dict[str, Any]]) -> str:
        """计算周期显示文本"""
        if cycle_type == 'daily':
            return '每天'
        elif cycle_type == 'monthly_days' and cycle_config and 'selectedDays' in cycle_config:
            days = cycle_config['selectedDays']
            days_str = '、'.join([str(d) for d in sorted(days)])
            return f'每月{days_str}日'
        elif cycle_type == 'weekly' and cycle_config and 'selectedWeeks' in cycle_config:
            week_names = ['一', '二', '三', '四', '五', '六', '日']
            weeks = [week_names[w-1] for w in sorted(cycle_config['selectedWeeks']) if 1 <= w <= 7]
            weeks_str = '、'.join([f'周{w}' for w in weeks])
            return f'每{weeks_str}'
        elif cycle_type == 'interval' and cycle_config and 'intervalDays' in cycle_config:
            days = cycle_config['intervalDays']
            return f'每{days}天'
        return ''
    
    @staticmethod
    def _calculate_time_display(time_config: Dict[str, Any]) -> Tuple[Optional[time], Optional[time]]:
        """计算时间显示字段"""
        
        if not time_config:
            return None, None
        
        if 'customTimes' in time_config and time_config['customTimes']:
            times = time_config['customTimes']
            if times:
                first_time_str = times[0]
                last_time_str = times[-1]
                try:
                    first_time = time.fromisoformat(first_time_str + ':00' if len(first_time_str) == 5 else first_time_str)
                    last_time = time.fromisoformat(last_time_str + ':00' if len(last_time_str) == 5 else last_time_str)
                    return first_time, last_time
                except:
                    return None, None
        
        if 'intervalTimeRange' in time_config and time_config['intervalTimeRange']:
            time_range = time_config['intervalTimeRange']
            if len(time_range) >= 2:
                try:
                    start_time = time.fromisoformat(time_range[0] + ':00' if len(time_range[0]) == 5 else time_range[0])
                    end_time = time.fromisoformat(time_range[1] + ':00' if len(time_range[1]) == 5 else time_range[1])
                    return start_time, end_time
                except:
                    return None, None
        
        return None, None
