# 博实智能巡检平台 - 日志系统使用指南

## 🎯 优化后的日志系统特性

### ✅ 已解决的问题

1. **前缀过长问题** - 采用分行显示，前缀与消息分离
2. **日志文件管理** - 按日期自动分级管理，便于维护

### 📋 新的日志格式

#### 控制台输出格式（简洁）
```
09:15:12 [INFO] app: 数据库初始化完成
09:15:12 [INFO] app.ros.ros2_bridge: ROS2 Bridge节点已启动
```

#### 文件日志格式（分行显示）
```
2025-09-18 09:15:12 [INFO] app
    数据库初始化完成
2025-09-18 09:15:12 [INFO] app.ros.ros2_bridge
    ROS2 Bridge节点已启动
```

#### 错误日志格式（详细信息）
```
2025-09-18 09:15:12 [ERROR] app.services.user_service
    Location: /path/to/file.py:123 in create_user()
    Message: 用户创建失败: 用户名已存在
    ---
```

## 📁 日志文件结构

```
logs/
├── 2025-09-18/          # 按日期分级
│   ├── app.log          # 主日志文件
│   ├── app_error.log    # 错误日志文件
│   └── app_debug.log    # 调试日志文件（仅开发环境）
├── 2025-09-17/
│   ├── app.log
│   ├── app_error.log
│   └── app_debug.log
└── ...
```

## 🔧 日志级别配置

### 不同模块的日志级别

| 模块 | 控制台级别 | 文件级别 | 说明 |
|------|------------|----------|------|
| `app.*` | INFO | INFO | 应用主日志 |
| `uvicorn` | INFO | INFO | Web服务器日志 |
| `uvicorn.access` | - | INFO | 访问日志（不输出到控制台） |
| `sqlalchemy.engine` | - | WARNING | 数据库日志（减少噪音） |
| `redis` | - | WARNING | Redis日志 |

### 开发环境 vs 生产环境

**开发环境** (`DEBUG=true`):
- 额外生成 `app_debug.log` 详细调试日志
- 包含函数名、行号等详细信息
- SQLAlchemy查询日志输出到debug文件

**生产环境** (`DEBUG=false`):
- 只保留必要的日志信息
- 不生成debug文件，节省空间
- 隐藏敏感的系统信息

## 🛠️ 日志管理工具

### 安装和使用

```bash
# 给脚本添加执行权限
chmod +x scripts/log_manager.py

# 查看帮助
python3 scripts/log_manager.py --help
```

### 可用命令

#### 1. 查看日志统计
```bash
python3 scripts/log_manager.py stats
```
输出示例：
```
📊 日志统计信息
========================================
日志目录数量: 3
总占用空间: 15.67 MB
日志目录列表: 2025-09-16, 2025-09-17, 2025-09-18

📁 今日日志目录: logs/2025-09-18/
  - app.log: 2.34 MB
  - app_debug.log: 1.23 MB
  - app_error.log: 0.45 MB
```

#### 2. 列出所有日志文件
```bash
python3 scripts/log_manager.py list
```

#### 3. 查看日志文件末尾
```bash
# 查看应用日志最后50行
python3 scripts/log_manager.py tail

# 查看错误日志最后100行
python3 scripts/log_manager.py tail --type error --lines 100

# 查看调试日志最后20行
python3 scripts/log_manager.py tail --type debug --lines 20
```

#### 4. 清理旧日志
```bash
# 清理7天前的日志（默认）
python3 scripts/log_manager.py cleanup

# 清理30天前的日志
python3 scripts/log_manager.py cleanup --days 30
```

## 📝 在代码中使用日志

### 基本用法

```python
from app.config.logging import get_logger

# 获取模块专用的logger
logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息：变量值为 %s", variable)
logger.info("用户登录成功")
logger.warning("配置文件缺少某个选项，使用默认值")
logger.error("数据库连接失败")
logger.critical("系统内存不足，即将崩溃")
```

### 结构化日志记录

```python
# 使用extra参数添加结构化信息
logger.info(
    "用户执行操作",
    extra={
        "user_id": "user123",
        "operation": "create_post",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
    }
)
```

### 异常日志记录

```python
try:
    # 业务逻辑
    result = risky_operation()
except Exception as e:
    logger.error(
        "操作失败: %s",
        str(e),
        extra={
            "operation": "risky_operation",
            "input_data": input_data
        },
        exc_info=True  # 自动包含异常堆栈
    )
    raise
```

### 性能日志记录

```python
import time

start_time = time.time()
try:
    # 执行操作
    result = expensive_operation()
    
    logger.info(
        "操作完成",
        extra={
            "operation": "expensive_operation",
            "duration_ms": round((time.time() - start_time) * 1000, 2),
            "result_count": len(result) if result else 0
        }
    )
except Exception as e:
    logger.error(
        "操作失败",
        extra={
            "operation": "expensive_operation", 
            "duration_ms": round((time.time() - start_time) * 1000, 2),
            "error": str(e)
        },
        exc_info=True
    )
```

## 🔍 日志分析建议

### 1. 日常监控
```bash
# 监控今日错误日志
tail -f logs/$(date +%Y-%m-%d)/app_error.log

# 查看应用启动日志
grep "应用启动" logs/$(date +%Y-%m-%d)/app.log

# 统计今日API请求数量
grep "请求完成" logs/$(date +%Y-%m-%d)/app.log | wc -l
```

### 2. 问题排查
```bash
# 查找特定错误
grep -r "数据库连接失败" logs/

# 查找特定用户的操作记录
grep -r "user_id.*user123" logs/

# 查看特定时间段的日志
sed -n '/09:00:00/,/10:00:00/p' logs/2025-09-18/app.log
```

### 3. 性能分析
```bash
# 查找处理时间较长的请求
grep "process_time.*[0-9]\{2,\}" logs/$(date +%Y-%m-%d)/app.log

# 统计不同API的调用次数
grep "请求开始" logs/$(date +%Y-%m-%d)/app.log | cut -d'"' -f4 | sort | uniq -c
```

## ⚙️ 配置调优

### 日志轮转配置

在 `app/config/logging.py` 中可以调整：

```python
"maxBytes": 10485760,  # 10MB，单文件最大大小
"backupCount": 3,      # 保留3个备份文件
```

### 清理策略

建议设置定时任务自动清理旧日志：

```bash
# 添加到crontab，每天凌晨2点清理30天前的日志
0 2 * * * cd /path/to/project && python3 scripts/log_manager.py cleanup --days 30
```

## 🚨 注意事项

1. **敏感信息**: 不要在日志中记录密码、token等敏感信息
2. **日志级别**: 生产环境建议使用INFO级别，避免过多DEBUG日志
3. **磁盘空间**: 定期清理旧日志，避免占用过多磁盘空间
4. **性能影响**: 避免在高频调用的函数中使用DEBUG级别日志

## 📈 日志监控集成

对于生产环境，建议集成专业的日志监控系统：

- **ELK Stack** (Elasticsearch + Logstash + Kibana)
- **Grafana + Loki**
- **Prometheus + Alertmanager**

可以将JSON格式的日志直接发送到这些系统进行分析和告警。
