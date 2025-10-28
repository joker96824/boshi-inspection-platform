# 🤖 博实智能巡检平台

一个基于 FastAPI 和 ROS2 的智能巡检系统数据中台，支持用户认证、权限管理、ROS2 通信和 WebSocket 实时通信。

---

## ✨ 项目特点

- 🚀 **现代化架构**: 基于 FastAPI 的异步 Web 框架
- 🤖 **ROS2 集成**: 原生支持 ROS2 通信协议
- ⚡ **实时通信**: WebSocket 支持实时数据推送
- 🔐 **权限管理**: 基于角色的访问控制(RBAC)
- 📝 **统一日志**: 分层日志策略（业务审计/错误/调试）
- 🔢 **统一错误码**: 简化的错误处理体系
- 📊 **完整文档**: 119个API接口的详细文档

---

## 🏗️ 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | FastAPI 0.104.1 |
| **数据库** | MySQL 8.0+ + SQLAlchemy (异步) |
| **认证** | JWT + Session 管理 |
| **缓存** | Redis |
| **机器人通信** | ROS2 Humble |
| **实时通信** | WebSocket |
| **开发环境** | WSL2 + Ubuntu 22.04 + Python 3.10 |

---

## 🎯 核心功能

### 1. 用户认证和权限
- ✅ JWT Token认证（有效期30天）
- ✅ 基于角色的权限控制（5种角色）
- ✅ 会话管理和安全登出
- ✅ 操作审计日志

### 2. 地图和巡检管理
- ✅ 地图管理（名称、图片、比例、坐标）
- ✅ 地图路网管理（点、线、矩形）
- ✅ 巡检点管理
- ✅ 巡检项目管理
- ✅ 点-项多对多关联

### 3. 机器人和任务
- ✅ 机器人信息管理
- ✅ 任务配置和调度
- ✅ 任务执行记录
- ✅ 任务结果管理
- ✅ 巡检记录管理

### 4. 报警系统
- ✅ 报警规则配置
- ✅ 报警信息记录

### 5. 系统管理
- ✅ 系统信息查询
- ✅ 健康检查接口
- ✅ 日志查询和下载
- ✅ ROS2 消息发布

---

## 🚀 快速开始

### 前置要求
- Windows 10/11
- WSL2 + Ubuntu 22.04
- MySQL 8.0+
- Python 3.10+
- ROS2 Humble（可选）

### 1. 初始化数据库
```bash
wsl -e bash -c "mysql -u root -proot < scripts/init_database.sql"
```

### 2. 启动服务
```bash
# 本地启动
wsl -e bash -c "cd /mnt/d/Project/boshi/boshi-inspection-platform && source /opt/ros/humble/setup.bash && export ROS_DOMAIN_ID=0 && python3 -m app.main"
```

### 3. 访问服务
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/system/health
- **登录测试**: 打开 `tests/login_test.html`

### 4. 默认账号
| 用户名 | 密码 | 角色 |
|--------|------|------|
| superadmin | superadmin | super_admin |
| admin | admin | admin |
| operator | operator | operator |

---

## 📚 文档导航

### 🎯 推荐文档（按使用场景）

#### 前端开发
1. **[API快速参考](docs/API_QUICK_REFERENCE.md)** - 接口速查表 ⭐
2. **[API测试数据](docs/API_TEST_DATA.md)** - Swagger测试参数 ⭐⭐
3. **[错误码规范](docs/ERROR_CODES.md)** - 错误处理

#### 后端开发
1. **[项目结构说明](docs/PROJECT_STRUCTURE.md)** - 完整的项目结构 ⭐
2. **[错误码规范](docs/ERROR_CODES.md)** - 错误处理
3. **[日志系统指南](docs/LOGGING_GUIDE.md)** - 日志配置

#### 部署运维
1. **[完整启动指南](STARTUP_GUIDE.md)** - WSL环境搭建 ⭐⭐⭐
2. **[外网部署指南](docs/EXTERNAL_DEPLOYMENT_GUIDE.md)** - 生产环境部署
3. **[脚本使用说明](scripts/README.md)** - 工具脚本

#### 测试
1. **[测试工具说明](tests/README.md)** - 可视化测试页面
2. 打开 `tests/login_test.html` - 登录功能测试
3. 打开 `tests/log_download_test.html` - 日志管理测试

### 📖 完整文档列表
详见 **[docs/README.md](docs/README.md)**

---

## 🏛️ 架构设计

### 分层架构
```
┌─────────────────────────────────────────┐
│  API Layer (app/api/v1/)                │
│  ├─ 18个模块接口文件                     │
│  └─ 处理HTTP请求、参数验证、路由定义      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  Service Layer (app/services/)          │
│  ├─ 16个业务服务类                       │
│  └─ 业务逻辑、事务管理、日志记录          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  Repository Layer (app/repositories/)   │
│  ├─ 14个数据仓库类                       │
│  └─ 数据库操作、CRUD、分页查询           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  Model Layer (app/models/)              │
│  ├─ 15个SQLAlchemy模型                  │
│  └─ 表结构定义、关系映射                 │
└─────────────────────────────────────────┘
```

### 核心组件
- **认证系统**: JWT + Session双重验证
- **权限系统**: RBAC角色权限控制
- **日志系统**: 分层日志（业务/错误/调试）
- **异常系统**: 统一异常处理和错误码
- **ROS2集成**: 消息发布和订阅
- **WebSocket**: 实时双向通信

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

详细说明: [错误码文档](docs/ERROR_CODES.md)

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
| 文档文件 | 27个 |

---

## 🔧 开发规范

### 编码规范
- 遵循 PEP 8 标准
- 使用 type hints
- 所有函数必须有文档字符串
- 详见 `.cursorrules`

### API设计规范
- RESTful API设计
- 统一响应格式
- 统一错误处理
- 详见 [API完整参考](docs/API_REFERENCE.md)

### 数据库规范
- SQLAlchemy 2.0 异步语法
- Repository 模式
- 软删除机制
- 详见 [项目结构说明](PROJECT_STRUCTURE.md)

---

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码（遵循编码规范）
4. 推送到分支
5. 创建 Pull Request

---

## 📞 技术支持

### 常见问题
- 启动问题 → 查看 [STARTUP_GUIDE.md](STARTUP_GUIDE.md)
- API问题 → 查看 [API模块文档](docs/api/README.md)
- 部署问题 → 查看 [EXTERNAL_DEPLOYMENT_GUIDE.md](docs/EXTERNAL_DEPLOYMENT_GUIDE.md)

### 联系方式
- **项目**: 博实智能巡检项目组
- **维护者**: 博实智能巡检项目组

---

## 📄 许可证

请参考项目许可证文件。

---

**最后更新**: 2024-01-16  
**项目状态**: ✅ 生产就绪