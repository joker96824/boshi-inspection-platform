# 🏗️ 博实智能巡检平台 - 项目结构说明

## 📁 目录结构

```
D:\Project\boshi\boshi-inspection-platform\
├── app/                          # 主应用程序
│   ├── api/                      # API路由层
│   │   └── v1/                   # API v1版本
│   │       ├── alarminfos.py     # 报警信息接口
│   │       ├── alarmrules.py     # 报警规则接口
│   │       ├── auth.py           # 认证接口
│   │       ├── itemhistories.py  # 巡检记录接口
│   │       ├── items.py          # 巡检项目接口
│   │       ├── logs.py           # 日志管理接口
│   │       ├── mapnets.py        # 地图路网接口
│   │       ├── maps.py           # 地图管理接口
│   │       ├── point_items.py    # 点-项关联接口
│   │       ├── points.py         # 巡检点接口
│   │       ├── robots.py         # 机器人管理接口
│   │       ├── ros2.py           # ROS2通信接口
│   │       ├── system.py         # 系统信息接口
│   │       ├── taskhistories.py  # 任务记录接口
│   │       ├── taskresults.py    # 任务结果接口
│   │       ├── tasks.py          # 任务管理接口
│   │       ├── taskschedules.py  # 任务日程接口
│   │       └── users.py          # 用户管理接口
│   ├── config/                   # 配置管理
│   │   ├── database.py           # 数据库配置
│   │   ├── logging.py            # 分层日志配置
│   │   ├── redis.py              # Redis配置
│   │   └── settings.py           # 应用设置
│   ├── core/                     # 核心功能
│   │   ├── auth.py               # JWT认证
│   │   ├── deps.py               # 依赖注入
│   │   ├── exceptions.py         # 自定义异常
│   │   ├── middleware.py         # 中间件
│   │   ├── permissions.py        # 权限管理
│   │   └── security.py           # 安全工具
│   ├── models/                   # 数据模型层(15个表)
│   │   ├── base.py               # 基础模型
│   │   ├── user.py               # 用户模型
│   │   ├── session.py            # 会话模型
│   │   ├── map.py                # 地图模型
│   │   ├── mapnet.py             # 地图路网模型
│   │   ├── robot.py              # 机器人模型
│   │   ├── point.py              # 巡检点模型
│   │   ├── item.py               # 巡检项目模型
│   │   ├── point_item.py         # 点-项关联模型
│   │   ├── task.py               # 任务模型
│   │   ├── taskschedule.py       # 任务日程模型
│   │   ├── taskhistory.py        # 任务记录模型
│   │   ├── taskresult.py         # 任务结果模型
│   │   ├── itemhistory.py        # 巡检记录模型
│   │   ├── alarmrule.py          # 报警规则模型
│   │   └── alarminfo.py          # 报警信息模型
│   ├── repositories/             # 数据访问层(14个)
│   │   ├── user_repository.py
│   │   ├── map_repository.py
│   │   ├── mapnet_repository.py
│   │   ├── robot_repository.py
│   │   ├── point_repository.py
│   │   ├── item_repository.py
│   │   ├── point_item_repository.py
│   │   ├── task_repository.py
│   │   ├── taskschedule_repository.py
│   │   ├── taskhistory_repository.py
│   │   ├── taskresult_repository.py
│   │   ├── itemhistory_repository.py
│   │   ├── alarmrule_repository.py
│   │   └── alarminfo_repository.py
│   ├── schemas/                  # Pydantic模式(15个)
│   │   ├── base.py               # 基础模式
│   │   ├── user.py               # 用户模式
│   │   ├── map.py                # 地图模式
│   │   ├── mapnet.py             # 路网模式
│   │   ├── robot.py              # 机器人模式
│   │   ├── point.py              # 巡检点模式
│   │   ├── item.py               # 巡检项目模式
│   │   ├── point_item.py         # 点-项关联模式
│   │   ├── task.py               # 任务模式
│   │   ├── taskschedule.py       # 任务日程模式
│   │   ├── taskhistory.py        # 任务记录模式
│   │   ├── taskresult.py         # 任务结果模式
│   │   ├── itemhistory.py        # 巡检记录模式
│   │   ├── alarmrule.py          # 报警规则模式
│   │   └── alarminfo.py          # 报警信息模式
│   ├── services/                 # 业务逻辑层(16个)
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── map_service.py
│   │   ├── mapnet_service.py
│   │   ├── robot_service.py
│   │   ├── point_service.py
│   │   ├── item_service.py
│   │   ├── point_item_service.py
│   │   ├── task_service.py
│   │   ├── taskschedule_service.py
│   │   ├── taskhistory_service.py
│   │   ├── taskresult_service.py
│   │   ├── itemhistory_service.py
│   │   ├── alarmrule_service.py
│   │   ├── alarminfo_service.py
│   │   └── log_service.py
│   ├── ros/                      # ROS2集成
│   │   └── ros2_bridge.py        # ROS2桥接
│   ├── websocket/                # WebSocket通信
│   │   ├── connection_manager.py # 连接管理
│   │   └── handlers.py           # 消息处理
│   ├── utils/                    # 工具函数
│   │   ├── datetime_utils.py     # 时间工具
│   │   ├── response.py           # 响应工具
│   │   └── validators.py         # 验证工具
│   └── main.py                   # 应用入口
├── docs/                         # 项目文档
│   ├── api/                      # API模块文档(19个文件)
│   │   ├── README.md             # 模块索引
│   │   ├── 01_auth.md            # 认证相关(4个接口)
│   │   ├── 02_users.md           # 用户管理(6个接口)
│   │   ├── 03_maps.md            # 地图管理(6个接口)
│   │   ├── 04_mapnets.md         # 地图路网(7个接口)
│   │   ├── 05_robots.md          # 机器人(7个接口)
│   │   ├── 06_points.md          # 巡检点(7个接口)
│   │   ├── 07_items.md           # 巡检项目(7个接口)
│   │   ├── 08_point_items.md     # 点-项关联(10个接口)
│   │   ├── 09_tasks.md           # 任务(6个接口)
│   │   ├── 10_taskschedules.md   # 任务日程(7个接口)
│   │   ├── 11_taskhistories.md   # 任务记录(6个接口)
│   │   ├── 12_taskresults.md     # 任务结果(7个接口)
│   │   ├── 13_itemhistories.md   # 巡检记录(8个接口)
│   │   ├── 14_alarmrules.md      # 报警规则(7个接口)
│   │   ├── 15_alarminfos.md      # 报警信息(7个接口)
│   │   ├── 16_system.md          # 系统管理(2个接口)
│   │   ├── 17_logs.md            # 日志管理(6个接口)
│   │   └── 18_ros2.md            # ROS2通信(6个接口)
│   ├── README.md                 # 文档总索引
│   ├── API_QUICK_REFERENCE.md    # API快速参考
│   ├── API_FIELDS_REFERENCE.md   # 字段参考手册
│   ├── ERROR_CODES.md            # 错误码规范
│   ├── LOGGING_GUIDE.md          # 日志系统指南
│   ├── EXTERNAL_DEPLOYMENT_GUIDE.md # 外网部署指南
│   └── PROJECT_STRUCTURE.md      # 项目结构说明(本文件)
├── logs/                         # 日志文件（按日期分级）
│   └── YYYY-MM-DD/               # 每日日志目录
│       ├── app.log               # 业务审计日志
│       ├── error.log             # 错误日志
│       └── debug.log             # 调试日志
├── migrations/                   # 数据库迁移
│   └── README.md                 # 迁移说明
├── scripts/                      # 工具脚本
│   ├── init_database.sql         # 数据库初始化(15个表+示例数据)
│   ├── deploy_external.sh        # 外网部署脚本
│   └── README.md                 # 脚本使用说明
├── tests/                        # 测试工具
│   ├── login_test.html           # 登录功能测试页面
│   ├── log_download_test.html    # 日志管理测试页面
│   └── README.md                 # 测试工具说明
├── .cursorrules                  # Cursor AI开发规则
├── .env.example                  # 环境变量示例
├── .env.production               # 生产环境配置
├── .gitignore                    # Git忽略规则
├── requirements.txt              # Python依赖
├── README.md                     # 项目说明
├── STARTUP_GUIDE.md              # 完整启动指南(WSL环境搭建)
└── 启动说明.md                    # 快速启动命令
```

---

## 🏛️ 架构分层

### 1. API层 (`app/api/v1/`)
**职责**: 处理HTTP请求和响应
- 18个模块接口文件
- 参数验证和序列化
- 路由定义和权限装饰器

### 2. 服务层 (`app/services/`)
**职责**: 业务逻辑实现
- 16个业务服务类
- 事务管理
- 业务规则验证
- 日志记录

### 3. 数据访问层 (`app/repositories/`)
**职责**: 数据库操作封装
- 14个数据仓库类
- CRUD操作
- 复杂查询
- 分页处理

### 4. 模型层 (`app/models/`)
**职责**: ORM模型定义
- 15个SQLAlchemy模型
- 表结构定义
- 关系映射

### 5. 模式层 (`app/schemas/`)
**职责**: 数据验证和序列化
- 15个Pydantic模式
- 请求验证
- 响应格式化

---

## 📊 数据库表结构(15个表)

### 用户和会话
1. **tb_users** - 用户表
2. **tb_sessions** - 会话表

### 地图系统
3. **tb_map** - 地图表
4. **tb_mapnet** - 地图路网表
5. **tb_point** - 巡检点表

### 机器人和巡检
6. **tb_robot** - 机器人表
7. **tb_item** - 巡检项目表
8. **tb_point_item** - 点-项关联表(中间表)

### 任务系统
9. **tb_task** - 任务表
10. **tb_taskschedule** - 任务日程表
11. **tb_taskhistory** - 任务记录表
12. **tb_taskresult** - 任务结果表(1对1)
13. **tb_itemhistory** - 巡检记录表

### 报警系统
14. **tb_alarmrule** - 报警规则表
15. **tb_alarminfo** - 报警信息表

---

## 🔗 表关系说明

### 外键关系
```
tb_sessions → tb_users (user_id)

tb_mapnet → tb_map (map_id)
tb_point → tb_map (map_id)

tb_point_item → tb_point (point_id)
tb_point_item → tb_item (item_id)

tb_task → tb_map (map_id)
tb_task → tb_robot (robot_id)

tb_taskschedule → tb_task (task_id)
tb_taskhistory → tb_task (task_id)
tb_taskresult → tb_taskhistory (taskhistory_id) [1对1 UNIQUE]
tb_itemhistory → tb_taskhistory (taskhistory_id)
tb_itemhistory → tb_item (item_id)

tb_alarmrule → tb_item (item_id)
tb_alarminfo → tb_alarmrule (alarmrule_id)
tb_alarminfo → tb_itemhistory (itemhistory_id)
```

### 用户关系说明 ⭐
**重要**: 地图、机器人等业务资源**不关联user_id**
- ✅ 用户只用于：认证、授权、审计（created_by/updated_by）
- ❌ 用户不负责：资源所有权
- 📊 所有资源全局共享，通过角色控制权限

---

## 📋 API接口总览(119个)

### 认证相关 (4个)
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- POST /api/v1/auth/refresh
- GET /api/v1/auth/me

### 用户管理 (6个)
- POST /api/v1/users/
- GET /api/v1/users/
- GET /api/v1/users/{user_id}
- PUT /api/v1/users/{user_id}
- PUT /api/v1/users/updatepassword
- DELETE /api/v1/users/{user_id}

### 地图管理 (6个)
- POST /api/v1/maps/
- GET /api/v1/maps/
- GET /api/v1/maps/{map_id}
- PUT /api/v1/maps/{map_id}
- DELETE /api/v1/maps/{map_id}
- GET /api/v1/maps/stats/summary

### 其他模块
详见 [API模块文档](./api/README.md)

---

## 🔐 权限体系

### 角色层级
```
super_admin > admin > operator > viewer > user
```

### 权限级别
| 权限 | 可访问角色 | 适用接口 |
|------|-----------|---------|
| 🌐 public | 所有人 | 登录、健康检查 |
| 🔒 authenticated | 所有登录用户 | 登出、获取个人信息 |
| 👁️ read | super_admin, admin, operator, viewer, user | 所有GET查询接口 |
| ✏️ write | super_admin, admin, operator | 所有POST/PUT/DELETE修改接口 |
| 👑 admin+ | super_admin, admin | 用户管理、日志管理 |

---

## 📝 日志系统

### 日志文件结构
```
logs/
├── 2024-01-16/
│   ├── app.log          # 业务审计日志(时间-用户-操作-结果-详情)
│   ├── error.log        # 错误日志
│   └── debug.log        # 调试日志(仅开发环境)
```

### 日志特点
- 按日期自动分级管理
- 业务审计日志人类可读
- 文件自动轮转(10MB/文件)
- 支持日志清理和下载

---

## 🔢 错误码规范

| 错误码 | 含义 | 使用场景 |
|-------|------|---------|
| 200 | 请求成功 | 正常成功响应 |
| 210 | 登录成功需重置密码 | 首次登录 |
| 301 | 请求参数错误 | 参数验证失败 |
| 410 | Token验证失败 | Token过期/无效 |
| 414 | 登录失败 | 用户名或密码错误 |
| 999 | 系统异常 | 服务器内部错误 |

详细说明: [错误码文档](./ERROR_CODES.md)

---

## 📊 项目统计

| 项目 | 数量 |
|------|------|
| 数据库表 | 15个 |
| API接口 | 119个 |
| API模块 | 18个 |
| 模型文件 | 15个 |
| 服务文件 | 16个 |
| 仓库文件 | 14个 |
| 文档文件 | 25个 |

---

**最后更新**: 2024-01-16  
**维护者**: 博实智能巡检平台开发团队
