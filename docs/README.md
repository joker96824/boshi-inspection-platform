# 文档目录

## 📚 文档概览

本目录包含博实智能巡检平台的完整技术文档。

已为平台创建 **18个模块，119个接口** 的完整文档。

---

## 🎯 快速导航

### API文档（最常用）⭐
- 📖 **[API快速参考](./API_QUICK_REFERENCE.md)** - 接口速查表
- 🧪 **[API测试数据](./API_TEST_DATA.md)** - Swagger测试参数手册

### 系统文档
- 🏗️ **[项目结构说明](./PROJECT_STRUCTURE.md)** - 完整的项目结构和架构
- 🔢 **[错误码规范](./ERROR_CODES.md)** - 统一错误码定义
- 📝 **[日志系统指南](./LOGGING_GUIDE.md)** - 日志配置和使用
- 🌐 **[外网部署指南](./EXTERNAL_DEPLOYMENT_GUIDE.md)** - 生产环境部署

### ROS2通信文档
- 🤖 **[ROS2集成架构详解](./ROS2_INTEGRATION_ARCHITECTURE.md)** - ROS2通信实现原理
- 🔌 **[ROS2通信指南](./ROS2_COMMUNICATION_GUIDE.md)** - ROS2使用和配置

---

## 📖 文档说明

### 1. API快速参考 (`API_QUICK_REFERENCE.md`)
- 119个接口的快速查找表
- 按模块分类
- 权限说明
- 适合快速查找接口

### 2. API测试数据 (`API_TEST_DATA.md`)
- 每个接口的测试参数
- 适合在Swagger文档页面测试
- 提供可用的示例ID和JSON数据

### 3. 项目结构说明 (`PROJECT_STRUCTURE.md`)
- 完整的目录结构
- 架构分层说明
- 数据库表关系
- 接口总览

### 4. 错误码规范 (`ERROR_CODES.md`)
- 统一错误码定义
- 错误处理规范
- 适合前端错误处理

### 5. 日志系统指南 (`LOGGING_GUIDE.md`)
- 分层日志策略
- 日志文件结构
- 适合日志配置和问题排查

### 6. 外网部署指南 (`EXTERNAL_DEPLOYMENT_GUIDE.md`)
- 生产环境部署步骤
- 防火墙、Nginx配置
- 适合运维人员

### 7. ROS2集成架构详解 (`ROS2_INTEGRATION_ARCHITECTURE.md`) ⭐
- ROS2通信实现原理
- Spin机制详解
- 线程安全和性能优化
- 适合理解ROS2集成

### 8. ROS2通信指南 (`ROS2_COMMUNICATION_GUIDE.md`)
- ROS2使用方法
- 测试步骤
- 调试技巧
- 适合快速上手

---

## 📝 API规范

### 响应格式
```json
{
  "code": 200,
  "message": "操作描述",
  "data": {}
}
```

### 权限标识
```
🌐 无需认证
🔒 需要认证
👁️ read权限
✏️ write权限
👑 admin+权限
```

### 时间格式
- ISO 8601: `2024-01-16T10:30:15`
- Unix时间戳: `1705392000`

### ID格式
- UUID: `550e8400-e29b-41d4-a716-446655440000`

---

## 🎯 使用建议

### 前端开发
1. 查看 **[API快速参考](./API_QUICK_REFERENCE.md)** 了解所有接口
2. 使用 **[API测试数据](./API_TEST_DATA.md)** 在Swagger测试
3. 参考 **[错误码规范](./ERROR_CODES.md)** 处理错误

### 后端开发
1. 查看 **[项目结构说明](./PROJECT_STRUCTURE.md)** 了解架构
2. 遵循 **[错误码规范](./ERROR_CODES.md)** 统一错误处理
3. 参考 **[日志系统指南](./LOGGING_GUIDE.md)** 添加日志

### 运维部署
1. 使用 **[外网部署指南](./EXTERNAL_DEPLOYMENT_GUIDE.md)** 进行部署
2. 参考 **[日志系统指南](./LOGGING_GUIDE.md)** 管理日志

### 接口测试
1. 访问 http://localhost:8000/docs 打开Swagger
2. 使用 **[API测试数据](./API_TEST_DATA.md)** 提供的参数测试
3. 或使用 `tests/login_test.html` 可视化测试页面

---

## 📊 文档统计

| 文档类型 | 数量 |
|---------|------|
| API文档 | 2个 |
| 系统文档 | 4个 |
| ROS2文档 | 2个 |
| **总计** | **8个** |

---

## 🔄 维护建议

1. API变更时同步更新快速参考表
2. 新增接口时更新测试数据手册
3. 重大变更时更新项目结构文档

---

## 📞 联系方式

如有文档问题或建议，请联系：
- **项目**: 博实智能巡检平台
- **维护者**: 开发团队

---

**最后更新**: 2024-01-16
