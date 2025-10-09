# 博实智能巡检平台

一个基于FastAPI和ROS2的智能巡检系统数据中台，支持用户认证、权限管理、ROS2通信和WebSocket实时通信。

## 🚀 项目特点

- **现代化架构**: 基于FastAPI的异步Web框架
- **ROS2集成**: 原生支持ROS2通信协议
- **实时通信**: WebSocket支持实时数据推送
- **权限管理**: 基于角色的访问控制(RBAC)
- **统一错误码**: 简化的错误处理体系
- **分层设计**: API → Service → Repository → Model

## 🏗️ 技术栈

- **后端框架**: FastAPI 0.104.1
- **数据库**: MySQL + SQLAlchemy (异步)
- **认证**: JWT + Session 管理
- **缓存**: Redis
- **机器人通信**: ROS2 (humble)
- **实时通信**: WebSocket
- **开发环境**: WSL2 + Python 3.10

## 📁 项目结构

```
D:\Project\boshi-inspection-platform\
├── app/                        # 主应用程序
│   ├── api/v1/                 # API路由层
│   ├── services/               # 业务逻辑层
│   ├── repositories/           # 数据访问层
│   ├── models/                 # 数据模型层
│   ├── schemas/                # Pydantic模式
│   ├── core/                   # 核心功能
│   ├── config/                 # 配置管理
│   ├── ros/                    # ROS2集成
│   ├── websocket/              # WebSocket通信
│   └── utils/                  # 工具函数
├── scripts/                    # 工具脚本
├── tests/                      # 测试代码
├── docs/                       # 项目文档
└── requirements.txt           # Python依赖
```

## 🔢 错误码规范

- **100**: 请求数据有误（数据验证、格式、密码等）
- **200**: 请求成功
- **210**: 登录成功但需重置密码
- **301**: 请求参数错误
- **400/403/404**: 业务错误（业务逻辑、权限、资源不存在）
- **410**: token验证失败（过期、无效、不存在等）
- **414**: 登录失败
- **999**: 系统异常

详细说明: [错误码文档](docs/ERROR_CODES.md)

## 🔐 权限体系

### 角色层级
- **super_admin**: 超级管理员（最高权限）
- **admin**: 管理员（用户管理权限）
- **operator**: 操作员（机器人操作权限）
- **viewer**: 观察员（只读权限）
- **user**: 普通用户（基础权限）

### 权限规则
- 高级别角色可以管理低级别角色
- 用户管理需要admin或super_admin权限
- ROS2操作需要operator或更高权限

## 🔌 API接口

### 认证接口
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 获取用户信息

### 用户管理
- `POST /api/v1/users/create` - 创建用户
- `GET /api/v1/users/` - 获取用户列表
- `PUT /api/v1/users/forceupdate` - 管理员强制更新
- `PUT /api/v1/users/updatepassword` - 用户修改密码
- `DELETE /api/v1/users/delete` - 删除用户

### 系统接口
- `GET /api/v1/system/health` - 健康检查
- `GET /api/v1/system/info` - 系统信息

### ROS2接口
- `GET /api/v1/ros2/topics` - 获取话题列表
- `GET /api/v1/ros2/status` - 获取ROS2状态
- `POST /api/v1/ros2/publish/*` - 发布消息

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
mysql -u root -p < scripts/init_database.sql
```

### 2. 配置环境

```bash
# 复制环境变量模板（如果需要自定义配置）
cp env.template .env

# 编辑配置（可选）
nano .env
```

### 3. 启动应用

```bash
# 在WSL中启动
cd /mnt/d/Project/boshi-inspection-platform
source /opt/ros/humble/setup.bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问应用

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/system/health
- **登录测试**: [tests/login_test.html](tests/login_test.html)

## 🧪 测试

### 健康检查
```bash
python scripts/health_check.py
```

### 登录测试
- 用户名: `admin`
- 密码: `admin`
- 角色: `super_admin`

## 📚 开发文档

- [项目结构说明](PROJECT_STRUCTURE.md)
- [错误码规范](docs/ERROR_CODES.md)
- [Cursor AI 开发规则](.cursorrules)

## 🔧 开发工具

- **数据库初始化**: `scripts/init_database.sql`
- **系统健康检查**: `scripts/health_check.py`
- **登录功能测试**: `tests/login_test.html`

## 📝 许可证

MIT License