# 日程管理接口调用示例

本文档提供创建任务日程和云台日程的多种调用示例。

## 接口地址

- **任务日程**: `POST /api/v1/taskschedules/`
- **云台日程**: `POST /api/v1/gimbalschedules/`

## 请求格式

所有请求都需要：
- **认证**: 需要 `Authorization` header（Bearer Token）
- **Content-Type**: `application/json`

---

## 示例 1: 每天执行 + 自定义时间点（任务日程）

### 场景
每天在 08:00、14:00、20:00 执行任务

### 请求体

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440010",
  "schedule_name": "每日三次巡检",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "enabled": true,
  "item_count": 5,
  "cycle_type": "daily",
  "cycle_config": null,
  "time_mode": "custom",
  "time_config": {
    "customTimes": ["08:00", "14:00", "20:00"]
  },
  "time_display_start": "08:00:00",
  "time_display_end": "20:00:00"
}
```

### cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/taskschedules/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440010",
    "schedule_name": "每日三次巡检",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "enabled": true,
    "item_count": 5,
    "cycle_type": "daily",
    "cycle_config": null,
    "time_mode": "custom",
    "time_config": {
      "customTimes": ["08:00", "14:00", "20:00"]
    },
    "time_display_start": "08:00:00",
    "time_display_end": "20:00:00"
  }'
```

### JavaScript (Fetch) 示例

```javascript
const response = await fetch('http://localhost:8000/api/v1/taskschedules/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    task_id: '550e8400-e29b-41d4-a716-446655440010',
    schedule_name: '每日三次巡检',
    start_date: '2025-01-01',
    end_date: '2025-12-31',
    enabled: true,
    item_count: 5,
    cycle_type: 'daily',
    cycle_config: null,
    time_mode: 'custom',
    time_config: {
      customTimes: ['08:00', '14:00', '20:00']
    },
    time_display_start: '08:00:00',
    time_display_end: '20:00:00'
  })
});

const result = await response.json();
console.log(result);
```

### Python (requests) 示例

```python
import requests

url = "http://localhost:8000/api/v1/taskschedules/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "task_id": "550e8400-e29b-41d4-a716-446655440010",
    "schedule_name": "每日三次巡检",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "enabled": True,
    "item_count": 5,
    "cycle_type": "daily",
    "cycle_config": None,
    "time_mode": "custom",
    "time_config": {
        "customTimes": ["08:00", "14:00", "20:00"]
    },
    "time_display_start": "08:00:00",
    "time_display_end": "20:00:00"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## 示例 2: 每月指定日期 + 自定义时间点（任务日程）

### 场景
每月 1 日、5 日、10 日、15 日、20 日在 09:00 和 18:00 执行

### 请求体

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440010",
  "schedule_name": "每月固定日期巡检",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "enabled": true,
  "item_count": 3,
  "cycle_type": "monthly_days",
  "cycle_config": {
    "selectedDays": [1, 5, 10, 15, 20]
  },
  "time_mode": "custom",
  "time_config": {
    "customTimes": ["09:00", "18:00"]
  },
  "time_display_start": "09:00:00",
  "time_display_end": "18:00:00"
}
```

### cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/taskschedules/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440010",
    "schedule_name": "每月固定日期巡检",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "enabled": true,
    "item_count": 3,
    "cycle_type": "monthly_days",
    "cycle_config": {
      "selectedDays": [1, 5, 10, 15, 20]
    },
    "time_mode": "custom",
    "time_config": {
      "customTimes": ["09:00", "18:00"]
    },
    "time_display_start": "09:00:00",
    "time_display_end": "18:00:00"
  }'
```

---

## 示例 3: 每周指定星期 + 间隔时间（任务日程）

### 场景
每周一、三、五在 08:00-18:00 之间，每 2 小时执行一次

### 请求体

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440010",
  "schedule_name": "工作日间隔巡检",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "enabled": true,
  "item_count": 8,
  "cycle_type": "weekly",
  "cycle_config": {
    "selectedWeeks": [1, 3, 5]
  },
  "time_mode": "interval",
  "time_config": {
    "intervalTimeRange": ["08:00", "18:00"],
    "intervalMinutes": 120
  },
  "time_display_start": "08:00:00",
  "time_display_end": "18:00:00"
}
```

### JavaScript 示例

```javascript
const scheduleData = {
  task_id: '550e8400-e29b-41d4-a716-446655440010',
  schedule_name: '工作日间隔巡检',
  start_date: '2025-01-01',
  end_date: '2025-12-31',
  enabled: true,
  item_count: 8,
  cycle_type: 'weekly',
  cycle_config: {
    selectedWeeks: [1, 3, 5]  // 1=周一, 3=周三, 5=周五
  },
  time_mode: 'interval',
  time_config: {
    intervalTimeRange: ['08:00', '18:00'],
    intervalMinutes: 120  // 每 120 分钟（2小时）执行一次
  },
  time_display_start: '08:00:00',
  time_display_end: '18:00:00'
};

const response = await fetch('http://localhost:8000/api/v1/taskschedules/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(scheduleData)
});
```

---

## 示例 4: 每月指定日期 + 间隔时间（任务日程）

### 场景
每月 5 日、10 日、15 日、20 日，在这些日期的 08:00-20:00 之间，每 2 小时执行一次

### 请求体

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440010",
  "schedule_name": "每月固定日期间隔巡检",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "enabled": true,
  "item_count": 6,
  "cycle_type": "monthly_days",
  "cycle_config": {
    "selectedDays": [5, 10, 15, 20]
  },
  "time_mode": "interval",
  "time_config": {
    "intervalTimeRange": ["08:00", "20:00"],
    "intervalMinutes": 120
  },
  "time_display_start": "08:00:00",
  "time_display_end": "20:00:00"
}
```

### cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/taskschedules/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440010",
    "schedule_name": "每月固定日期间隔巡检",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "enabled": true,
    "item_count": 6,
    "cycle_type": "monthly_days",
    "cycle_config": {
      "selectedDays": [5, 10, 15, 20]
    },
    "time_mode": "interval",
    "time_config": {
      "intervalTimeRange": ["08:00", "20:00"],
      "intervalMinutes": 120
    },
    "time_display_start": "08:00:00",
    "time_display_end": "20:00:00"
  }'
```

### JavaScript 示例

```javascript
const scheduleData = {
  task_id: '550e8400-e29b-41d4-a716-446655440010',
  schedule_name: '每月固定日期间隔巡检',
  start_date: '2025-01-01',
  end_date: '2025-12-31',
  enabled: true,
  item_count: 6,
  cycle_type: 'monthly_days',
  cycle_config: {
    selectedDays: [5, 10, 15, 20]  // 每月 5、10、15、20 日
  },
  time_mode: 'interval',
  time_config: {
    intervalTimeRange: ['08:00', '20:00'],  // 08:00 到 20:00
    intervalMinutes: 120  // 每 120 分钟（2小时）执行一次
  },
  time_display_start: '08:00:00',
  time_display_end: '20:00:00'
};

const response = await fetch('http://localhost:8000/api/v1/taskschedules/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(scheduleData)
});

const result = await response.json();
console.log('创建结果:', result);
```

### Python 示例

```python
import requests

url = "http://localhost:8000/api/v1/taskschedules/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

schedule_data = {
    "task_id": "550e8400-e29b-41d4-a716-446655440010",
    "schedule_name": "每月固定日期间隔巡检",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "enabled": True,
    "item_count": 6,
    "cycle_type": "monthly_days",
    "cycle_config": {
        "selectedDays": [5, 10, 15, 20]  # 每月 5、10、15、20 日
    },
    "time_mode": "interval",
    "time_config": {
        "intervalTimeRange": ["08:00", "20:00"],  # 08:00 到 20:00
        "intervalMinutes": 120  # 每 120 分钟（2小时）执行一次
    },
    "time_display_start": "08:00:00",
    "time_display_end": "20:00:00"
}

response = requests.post(url, json=schedule_data, headers=headers)
if response.status_code == 200:
    print("创建成功:", response.json())
else:
    print("创建失败:", response.text)
```

### 执行时间说明

这个配置会在以下时间执行：
- **每月 5 日**: 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00
- **每月 10 日**: 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00
- **每月 15 日**: 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00
- **每月 20 日**: 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00

**注意**: 如果某个月没有 31 日，则不会在 31 日执行。例如 2 月只有 28/29 日，所以只会执行 5、10、15、20 日。

---

## 示例 5: 云台日程 - 每天 + 间隔时间

### 场景
每天在 06:00-22:00 之间，每 30 分钟执行一次云台巡检

### 请求体

```json
{
  "gimbaltask_id": "550e8400-e29b-41d4-a716-446655440040",
  "schedule_name": "云台全天候监控",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "enabled": true,
  "cycle_type": "daily",
  "cycle_config": null,
  "time_mode": "interval",
  "time_config": {
    "intervalTimeRange": ["06:00", "22:00"],
    "intervalMinutes": 30
  },
  "time_display_start": "06:00:00",
  "time_display_end": "22:00:00"
}
```

### Python 示例

```python
import requests
from datetime import date

url = "http://localhost:8000/api/v1/gimbalschedules/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

schedule_data = {
    "gimbaltask_id": "550e8400-e29b-41d4-a716-446655440040",
    "schedule_name": "云台全天候监控",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "enabled": True,
    "cycle_type": "daily",
    "cycle_config": None,
    "time_mode": "interval",
    "time_config": {
        "intervalTimeRange": ["06:00", "22:00"],
        "intervalMinutes": 30
    },
    "time_display_start": "06:00:00",
    "time_display_end": "22:00:00"
}

response = requests.post(url, json=schedule_data, headers=headers)
if response.status_code == 200:
    print("创建成功:", response.json())
else:
    print("创建失败:", response.text)
```

---

## 示例 6: 前端格式转换示例

如果前端使用自己的格式，需要先转换为后端格式再调用接口。

### 前端格式（示例）

```javascript
// 前端收集的数据
const frontendData = {
  task_id: '550e8400-e29b-41d4-a716-446655440010',
  schedule_name: '每日巡检',
  dateRange: ['2025-01-01', '2025-12-31'],
  enabled: true,
  item_count: 5,
  cycle: '每天',  // 前端格式：每天/日/周
  selectedDays: null,
  selectedWeeks: null,
  timeMode: '自定义',  // 前端格式：自定义/间隔
  customTimes: ['08:00', '14:00', '20:00'],
  intervalTimeRange: null,
  intervalMinutes: null
};
```

### 转换函数（JavaScript）

```javascript
function convertFrontendToBackend(frontendData) {
  // 周期类型映射
  const cycleMapping = {
    '每天': 'daily',
    '日': 'monthly_days',
    '周': 'weekly'
  };
  
  // 时间模式映射
  const timeModeMapping = {
    '自定义': 'custom',
    '间隔': 'interval'
  };
  
  const cycleType = cycleMapping[frontendData.cycle];
  const timeMode = timeModeMapping[frontendData.timeMode];
  
  // 构建 cycle_config
  let cycleConfig = null;
  if (cycleType === 'monthly_days' && frontendData.selectedDays) {
    cycleConfig = { selectedDays: frontendData.selectedDays };
  } else if (cycleType === 'weekly' && frontendData.selectedWeeks) {
    cycleConfig = { selectedWeeks: frontendData.selectedWeeks };
  }
  
  // 构建 time_config
  let timeConfig = {};
  if (timeMode === 'custom' && frontendData.customTimes) {
    timeConfig = { customTimes: frontendData.customTimes };
  } else if (timeMode === 'interval' && frontendData.intervalTimeRange && frontendData.intervalMinutes) {
    timeConfig = {
      intervalTimeRange: frontendData.intervalTimeRange,
      intervalMinutes: frontendData.intervalMinutes
    };
  }
  
  // 计算时间显示字段
  let timeDisplayStart = null;
  let timeDisplayEnd = null;
  if (timeConfig.customTimes && timeConfig.customTimes.length > 0) {
    timeDisplayStart = timeConfig.customTimes[0] + ':00';
    timeDisplayEnd = timeConfig.customTimes[timeConfig.customTimes.length - 1] + ':00';
  } else if (timeConfig.intervalTimeRange && timeConfig.intervalTimeRange.length >= 2) {
    timeDisplayStart = timeConfig.intervalTimeRange[0] + ':00';
    timeDisplayEnd = timeConfig.intervalTimeRange[1] + ':00';
  }
  
  // 返回后端格式
  return {
    task_id: frontendData.task_id,
    schedule_name: frontendData.schedule_name,
    start_date: frontendData.dateRange[0],
    end_date: frontendData.dateRange[1],
    enabled: frontendData.enabled,
    item_count: frontendData.item_count || 0,
    cycle_type: cycleType,
    cycle_config: cycleConfig,
    time_mode: timeMode,
    time_config: timeConfig,
    time_display_start: timeDisplayStart,
    time_display_end: timeDisplayEnd
  };
}

// 使用示例
const backendData = convertFrontendToBackend(frontendData);

const response = await fetch('http://localhost:8000/api/v1/taskschedules/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(backendData)
});
```

### 转换函数（Python）

```python
def convert_frontend_to_backend(frontend_data):
    """将前端格式转换为后端格式"""
    # 周期类型映射
    cycle_mapping = {
        '每天': 'daily',
        '日': 'monthly_days',
        '周': 'weekly'
    }
    
    # 时间模式映射
    time_mode_mapping = {
        '自定义': 'custom',
        '间隔': 'interval'
    }
    
    cycle_type = cycle_mapping[frontend_data['cycle']]
    time_mode = time_mode_mapping[frontend_data['timeMode']]
    
    # 构建 cycle_config
    cycle_config = None
    if cycle_type == 'monthly_days' and frontend_data.get('selectedDays'):
        cycle_config = {'selectedDays': frontend_data['selectedDays']}
    elif cycle_type == 'weekly' and frontend_data.get('selectedWeeks'):
        cycle_config = {'selectedWeeks': frontend_data['selectedWeeks']}
    
    # 构建 time_config
    time_config = {}
    if time_mode == 'custom' and frontend_data.get('customTimes'):
        time_config = {'customTimes': frontend_data['customTimes']}
    elif time_mode == 'interval' and frontend_data.get('intervalTimeRange') and frontend_data.get('intervalMinutes'):
        time_config = {
            'intervalTimeRange': frontend_data['intervalTimeRange'],
            'intervalMinutes': frontend_data['intervalMinutes']
        }
    
    # 计算时间显示字段
    time_display_start = None
    time_display_end = None
    if time_config.get('customTimes'):
        times = time_config['customTimes']
        if times:
            time_display_start = times[0] + ':00'
            time_display_end = times[-1] + ':00'
    elif time_config.get('intervalTimeRange'):
        time_range = time_config['intervalTimeRange']
        if len(time_range) >= 2:
            time_display_start = time_range[0] + ':00'
            time_display_end = time_range[1] + ':00'
    
    # 返回后端格式
    return {
        'task_id': frontend_data['task_id'],
        'schedule_name': frontend_data['schedule_name'],
        'start_date': frontend_data['dateRange'][0],
        'end_date': frontend_data['dateRange'][1],
        'enabled': frontend_data.get('enabled', True),
        'item_count': frontend_data.get('item_count', 0),
        'cycle_type': cycle_type,
        'cycle_config': cycle_config,
        'time_mode': time_mode,
        'time_config': time_config,
        'time_display_start': time_display_start,
        'time_display_end': time_display_end
    }

# 使用示例
frontend_data = {
    'task_id': '550e8400-e29b-41d4-a716-446655440010',
    'schedule_name': '每日巡检',
    'dateRange': ['2025-01-01', '2025-12-31'],
    'enabled': True,
    'item_count': 5,
    'cycle': '每天',
    'timeMode': '自定义',
    'customTimes': ['08:00', '14:00', '20:00']
}

backend_data = convert_frontend_to_backend(frontend_data)
response = requests.post(
    'http://localhost:8000/api/v1/taskschedules/',
    json=backend_data,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

---

## 字段说明

### 周期类型 (cycle_type)

- `daily`: 每天执行
- `monthly_days`: 每月指定日期执行（需要 `cycle_config.selectedDays`）
- `weekly`: 每周指定星期执行（需要 `cycle_config.selectedWeeks`，1=周一，7=周日）

### 时间模式 (time_mode)

- `custom`: 自定义时间点（需要 `time_config.customTimes` 数组）
- `interval`: 间隔时间（需要 `time_config.intervalTimeRange` 和 `intervalMinutes`）

### 可选字段

- `time_display_start` 和 `time_display_end`: 用于前端时间轴显示，如果不提供，后端会根据 `time_config` 自动计算
- `item_count`: 关联的巡检项目数量（任务日程专用）

---

## 响应示例

### 成功响应

```json
{
  "code": 200,
  "message": "任务日程创建成功",
  "data": {
    "id": "schedule-uuid-here",
    "task_id": "550e8400-e29b-41d4-a716-446655440010",
    "task_name": "巡检任务1",
    "schedule_name": "每日三次巡检",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "enabled": true,
    "item_count": 5,
    "cycle_type": "daily",
    "cycle_config": null,
    "time_mode": "custom",
    "time_config": {
      "customTimes": ["08:00", "14:00", "20:00"]
    },
    "cycle_display": "每天",
    "time_display_start": "08:00",
    "time_display_end": "20:00",
    "created_at": "2025-01-01T10:00:00",
    "updated_at": "2025-01-01T10:00:00",
    "created_by": "admin",
    "updated_by": "admin",
    "is_deleted": false
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "cycle_type must be one of ['daily', 'monthly_days', 'weekly']",
  "data": null
}
```

---

## 注意事项

1. **认证**: 所有接口都需要有效的 JWT Token
2. **日期格式**: 使用 `YYYY-MM-DD` 格式
3. **时间格式**: 使用 `HH:MM` 或 `HH:MM:SS` 格式
4. **周期配置**: 
   - `monthly_days` 需要 `selectedDays` 数组（1-31）
   - `weekly` 需要 `selectedWeeks` 数组（1-7，1=周一）
5. **时间配置**:
   - `custom` 模式需要 `customTimes` 数组
   - `interval` 模式需要 `intervalTimeRange` 和 `intervalMinutes`
6. **可选字段**: `time_display_start` 和 `time_display_end` 可以不提供，后端会自动计算

