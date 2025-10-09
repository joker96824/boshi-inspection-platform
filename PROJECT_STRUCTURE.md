# 🏗️ 博实智能巡检平台 - 项目结构说明

## 📁 目录结构

```
D:\Project\boshi-inspection-platform\
├── app/                        # 主应用程序
│   ├── api/                    # API路由层
│   │   └── v1/                 # API v1版本
│   │       ├── auth.py         # 认证相关接口
│   │       ├── users.py        # 用户管理接口
│   │       ├── ros2.py         # ROS2相关接口
│   │       └── system.py       # 系统信息接口
│   ├── config/                 # 配置管理
│   │   ├── database.py         # 数据库配置
│   │   ├── logging.py          # 统一日志配置（按日期分级）
│   │   ├── redis.py           # Redis配置
│   │   └── settings.py         # 应用设置
│   ├── core/                   # 核心功能
│   │   ├── app_factory.py      # 应用工厂（全局异常处理器）
│   │   ├── auth.py             # 认证逻辑
│   │   ├── deps.py             # 依赖注入
│   │   ├── error_codes.py      # 统一错误码定义
│   │   ├── exceptions.py       # 统一异常类体系
│   │   ├── middleware.py       # 中间件（日志、安全等）
│   │   ├── permissions.py      # 权限管理
│   │   └── security.py         # 安全工具
│   ├── models/                 # 数据模型层
│   │   ├── base.py             # 基础模型
│   │   ├── user.py             # 用户模型
│   │   └── session.py          # 会话模型
│   ├── repositories/           # 数据访问层
│   │   └── user_repository.py  # 用户数据仓库
│   ├── schemas/                # Pydantic模式
│   │   ├── base.py             # 基础模式
│   │   ├── user.py             # 用户模式
│   │   └── session.py          # 会话模式
│   ├── services/               # 业务逻辑层
│   │   ├── auth_service.py     # 认证服务
│   │   └── user_service.py     # 用户服务
│   ├── ros/                    # ROS2集成
│   │   └── ros2_bridge.py      # ROS2桥接
│   ├── websocket/              # WebSocket通信
│   │   ├── connection_manager.py # 连接管理
│   │   └── handlers.py         # 消息处理
│   ├── utils/                  # 工具函数
│   │   ├── datetime_utils.py   # 时间工具
│   │   ├── response.py         # 响应工具
│   │   └── validators.py       # 验证工具
│   └── main.py                 # 应用入口
├── docker/                     # Docker配置
├── docs/                       # 项目文档
│   └── ERROR_CODES.md          # 错误码规范文档
├── logs/                       # 日志文件（按日期分级）
│   └── YYYY-MM-DD/             # 每日日志目录
│       ├── app.log             # 主日志文件
│       ├── app_error.log       # 错误日志文件
│       └── app_debug.log       # 调试日志文件（仅开发环境）
├── migrations/                 # 数据库迁移
├── scripts/                    # 工具脚本
│   ├── init_database.sql       # 数据库初始化SQL
│   ├── log_manager.py          # 日志管理工具
│   └── health_check.py         # 系统健康检查
├── tests/                      # 测试代码
│   └── login_test.html         # 登录测试页面
├── .cursorrules               # Cursor AI 开发规则
├── requirements.txt           # Python依赖
└── PROJECT_STRUCTURE.md       # 项目结构说明
```

## 🏛️ 架构分层

### 1. **API层** (`app/api/`)
- 处理HTTP请求和响应
- 参数验证和序列化
- 路由定义

### 2. **服务层** (`app/services/`)
- 业务逻辑实现
- 事务管理
- 跨领域协调

### 3. **仓库层** (`app/repositories/`)
- 数据访问抽象
- SQL查询封装
- 数据持久化

### 4. **模型层** (`app/models/`)
- 数据库表结构定义
- ORM映射
- 数据关系

## 🔧 核心组件

### **认证系统**
- JWT令牌管理
- 用户会话控制
- 权限验证

### **权限管理**
- 基于角色的访问控制(RBAC)
- 角色层级: `super_admin` > `admin` > `operator` > `viewer` > `user`
- 细粒度权限检查

### **ROS2集成**
- 话题发布/订阅
- 消息类型支持
- WebSocket桥接

### **WebSocket通信**
- 实时消息推送
- 连接管理
- ROS2消息广播

## 📋 数据模型

### **用户表** (`users`)
```sql
- id: 用户唯一标识
- username: 用户名
- password_hash: 密码哈希
- mobile: 手机号
- email: 邮箱
- role: 角色
- last_login_at: 最后登录时间
```

### **会话表** (`sessions`)
```sql
- id: 会话唯一标识
- user_id: 用户ID
- token: JWT令牌
- expires_at: 过期时间
```

## 🛠️ 开发工具

### **脚本工具** (`scripts/`)
- `init_db.py`: 数据库初始化
- `health_check.py`: 系统健康检查

### **数据库迁移** (`migrations/`)
- Alembic迁移文件
- 版本控制和升级

## 🚀 启动方式

### **开发环境**
```bash
# 在WSL中启动
wsl -d Ubuntu-22.04 -e bash -c "cd /mnt/d/Project/boshi-inspection-platform && source /opt/ros/humble/setup.bash && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# 或者在WSL shell中直接运行
cd /mnt/d/Project/boshi-inspection-platform
source /opt/ros/humble/setup.bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **健康检查**
```bash
python scripts/health_check.py
```

## 🔍 API接口

### **认证接口**
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 获取用户信息

### **用户管理**
- `POST /api/v1/users/create` - 创建用户
- `GET /api/v1/users/` - 获取用户列表
- `PUT /api/v1/users/forceupdate` - 管理员强制更新
- `PUT /api/v1/users/updatepassword` - 用户修改密码
- `DELETE /api/v1/users/delete` - 删除用户

### **系统接口**
- `GET /api/v1/system/health` - 健康检查
- `GET /api/v1/system/info` - 系统信息

### **ROS2接口**
- `GET /api/v1/ros2/topics` - 获取话题列表
- `POST /api/v1/ros2/publish/*` - 发布消息

## 🔐 安全特性

- JWT令牌认证
- 密码哈希存储
- 会话管理
- CORS保护
- 安全头设置
- 请求日志记录

## 🔢 统一错误码规范

- **简化的错误码体系**: 减少分类复杂度，通过message传达具体信息
- **标准化响应格式**: 统一的成功/错误响应结构
- **分层错误处理**: API → Service → Repository 各层异常处理
- **前端友好**: 简单的错误码分类，详细的错误消息

**简化错误码分类**:
- **100**: 请求数据有误（数据验证、格式、密码重置/修改等）
- **200**: 请求成功
- **210**: 登录成功但需重置密码
- **301**: 请求参数错误
- **410**: token验证失败（过期、无效、不存在等）
- **414**: 登录失败
- **400/403/404**: 业务错误（业务逻辑、权限、资源不存在）
- **999**: 系统异常

**设计理念**: 通过减少错误码种类降低复杂度，具体错误信息通过message字段详细说明。

详细说明请参考: [`docs/ERROR_CODES.md`](docs/ERROR_CODES.md)

## 📊 监控和日志

### 统一日志系统
- **按日期分级管理**: `logs/YYYY-MM-DD/` 目录结构
- **多种日志格式**: 控制台简洁格式、文件分行格式、错误详细格式
- **分类日志文件**: 主日志、错误日志、调试日志
- **自动日志轮转**: 10MB文件限制，保留3个备份
- **日志管理工具**: 提供统计、清理、查看功能

### 日志使用方式
```python
from app.config.logging import get_logger
logger = get_logger(__name__)

# 结构化日志记录
logger.info("用户操作", extra={
    "user_id": "user123",
    "operation": "login",
    "ip": "192.168.1.1"
})
```

### 异常监控
- **全局异常处理**: 自动捕获并记录所有异常
- **结构化错误信息**: 包含请求ID、路径、方法等上下文
- **环境区分**: 开发环境显示详细信息，生产环境隐藏敏感信息
- **请求追踪**: 每个请求自动生成唯一ID用于链路追踪

## 🤖 AI 开发辅助

### **Cursor AI 规则** (`.cursorrules`)
- 定义项目的架构模式和编码规范
- 指导 AI 生成符合项目风格的代码
- 包含常用代码模板和最佳实践
- 自动化代码生成的质量保证

**主要内容**:
- 项目架构说明
- 编码规范和命名约定
- FastAPI 特定规范
- 数据库操作模式
- 认证权限模式
- ROS2 集成模式
- WebSocket 处理模式
- 错误处理和日志记录
- 安全考虑和性能优化
