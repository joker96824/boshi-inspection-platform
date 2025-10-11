# API测试数据手册

## 📋 说明
本文档提供所有API接口在Swagger文档页面（http://localhost:8000/docs）测试时使用的参数。

---

## 🔐 认证相关 (4个接口)

### 1. POST /api/v1/auth/login
```json
{
  "username": "admin",
  "password": "admin"
}
```

### 2. POST /api/v1/auth/logout
无需参数（需要Token）

### 3. POST /api/v1/auth/refresh
无需参数（需要Token）

### 4. GET /api/v1/auth/me
无需参数（需要Token）

---

## 👥 用户管理 (6个接口)

### 1. POST /api/v1/users/
```json
{
  "username": "testuser001",
  "password": "password123",
  "role": "operator",
  "mobile": "13800138888",
  "email": "test@example.com"
}
```

### 2. GET /api/v1/users/
**查询参数**:
- page: `1`
- size: `20`

### 3. GET /api/v1/users/{user_id}
**路径参数**:
- user_id: `550e8400-e29b-41d4-a716-446655440101`

### 4. PUT /api/v1/users/{user_id}
**路径参数**:
- user_id: `550e8400-e29b-41d4-a716-446655440101`

**请求体**:
```json
{
  "email": "updated@example.com",
  "mobile": "13900139999"
}
```

### 5. PUT /api/v1/users/updatepassword
```json
{
  "old_password": "admin",
  "new_password": "newpass123"
}
```

### 6. DELETE /api/v1/users/{user_id}
**路径参数**:
- user_id: `{创建的测试用户ID}`

---

## 🗺️ 地图管理 (6个接口)

### 1. POST /api/v1/maps/
```json
{
  "map_name": "测试地图001",
  "map_image_url": "/uploads/maps/test_map.png",
  "map_scale": 1.0,
  "map_center_x": 100.0,
  "map_center_y": 100.0
}
```

### 2. GET /api/v1/maps/
**查询参数**:
- page: `1`
- size: `20`
- map_name: `一楼`（可选，模糊匹配）

### 3. GET /api/v1/maps/{map_id}
**路径参数**:
- map_id: `550e8400-e29b-41d4-a716-446655440001`

### 4. PUT /api/v1/maps/{map_id}
**路径参数**:
- map_id: `550e8400-e29b-41d4-a716-446655440001`

**请求体**:
```json
{
  "map_name": "一楼巡检地图（已更新）",
  "map_scale": 1.5
}
```

### 5. DELETE /api/v1/maps/{map_id}
**路径参数**:
- map_id: `{创建的测试地图ID}`

### 6. GET /api/v1/maps/stats/summary
无需参数

---

## 🛣️ 地图路网管理 (7个接口)

### 1. POST /api/v1/mapnets/
```json
{
  "map_id": "550e8400-e29b-41d4-a716-446655440001",
  "map_net_type": "point",
  "map_net_properties": {"name": "测试导航点", "type": "navigation"},
  "map_net_geometry": {"x": 120.0, "y": 80.0}
}
```

### 2. GET /api/v1/mapnets/
**查询参数**:
- page: `1`
- size: `20`
- map_id: `550e8400-e29b-41d4-a716-446655440001`（可选）
- map_net_type: `point`（可选）

### 3. GET /api/v1/mapnets/by-ids
**查询参数**:
- mapnet_ids: `550e8400-e29b-41d4-a716-446655440501`

### 4. GET /api/v1/mapnets/{mapnet_id}
**路径参数**:
- mapnet_id: `550e8400-e29b-41d4-a716-446655440501`

### 5. PUT /api/v1/mapnets/{mapnet_id}
**路径参数**:
- mapnet_id: `550e8400-e29b-41d4-a716-446655440501`

**请求体**:
```json
{
  "map_net_properties": {"name": "更新的导航点", "color": "red"}
}
```

### 6. DELETE /api/v1/mapnets/{mapnet_id}
**路径参数**:
- mapnet_id: `{创建的测试路网ID}`

### 7. GET /api/v1/mapnets/stats/summary
无需参数

---

## 🤖 机器人管理 (7个接口)

### 1. POST /api/v1/robots/
```json
{
  "robot_name": "测试机器人001",
  "robot_info": {"model": "TEST-01", "battery": 95}
}
```

### 2. GET /api/v1/robots/
**查询参数**:
- page: `1`
- size: `20`
- robot_name: `巡检`（可选，模糊匹配）

### 3. GET /api/v1/robots/by-ids
**查询参数**:
- robot_ids: `550e8400-e29b-41d4-a716-446655440002`

### 4. GET /api/v1/robots/{robot_id}
**路径参数**:
- robot_id: `550e8400-e29b-41d4-a716-446655440002`

### 5. PUT /api/v1/robots/{robot_id}
**路径参数**:
- robot_id: `550e8400-e29b-41d4-a716-446655440002`

**请求体**:
```json
{
  "robot_name": "巡检机器人001（已更新）",
  "robot_info": {"model": "BOSHI-RB-01", "battery": 85}
}
```

### 6. DELETE /api/v1/robots/{robot_id}
**路径参数**:
- robot_id: `{创建的测试机器人ID}`

### 7. GET /api/v1/robots/stats/summary
无需参数

---

## 📍 巡检点管理 (7个接口)

### 1. POST /api/v1/points/
```json
{
  "point_name": "测试检查点001",
  "map_id": "550e8400-e29b-41d4-a716-446655440001",
  "point_actions": {"action": "patrol", "duration": 30}
}
```

### 2. GET /api/v1/points/
**查询参数**:
- page: `1`
- size: `20`
- point_name: `入口`（可选）
- map_id: `550e8400-e29b-41d4-a716-446655440001`（可选）

### 3. GET /api/v1/points/by-ids
**查询参数**:
- point_ids: `550e8400-e29b-41d4-a716-446655440005`

### 4. GET /api/v1/points/{point_id}
**路径参数**:
- point_id: `550e8400-e29b-41d4-a716-446655440005`

### 5. PUT /api/v1/points/{point_id}
**路径参数**:
- point_id: `550e8400-e29b-41d4-a716-446655440005`

**请求体**:
```json
{
  "point_name": "一楼入口检查点（已更新）",
  "point_actions": {"action": "stop_and_check", "duration": 45}
}
```

### 6. DELETE /api/v1/points/{point_id}
**路径参数**:
- point_id: `{创建的测试巡检点ID}`

### 7. GET /api/v1/points/stats/summary
无需参数

---

## 📦 巡检项目管理 (7个接口)

### 1. POST /api/v1/items/
```json
{
  "item_name": "测试巡检项目001",
  "item_info": {"type": "photo", "required": true}
}
```

### 2. GET /api/v1/items/
**查询参数**:
- page: `1`
- size: `20`
- item_name: `拍照`（可选）

### 3. GET /api/v1/items/by-ids
**查询参数**:
- item_ids: `550e8400-e29b-41d4-a716-446655440009`

### 4. GET /api/v1/items/{item_id}
**路径参数**:
- item_id: `550e8400-e29b-41d4-a716-446655440009`

### 5. PUT /api/v1/items/{item_id}
**路径参数**:
- item_id: `550e8400-e29b-41d4-a716-446655440009`

**请求体**:
```json
{
  "item_name": "拍照记录（已更新）",
  "item_info": {"type": "photo", "required": true, "min_count": 2}
}
```

### 6. DELETE /api/v1/items/{item_id}
**路径参数**:
- item_id: `{创建的测试巡检项目ID}`

### 7. GET /api/v1/items/stats/summary
无需参数

---

## 🔗 点-项关联管理 (10个接口)

### 1. POST /api/v1/point-items/
```json
{
  "point_id": "550e8400-e29b-41d4-a716-446655440005",
  "item_id": "550e8400-e29b-41d4-a716-446655440009"
}
```

### 2. GET /api/v1/point-items/by-point/{point_id}
**路径参数**:
- point_id: `550e8400-e29b-41d4-a716-446655440005`

**查询参数**:
- page: `1`
- size: `20`
- with_details: `true`（可选）

### 3. GET /api/v1/point-items/by-item/{item_id}
**路径参数**:
- item_id: `550e8400-e29b-41d4-a716-446655440009`

**查询参数**:
- page: `1`
- size: `20`
- with_details: `true`（可选）

### 4. PUT /api/v1/point-items/by-point/{point_id}
**路径参数**:
- point_id: `550e8400-e29b-41d4-a716-446655440005`

**请求体**:
```json
{
  "item_ids": [
    "550e8400-e29b-41d4-a716-446655440009",
    "550e8400-e29b-41d4-a716-446655440010"
  ]
}
```

### 5. PUT /api/v1/point-items/by-item/{item_id}
**路径参数**:
- item_id: `550e8400-e29b-41d4-a716-446655440009`

**请求体**:
```json
{
  "point_ids": [
    "550e8400-e29b-41d4-a716-446655440005",
    "550e8400-e29b-41d4-a716-446655440006"
  ]
}
```

### 6. DELETE /api/v1/point-items/{point_item_id}
**路径参数**:
- point_item_id: `550e8400-e29b-41d4-a716-446655440015`

### 7. DELETE /api/v1/point-items/by-point/{point_id}
**路径参数**:
- point_id: `{测试用的point_id}`

### 8. DELETE /api/v1/point-items/by-item/{item_id}
**路径参数**:
- item_id: `{测试用的item_id}`

### 9. GET /api/v1/point-items/{point_item_id}
**路径参数**:
- point_item_id: `550e8400-e29b-41d4-a716-446655440015`

### 10. GET /api/v1/point-items/stats/summary
无需参数

---

## 📋 任务管理 (6个接口)

### 1. POST /api/v1/tasks/
```json
{
  "task_name": "测试任务001",
  "map_id": "550e8400-e29b-41d4-a716-446655440001",
  "robot_id": "550e8400-e29b-41d4-a716-446655440002",
  "task_items": [
    "550e8400-e29b-41d4-a716-446655440009",
    "550e8400-e29b-41d4-a716-446655440010"
  ],
  "task_order": 1,
  "task_res_prior": 5,
  "task_int_prior": 3
}
```

### 2. GET /api/v1/tasks/
**查询参数**:
- page: `1`
- size: `20`
- task_name: `日常`（可选）
- map_id: `550e8400-e29b-41d4-a716-446655440001`（可选）
- robot_id: `550e8400-e29b-41d4-a716-446655440002`（可选）
- sort_by: `task_order`（可选）
- sort_order: `asc`（可选）

### 3. GET /api/v1/tasks/by-ids
**查询参数**:
- task_ids: `550e8400-e29b-41d4-a716-446655440003`

### 4. GET /api/v1/tasks/{task_id}
**路径参数**:
- task_id: `550e8400-e29b-41d4-a716-446655440003`

### 5. PUT /api/v1/tasks/{task_id}
**路径参数**:
- task_id: `550e8400-e29b-41d4-a716-446655440003`

**请求体**:
```json
{
  "task_name": "一楼日常巡检（已更新）",
  "task_res_prior": 7
}
```

### 6. DELETE /api/v1/tasks/{task_id}
**路径参数**:
- task_id: `{创建的测试任务ID}`

---

## 📅 任务日程管理 (7个接口)

### 1. POST /api/v1/taskschedules/
```json
{
  "schedule_type": "daily",
  "schedule_is_active": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440003",
  "schedule_param": {"time": "08:00:00", "repeat": true},
  "set_time": 1705392000,
  "cnt": 0
}
```

### 2. GET /api/v1/taskschedules/
**查询参数**:
- page: `1`
- size: `20`
- task_id: `550e8400-e29b-41d4-a716-446655440003`（可选）
- schedule_is_active: `true`（可选）

### 3. GET /api/v1/taskschedules/by-ids
**查询参数**:
- taskschedule_ids: `550e8400-e29b-41d4-a716-446655440601`

### 4. GET /api/v1/taskschedules/{taskschedule_id}
**路径参数**:
- taskschedule_id: `550e8400-e29b-41d4-a716-446655440601`

### 5. PUT /api/v1/taskschedules/{taskschedule_id}
**路径参数**:
- taskschedule_id: `550e8400-e29b-41d4-a716-446655440601`

**请求体**:
```json
{
  "schedule_is_active": false,
  "cnt": 10
}
```

### 6. DELETE /api/v1/taskschedules/{taskschedule_id}
**路径参数**:
- taskschedule_id: `{创建的测试日程ID}`

### 7. GET /api/v1/taskschedules/stats/summary
无需参数

---

## 📝 任务记录管理 (6个接口)

### 1. POST /api/v1/taskhistories/
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440003",
  "record_start_time": "2024-01-17T08:00:00",
  "record_end_time": "2024-01-17T08:30:00",
  "record_status": "completed",
  "record_batch": 10
}
```

### 2. GET /api/v1/taskhistories/
**查询参数**:
- page: `1`
- size: `20`
- task_id: `550e8400-e29b-41d4-a716-446655440003`（可选）
- record_status: `completed`（可选）
- start_time_from: `2024-01-15T00:00:00`（可选）
- start_time_to: `2024-01-17T23:59:59`（可选）

### 3. GET /api/v1/taskhistories/by-ids
**查询参数**:
- taskhistory_ids: `550e8400-e29b-41d4-a716-446655440801`

### 4. GET /api/v1/taskhistories/{taskhistory_id}
**路径参数**:
- taskhistory_id: `550e8400-e29b-41d4-a716-446655440801`

### 5. PUT /api/v1/taskhistories/{taskhistory_id}
**路径参数**:
- taskhistory_id: `550e8400-e29b-41d4-a716-446655440801`

**请求体**:
```json
{
  "record_end_time": "2024-01-15T08:35:00",
  "record_status": "completed"
}
```

### 6. DELETE /api/v1/taskhistories/{taskhistory_id}
**路径参数**:
- taskhistory_id: `{创建的测试记录ID}`

---

## 📊 任务结果管理 (7个接口)

### 1. POST /api/v1/taskresults/
```json
{
  "taskhistory_id": "550e8400-e29b-41d4-a716-446655440803",
  "record_batch": 3,
  "result_point_id": "550e8400-e29b-41d4-a716-446655440006",
  "result_item_id": "550e8400-e29b-41d4-a716-446655440011",
  "result_file_url": "/uploads/results/test_result.json",
  "result_collect_time": "2024-01-17T09:00:00"
}
```

### 2. GET /api/v1/taskresults/
**查询参数**:
- page: `1`
- size: `20`
- taskhistory_id: `550e8400-e29b-41d4-a716-446655440801`（可选）

### 3. GET /api/v1/taskresults/by-ids
**查询参数**:
- taskresult_ids: `550e8400-e29b-41d4-a716-446655440901`

### 4. GET /api/v1/taskresults/{taskresult_id}
**路径参数**:
- taskresult_id: `550e8400-e29b-41d4-a716-446655440901`

### 5. PUT /api/v1/taskresults/{taskresult_id}
**路径参数**:
- taskresult_id: `550e8400-e29b-41d4-a716-446655440901`

**请求体**:
```json
{
  "result_file_url": "/uploads/results/updated_result.json"
}
```

### 6. DELETE /api/v1/taskresults/{taskresult_id}
**路径参数**:
- taskresult_id: `{创建的测试结果ID}`

### 7. GET /api/v1/taskresults/stats/summary
无需参数

---

## 🔍 巡检记录管理 (8个接口)

### 1. POST /api/v1/itemhistories/
```json
{
  "taskhistory_id": "550e8400-e29b-41d4-a716-446655440801",
  "item_id": "550e8400-e29b-41d4-a716-446655440009",
  "item_result": {"status": "success", "photos": ["/data/test_photo.jpg"]}
}
```

### 2. GET /api/v1/itemhistories/by-taskhistory/{taskhistory_id}
**路径参数**:
- taskhistory_id: `550e8400-e29b-41d4-a716-446655440801`

**查询参数**:
- page: `1`
- size: `20`
- with_details: `true`（可选）

### 3. GET /api/v1/itemhistories/by-item/{item_id}
**路径参数**:
- item_id: `550e8400-e29b-41d4-a716-446655440009`

**查询参数**:
- page: `1`
- size: `20`
- with_details: `true`（可选）

### 4. GET /api/v1/itemhistories/{itemhistory_id}
**路径参数**:
- itemhistory_id: `550e8400-e29b-41d4-a716-446655441001`

### 5. PUT /api/v1/itemhistories/{itemhistory_id}
**路径参数**:
- itemhistory_id: `550e8400-e29b-41d4-a716-446655441001`

**请求体**:
```json
{
  "item_result": {"status": "success", "photos": ["/data/photo1.jpg", "/data/photo2.jpg"]}
}
```

### 6. DELETE /api/v1/itemhistories/{itemhistory_id}
**路径参数**:
- itemhistory_id: `{创建的测试巡检记录ID}`

### 7. DELETE /api/v1/itemhistories/by-taskhistory/{taskhistory_id}
**路径参数**:
- taskhistory_id: `{测试用的taskhistory_id}`

### 8. GET /api/v1/itemhistories/stats/summary
无需参数

---

## 🚨 报警规则管理 (7个接口)

### 1. POST /api/v1/alarmrules/
```json
{
  "rule_name": "测试报警规则001",
  "item_id": "550e8400-e29b-41d4-a716-446655440601",
  "alarm_param": {"threshold": 40, "operator": "gt", "level": "warning"}
}
```

### 2. GET /api/v1/alarmrules/
**查询参数**:
- page: `1`
- size: `20`
- rule_name: `温度`（可选）
- item_id: `550e8400-e29b-41d4-a716-446655440601`（可选）

### 3. GET /api/v1/alarmrules/by-ids
**查询参数**:
- alarmrule_ids: `550e8400-e29b-41d4-a716-446655441101`

### 4. GET /api/v1/alarmrules/{alarmrule_id}
**路径参数**:
- alarmrule_id: `550e8400-e29b-41d4-a716-446655441101`

### 5. PUT /api/v1/alarmrules/{alarmrule_id}
**路径参数**:
- alarmrule_id: `550e8400-e29b-41d4-a716-446655441101`

**请求体**:
```json
{
  "alarm_param": {"threshold": 45, "operator": "gte", "level": "critical"}
}
```

### 6. DELETE /api/v1/alarmrules/{alarmrule_id}
**路径参数**:
- alarmrule_id: `{创建的测试规则ID}`

### 7. GET /api/v1/alarmrules/stats/summary
无需参数

---

## 🔔 报警信息管理 (7个接口)

### 1. POST /api/v1/alarminfos/
```json
{
  "alarmrule_id": "550e8400-e29b-41d4-a716-446655441102",
  "itemhistory_id": "550e8400-e29b-41d4-a716-446655441003",
  "alarm_data": {"actual_value": 42, "threshold": 40},
  "alarm_info": "温度超过阈值！"
}
```

### 2. GET /api/v1/alarminfos/
**查询参数**:
- page: `1`
- size: `20`
- alarmrule_id: `550e8400-e29b-41d4-a716-446655441101`（可选）
- itemhistory_id: `550e8400-e29b-41d4-a716-446655441003`（可选）

### 3. GET /api/v1/alarminfos/by-ids
**查询参数**:
- alarminfo_ids: `550e8400-e29b-41d4-a716-446655441201`

### 4. GET /api/v1/alarminfos/{alarminfo_id}
**路径参数**:
- alarminfo_id: `550e8400-e29b-41d4-a716-446655441201`

### 5. PUT /api/v1/alarminfos/{alarminfo_id}
**路径参数**:
- alarminfo_id: `550e8400-e29b-41d4-a716-446655441201`

**请求体**:
```json
{
  "alarm_info": "温度异常已处理"
}
```

### 6. DELETE /api/v1/alarminfos/{alarminfo_id}
**路径参数**:
- alarminfo_id: `{创建的测试报警信息ID}`

### 7. GET /api/v1/alarminfos/stats/summary
无需参数

---

## ⚙️ 系统管理 (2个接口)

### 1. GET /api/v1/system/info
无需参数

### 2. GET /api/v1/system/health
无需参数（无需认证）

---

## 📄 日志管理 (6个接口)

### 1. GET /api/v1/logs/files
**查询参数**:
- page: `1`
- size: `20`
- date: `2024-01-16`（可选）
- start_date: `2024-01-15`（可选）
- end_date: `2024-01-17`（可选）

### 2. GET /api/v1/logs/read
**查询参数**:
- filepath: `/logs/2024-01-16/app.log`
- lines: `100`（可选）

### 3. GET /api/v1/logs/download
**查询参数**:
- filepath: `/logs/2024-01-16/app.log`

### 4. GET /api/v1/logs/search
**查询参数**:
- filepath: `/logs/2024-01-16/error.log`
- keyword: `数据库`
- max_results: `50`（可选）

### 5. DELETE /api/v1/logs/cleanup
**查询参数**:
- days: `30`

### 6. GET /api/v1/logs/stats
无需参数

---

## 🤝 ROS2通信 (6个接口)

### 1. POST /api/v1/ros2/publish/string
```json
{
  "topic": "/robot/command",
  "message": "start_inspection"
}
```

### 2. POST /api/v1/ros2/publish/int
```json
{
  "topic": "/robot/priority",
  "message": 5
}
```

### 3. POST /api/v1/ros2/publish/float
```json
{
  "topic": "/robot/speed",
  "message": 1.5
}
```

### 4. POST /api/v1/ros2/publish/bool
```json
{
  "topic": "/robot/emergency_stop",
  "message": false
}
```

### 5. GET /api/v1/ros2/nodes
无需参数

### 6. GET /api/v1/ros2/topics
无需参数

---

## 📌 使用提示

### 1. Token获取
先调用登录接口获取Token，然后在右上角"Authorize"按钮中输入：
```
Bearer {你的token}
```

### 2. ID参数来源
- 使用初始化数据库中的示例ID
- 或创建新资源后使用返回的ID

### 3. 测试顺序建议
```
1. 登录 → 获取Token
2. 创建资源 → 记录返回的ID
3. 查询资源 → 使用创建的ID
4. 更新资源 → 使用创建的ID
5. 删除资源 → 使用创建的ID
```

### 4. 初始化数据库中的可用ID
```
地图: 550e8400-e29b-41d4-a716-446655440001
机器人: 550e8400-e29b-41d4-a716-446655440002
任务: 550e8400-e29b-41d4-a716-446655440003
巡检点: 550e8400-e29b-41d4-a716-446655440005/006/007/008
巡检项目: 550e8400-e29b-41d4-a716-446655440009/010/011/012/013/014/601/602
```

---

**最后更新**: 2024-01-16
