# API快速参考

## 🚀 快速开始

### 1. 登录获取Token
```bash
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "admin"
}
```

### 2. 使用Token访问API
```bash
Authorization: Bearer {your_token}
```

---

## 📋 接口速查表

### 认证相关 (详见 `docs/api/01_auth.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/auth/login` | POST | 🌐 | 用户登录 |
| `/api/v1/auth/logout` | POST | 🔒 | 用户登出 |
| `/api/v1/auth/refresh` | POST | 🔒 | 刷新令牌 |
| `/api/v1/auth/me` | GET | 🔒 | 获取当前用户信息 |

### 用户管理 (详见 `docs/api/02_users.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/users/` | POST | 👑 | 创建用户 |
| `/api/v1/users/` | GET | 👁️ | 获取用户列表 |
| `/api/v1/users/{id}` | GET | 👁️ | 获取单个用户 |
| `/api/v1/users/{id}` | PUT | 👑 | 更新用户 |
| `/api/v1/users/{id}` | DELETE | 👑 | 删除用户 |
| `/api/v1/users/updatepassword` | PUT | 🔒 | 修改密码 |

### 地图管理 (详见 `docs/api/03_maps.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/maps/` | POST | ✏️ | 创建地图 |
| `/api/v1/maps/` | GET | 👁️ | 获取地图列表 |
| `/api/v1/maps/{id}` | GET | 👁️ | 获取单个地图 |
| `/api/v1/maps/{id}` | PUT | ✏️ | 更新地图 |
| `/api/v1/maps/{id}` | DELETE | ✏️ | 删除地图 |
| `/api/v1/maps/stats/summary` | GET | 👁️ | 地图统计 |

### 路网管理 (详见 `docs/api/04_mapnets.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/mapnets/` | POST | ✏️ | 创建路网元素 |
| `/api/v1/mapnets/` | GET | 👁️ | 获取路网列表 |
| `/api/v1/mapnets/by-ids` | GET | 👁️ | 批量ID查询 |
| `/api/v1/mapnets/{id}` | GET | 👁️ | 获取单个路网 |
| `/api/v1/mapnets/{id}` | PUT | ✏️ | 更新路网 |
| `/api/v1/mapnets/{id}` | DELETE | ✏️ | 删除路网 |
| `/api/v1/mapnets/stats/summary` | GET | 👁️ | 路网统计 |

### 机器人管理 (详见 `docs/api/05_robots.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/robots/` | POST | ✏️ | 创建机器人 |
| `/api/v1/robots/` | GET | 👁️ | 获取机器人列表 |
| `/api/v1/robots/by-ids` | GET | 👁️ | 批量ID查询 |
| `/api/v1/robots/{id}` | GET | 👁️ | 获取单个机器人 |
| `/api/v1/robots/{id}` | PUT | ✏️ | 更新机器人 |
| `/api/v1/robots/{id}` | DELETE | ✏️ | 删除机器人 |
| `/api/v1/robots/stats/summary` | GET | 👁️ | 机器人统计 |

### 巡检点管理 (详见 `docs/api/06_points.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/points/` | POST | ✏️ | 创建巡检点 |
| `/api/v1/points/` | GET | 👁️ | 获取巡检点列表 |
| `/api/v1/points/by-ids` | GET | 👁️ | 批量ID查询 |
| `/api/v1/points/{id}` | GET | 👁️ | 获取单个巡检点 |
| `/api/v1/points/{id}` | PUT | ✏️ | 更新巡检点 |
| `/api/v1/points/{id}` | DELETE | ✏️ | 删除巡检点 |
| `/api/v1/points/stats/summary` | GET | 👁️ | 巡检点统计 |

### 巡检项目管理 (详见 `docs/api/07_items.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/items/` | POST | ✏️ | 创建巡检项目 |
| `/api/v1/items/` | GET | 👁️ | 获取巡检项目列表 |
| `/api/v1/items/by-ids` | GET | 👁️ | 批量ID查询 |
| `/api/v1/items/{id}` | GET | 👁️ | 获取单个巡检项目 |
| `/api/v1/items/{id}` | PUT | ✏️ | 更新巡检项目 |
| `/api/v1/items/{id}` | DELETE | ✏️ | 删除巡检项目 |
| `/api/v1/items/stats/summary` | GET | 👁️ | 巡检项目统计 |

### 任务管理 (详见 `docs/api/09_tasks.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/tasks/` | POST | ✏️ | 创建任务 |
| `/api/v1/tasks/` | GET | 👁️ | 获取任务列表 |
| `/api/v1/tasks/by-ids` | GET | 👁️ | 批量ID查询 |
| `/api/v1/tasks/{id}` | GET | 👁️ | 获取单个任务 |
| `/api/v1/tasks/{id}` | PUT | ✏️ | 更新任务 |
| `/api/v1/tasks/{id}` | DELETE | ✏️ | 删除任务 |

### 报警规则 (详见 `docs/api/14_alarmrules.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/alarmrules/` | POST | ✏️ | 创建报警规则 |
| `/api/v1/alarmrules/` | GET | 👁️ | 获取报警规则列表 |
| `/api/v1/alarmrules/by-ids` | GET | 👁️ | 批量ID查询 |
| `/api/v1/alarmrules/{id}` | GET | 👁️ | 获取单个报警规则 |
| `/api/v1/alarmrules/{id}` | PUT | ✏️ | 更新报警规则 |
| `/api/v1/alarmrules/{id}` | DELETE | ✏️ | 删除报警规则 |
| `/api/v1/alarmrules/stats/summary` | GET | 👁️ | 报警规则统计 |

### 日志管理 (详见 `docs/api/17_logs.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/logs/files` | GET | 👑 | 获取日志文件列表 |
| `/api/v1/logs/read` | GET | 👑 | 在线阅读日志 |
| `/api/v1/logs/download` | GET | 👑 | 下载日志文件 |
| `/api/v1/logs/search` | GET | 👑 | 搜索日志内容 |
| `/api/v1/logs/cleanup` | DELETE | 👑 | 清理旧日志 |
| `/api/v1/logs/stats` | GET | 👑 | 日志统计 |

### 系统管理 (详见 `docs/api/16_system.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/system/info` | GET | 👁️ | 获取系统信息 |
| `/api/v1/system/health` | GET | 🌐 | 健康检查 |

### ROS2通信 (详见 `docs/api/18_ros2.md`)
| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/v1/ros2/publish/string` | POST | ✏️ | 发布字符串消息 |
| `/api/v1/ros2/publish/int` | POST | ✏️ | 发布整数消息 |
| `/api/v1/ros2/publish/float` | POST | ✏️ | 发布浮点数消息 |
| `/api/v1/ros2/publish/bool` | POST | ✏️ | 发布布尔值消息 |
| `/api/v1/ros2/nodes` | GET | 👁️ | 获取节点列表 |
| `/api/v1/ros2/topics` | GET | 👁️ | 获取话题列表 |

---

## 🔐 权限说明

| 图标 | 权限级别 | 可访问角色 |
|------|---------|-----------|
| 🌐 | 无需认证 | 所有人 |
| 🔒 | 需要认证 | 所有登录用户 |
| 👁️ | read | super_admin, admin, operator, viewer, user |
| ✏️ | write | super_admin, admin, operator |
| 👑 | admin+ | super_admin, admin |

**角色层级**: super_admin > admin > operator > viewer > user

---

## 📊 统一响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 响应数据
  }
}
```

### 分页响应
```json
{
  "code": 200,
  "message": "获取列表成功",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 错误响应
```json
{
  "code": 404,
  "message": "资源不存在"
}
```

---

## 🔢 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 210 | 登录成功，需要重置密码 |
| 301 | 请求参数错误 |
| 410 | Token验证失败 |
| 414 | 登录失败 |
| 999 | 系统异常 |

---

## 📞 更多信息

- **完整API文档**: `docs/API_REFERENCE.md`
- **模块详细文档**: `docs/api/README.md`
- **文档总结**: `docs/API_DOCS_SUMMARY.md`

---

**最后更新**: 2024-01-16
