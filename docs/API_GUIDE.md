# 博实智能巡检平台 - API接口使用指南

## 🎯 概述

博实智能巡检平台提供完整的RESTful API接口，支持用户管理、认证授权、日志管理、ROS2通信和系统监控等功能。

### 📋 API基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: `v1`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON
- **文档地址**: http://localhost:8000/docs

### 🔐 认证说明

除登录接口外，所有API都需要在请求头中携带JWT Token：
```
Authorization: Bearer <your_jwt_token>
```

## 📚 API接口分类

### 1. 🔑 认证管理 (`/api/v1/auth`)

#### 1.1 用户登录
**接口**: `POST /api/v1/auth/login`

**请求参数**:
```json
{
  "username": "admin",
  "password": "admin"
}
```

**成功响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 2592000,
    "user": {
      "id": "user-uuid",
      "username": "admin",
      "role": "super_admin"
    }
  }
}
```

#### 1.2 用户登出
**接口**: `POST /api/v1/auth/logout`

**权限**: 需要登录

#### 1.3 刷新Token
**接口**: `POST /api/v1/auth/refresh`

**权限**: 需要登录

#### 1.4 获取当前用户信息
**接口**: `GET /api/v1/auth/me`

**权限**: 需要登录

### 2. 👥 用户管理 (`/api/v1/users`)

#### 2.1 创建用户
**接口**: `POST /api/v1/users/create`

**权限**: admin及以上

**请求参数**:
```json
{
  "username": "testuser",
  "password": "password123",
  "mobile": "12345678901",
  "email": "test@example.com"
}
```

**验证规则**:
- 用户名: 3-50字符，支持字母、数字、下划线、中文
- 密码: 6-50字符
- 手机号: 11位数字
- 邮箱: *@*.com格式（可选）

#### 2.2 获取用户列表
**接口**: `GET /api/v1/users/`

**权限**: admin及以上

**查询参数**:
- `skip`: 跳过条数（默认0）
- `limit`: 每页数量（默认100）

#### 2.3 获取指定用户
**接口**: `GET /api/v1/users/{user_id}`

**权限**: admin及以上

#### 2.4 强制更新用户
**接口**: `PUT /api/v1/users/forceupdate`

**权限**: admin及以上，只能修改权限级别低于自己的用户

**请求参数**:
```json
{
  "user_id": "target-user-id",
  "username": "newusername",
  "mobile": "12345678901",
  "email": "new@example.com",
  "role": "operator",
  "new_password": "newpassword"
}
```

#### 2.5 用户修改密码
**接口**: `PUT /api/v1/users/updatepassword`

**权限**: 登录用户

**请求参数**:
```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword"
}
```

#### 2.6 删除用户
**接口**: `DELETE /api/v1/users/delete`

**权限**: admin及以上，只能删除权限级别低于自己的用户

**请求参数**:
```json
{
  "user_id": "target-user-id"
}
```

**权限矩阵**:
| 调用者角色 | 可删除的目标角色 |
|------------|------------------|
| `super_admin` | `admin`, `operator`, `viewer`, `user` |
| `admin` | `operator`, `viewer`, `user` |
| 其他角色 | ❌ 无删除权限 |

### 3. 📝 日志管理 (`/api/v1/logs`)

#### 3.1 获取日志文件列表
**接口**: `GET /api/v1/logs/files`

**权限**: admin及以上

**查询参数**:
- `start_date`: 开始日期 (YYYY-MM-DD, 可选, 默认7天前)
- `end_date`: 结束日期 (YYYY-MM-DD, 可选, 默认今天)
- `log_type`: 日志类型 (app/error/debug/all, 默认app)
- `page`: 页码 (默认1)
- `size`: 每页数量 (默认20, 最大100)

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 15,
    "page": 1,
    "size": 20,
    "items": [
      {
        "filename": "app.log",
        "file_path": "logs/2025-09-18/app.log",
        "file_size": 2048576,
        "file_size_mb": 1.95,
        "created_at": "2025-09-18T09:00:00",
        "modified_at": "2025-09-18T10:30:00",
        "log_type": "app"
      }
    ]
  }
}
```

#### 3.2 在线阅读日志内容
**接口**: `GET /api/v1/logs/content`

**权限**: admin及以上

**查询参数**:
- `log_date`: 日志日期 (YYYY-MM-DD, 必填)
- `log_type`: 日志类型 (app/error/debug, 默认app)
- `start_line`: 开始行号 (默认1)
- `limit`: 读取行数 (默认100, 最大1000)
- `search_keyword`: 搜索关键词 (可选)

#### 3.3 下载日志文件
**接口**: `GET /api/v1/logs/download`

**权限**: admin及以上

**查询参数**:
- `log_date`: 日志日期 (YYYY-MM-DD, 必填)
- `log_type`: 日志类型 (app/error/debug, 默认app)

**特殊处理**: 使用文件快照策略，避免下载过程中文件被修改

#### 3.4 搜索日志内容
**接口**: `POST /api/v1/logs/search`

**权限**: admin及以上

#### 3.5 获取日志统计
**接口**: `GET /api/v1/logs/stats`

**权限**: admin及以上

#### 3.6 清理旧日志
**接口**: `POST /api/v1/logs/cleanup`

**权限**: admin及以上

### 4. 🤖 ROS2通信 (`/api/v1/ros2`)

#### 4.1 获取ROS2话题列表
**接口**: `GET /api/v1/ros2/topics`

**权限**: 登录用户

#### 4.2 发布字符串消息
**接口**: `POST /api/v1/ros2/publish/string`

**权限**: 登录用户

**请求参数**:
```json
{
  "data": "Hello ROS2",
  "topic": "/test_topic"
}
```

#### 4.3 发布整数消息
**接口**: `POST /api/v1/ros2/publish/int`

**权限**: 登录用户

#### 4.4 发布浮点数消息
**接口**: `POST /api/v1/ros2/publish/float`

**权限**: 登录用户

#### 4.5 发布速度命令
**接口**: `POST /api/v1/ros2/publish/cmd_vel`

**权限**: 登录用户

**请求参数**:
```json
{
  "linear_x": 1.0,
  "angular_z": 0.5
}
```

### 5. ⚙️ 系统管理 (`/api/v1/system`)

#### 5.1 健康检查
**接口**: `GET /api/v1/system/health`

**权限**: 无需认证

**响应示例**:
```json
{
  "code": 200,
  "message": "系统运行正常",
  "data": {
    "status": "healthy",
    "timestamp": "2025-09-18T10:30:00",
    "version": "1.0.0"
  }
}
```

#### 5.2 系统信息
**接口**: `GET /api/v1/system/info`

**权限**: admin及以上

## 🔧 前端集成示例

### JavaScript/TypeScript 示例

#### 认证相关
```javascript
// 登录获取Token
async function login(username, password) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });
  
  const result = await response.json();
  if (result.code === 200) {
    localStorage.setItem('token', result.data.access_token);
    return result.data;
  }
  throw new Error(result.message);
}

// 获取认证头
function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}
```

#### 用户管理
```javascript
// 创建用户
async function createUser(userData) {
  const response = await fetch('/api/v1/users/create', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(userData)
  });
  
  return await response.json();
}

// 获取用户列表
async function getUserList(page = 1, size = 20) {
  const response = await fetch(`/api/v1/users/?skip=${(page-1)*size}&limit=${size}`, {
    headers: getAuthHeaders()
  });
  
  return await response.json();
}

// 删除用户
async function deleteUser(userId) {
  const response = await fetch('/api/v1/users/delete', {
    method: 'DELETE',
    headers: getAuthHeaders(),
    body: JSON.stringify({ user_id: userId })
  });
  
  return await response.json();
}
```

#### 日志管理
```javascript
// 直接下载日志文件
async function downloadLog(logDate, logType = 'app') {
  try {
    const params = new URLSearchParams({
      log_date: logDate,
      log_type: logType
    });

    const response = await fetch(`/api/v1/logs/download?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error(`下载失败: ${response.status}`);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `boshi_inspection_${logDate}_${logType}.log`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(downloadUrl);
    
  } catch (error) {
    console.error('下载失败:', error);
  }
}

// 获取日志内容
async function getLogContent(logDate, logType = 'app', startLine = 1, limit = 100) {
  const params = new URLSearchParams({
    log_date: logDate,
    log_type: logType,
    start_line: startLine.toString(),
    limit: limit.toString()
  });
  
  const response = await fetch(`/api/v1/logs/content?${params}`, {
    headers: getAuthHeaders()
  });
  
  return await response.json();
}
```

#### ROS2通信
```javascript
// 发布ROS2消息
async function publishROS2String(data, topic = '/test_topic') {
  const response = await fetch('/api/v1/ros2/publish/string', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ data, topic })
  });
  
  return await response.json();
}

// 发布速度命令
async function publishCmdVel(linearX, angularZ) {
  const response = await fetch('/api/v1/ros2/publish/cmd_vel', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      linear_x: linearX,
      angular_z: angularZ
    })
  });
  
  return await response.json();
}
```

## 🎭 用户角色和权限

### 角色层级
```
super_admin > admin > operator > viewer > user
```

### 权限矩阵

| 功能 | super_admin | admin | operator | viewer | user |
|------|-------------|-------|----------|--------|------|
| 用户管理 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 日志管理 | ✅ | ✅ | ❌ | ❌ | ❌ |
| ROS2通信 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 系统信息 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 健康检查 | ✅ | ✅ | ✅ | ✅ | ✅ |

## 🚨 错误处理

### 统一错误格式
```json
{
  "code": 400,
  "message": "具体的错误信息",
  "details": {}
}
```

### 常见错误码
- **100**: 请求数据有误（验证失败）
- **200**: 请求成功
- **301**: 请求参数错误
- **403**: 权限不足
- **404**: 资源不存在
- **410**: Token验证失败
- **414**: 登录失败
- **999**: 系统异常

详细错误码说明请参考: [ERROR_CODES.md](ERROR_CODES.md)

## 🔌 WebSocket通信

### 连接信息
- **连接地址**: `ws://localhost:8000/ws`
- **认证方式**: 无需认证，直接连接
- **协议**: WebSocket (ws://)

### 基础连接示例

#### JavaScript 连接
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('WebSocket 连接已建立');
    // 发送心跳
    ws.send(JSON.stringify({ type: 'ping' }));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('收到消息:', message);
};

ws.onclose = () => {
    console.log('WebSocket 连接已关闭');
};

ws.onerror = (error) => {
    console.error('WebSocket 错误:', error);
};
```

### 消息格式

#### 发送消息格式
```json
{
  "type": "消息类型",
  "topic": "ROS2话题名（可选）",
  "data": "消息数据（可选）"
}
```

#### 接收消息格式
```json
{
  "type": "响应类型",
  "status": "success/error",
  "message": "响应消息",
  "data": "响应数据（可选）",
  "timestamp": 1234567890.123
}
```

### 支持的消息类型

#### 基础通信
| 消息类型 | 方向 | 说明 | 参数 |
|----------|------|------|------|
| `ping` | 客户端→服务器 | 心跳检测 | 无 |
| `pong` | 服务器→客户端 | 心跳响应 | `timestamp` |
| `get_connection_status` | 客户端→服务器 | 获取连接状态 | 无 |
| `connection_status` | 服务器→客户端 | 连接状态响应 | `total_connections`, `ros2_available` |

#### ROS2 通信
| 消息类型 | 方向 | 说明 | 参数 |
|----------|------|------|------|
| `get_ros2_topics` | 客户端→服务器 | 获取ROS2话题列表 | 无 |
| `ros2_topics_response` | 服务器→客户端 | ROS2话题列表响应 | `topics[]` |
| `publish_ros2_string` | 客户端→服务器 | 发布字符串消息 | `topic`, `data` |
| `publish_ros2_int` | 客户端→服务器 | 发布整数消息 | `topic`, `data` |
| `publish_ros2_float` | 客户端→服务器 | 发布浮点数消息 | `topic`, `data` |
| `publish_ros2_cmd_vel` | 客户端→服务器 | 发布速度命令 | `data: {linear_x, angular_z}` |

#### 响应消息
| 消息类型 | 方向 | 说明 | 参数 |
|----------|------|------|------|
| `response` | 服务器→客户端 | 操作响应 | `status`, `message` |
| `error` | 服务器→客户端 | 错误响应 | `message` |
| `server_shutdown` | 服务器→客户端 | 服务器关闭通知 | `message` |

### 使用示例

#### 1. 心跳检测
```javascript
// 发送心跳
ws.send(JSON.stringify({ type: 'ping' }));

// 接收响应
// {"type": "pong", "timestamp": 1234567890.123}
```

#### 2. 获取 ROS2 话题列表
```javascript
// 发送请求
ws.send(JSON.stringify({ type: 'get_ros2_topics' }));

// 接收响应
// {"type": "ros2_topics_response", "topics": ["/topic1", "/topic2"]}
```

#### 3. 发布 ROS2 消息
```javascript
// 发布字符串消息
ws.send(JSON.stringify({
    type: 'publish_ros2_string',
    topic: '/test_topic',
    data: 'Hello ROS2!'
}));

// 发布速度命令
ws.send(JSON.stringify({
    type: 'publish_ros2_cmd_vel',
    data: {
        linear_x: 0.5,  // 前进速度
        angular_z: 0.2  // 转向速度
    }
}));
```

#### 4. 获取连接状态
```javascript
// 发送请求
ws.send(JSON.stringify({ type: 'get_connection_status' }));

// 接收响应
// {"type": "connection_status", "total_connections": 2, "ros2_available": true}
```

### React 组件示例

```jsx
import React, { useState, useEffect, useRef } from 'react';

const WebSocketComponent = () => {
    const [ws, setWs] = useState(null);
    const [connected, setConnected] = useState(false);
    const [messages, setMessages] = useState([]);
    const wsRef = useRef(null);

    useEffect(() => {
        const websocket = new WebSocket('ws://localhost:8000/ws');
        
        websocket.onopen = () => {
            setConnected(true);
            setWs(websocket);
            wsRef.current = websocket;
        };

        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            setMessages(prev => [...prev, message]);
        };

        websocket.onclose = () => {
            setConnected(false);
            setWs(null);
        };

        return () => websocket.close();
    }, []);

    const sendMessage = (message) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        }
    };

    return (
        <div>
            <h3>WebSocket 状态: {connected ? '已连接' : '未连接'}</h3>
            <button onClick={() => sendMessage({ type: 'ping' })}>
                发送心跳
            </button>
            <button onClick={() => sendMessage({ type: 'get_ros2_topics' })}>
                获取 ROS2 话题
            </button>
            {/* 消息显示区域 */}
        </div>
    );
};
```

### 实时数据流

#### 机器人数据 → 前端
```
机器人 → ROS2话题 → 服务器ROS2Bridge → WebSocket → 前端
```

**支持的数据类型**:
- **字符串消息**: `/bridge/string_out`
- **整数消息**: `/bridge/int_out`  
- **浮点数消息**: `/bridge/float_out`
- **激光雷达数据**: `/scan`

**前端接收格式**:
```json
{
  "type": "string_message|int_message|float_message|laser_scan",
  "topic": "/bridge/string_out",
  "data": "实际数据",
  "timestamp": 1234567890.123
}
```

#### 前端控制 → 机器人
```
前端 → WebSocket/HTTP → 服务器 → ROS2话题 → 机器人
```

**支持的控制类型**:
- **速度控制**: `publish_ros2_cmd_vel`
- **字符串命令**: `publish_ros2_string`
- **数值命令**: `publish_ros2_int/float`

### 注意事项

1. **连接稳定性**: 建议实现自动重连机制
2. **心跳检测**: 定期发送 `ping` 消息保持连接活跃
3. **错误处理**: 监听 `error` 类型消息进行错误处理
4. **ROS2 依赖**: ROS2 功能需要后端正确配置 ROS2 环境
5. **消息队列**: 考虑实现消息队列避免消息丢失
6. **实时性**: ROS2 消息会自动转发到所有连接的 WebSocket 客户端

## 🧪 测试工具

### 1. Swagger UI
访问 http://localhost:8000/docs 使用交互式API文档

### 2. 测试页面
- **登录测试**: `tests/login_test.html`
- **日志下载测试**: `tests/log_download_test.html`

### 3. curl命令示例
```bash
# 登录获取Token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 获取用户列表
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 下载日志文件
curl -X GET "http://localhost:8000/api/v1/logs/download?log_date=2025-09-18&log_type=app" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o "downloaded_log.log"
```

## 📱 移动端集成

### React Native 示例
```javascript
// 使用fetch进行API调用
const apiCall = async (endpoint, options = {}) => {
  const token = await AsyncStorage.getItem('token');
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  
  return await response.json();
};

// 登录
const login = async (username, password) => {
  return await apiCall('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
};
```

## 🔄 状态码说明

### HTTP状态码
- **200**: 成功
- **400**: 请求错误
- **401**: 未认证
- **403**: 权限不足
- **404**: 资源不存在
- **500**: 服务器错误

### 业务状态码
所有响应都包含业务状态码 `code` 字段，详见错误码文档。

## 📈 性能建议

### 1. 分页查询
对于列表接口，建议使用分页参数控制返回数据量

### 2. 缓存策略
- Token缓存: 本地存储JWT Token
- 数据缓存: 适当缓存不常变化的数据

### 3. 错误处理
```javascript
// 统一错误处理
function handleApiError(response) {
  const { code, message } = response;
  
  switch (code) {
    case 410:
      // Token过期，跳转登录
      redirectToLogin();
      break;
    case 403:
      showError('权限不足');
      break;
    default:
      showError(message);
  }
}
```

## 🔗 相关文档

- [项目结构说明](../PROJECT_STRUCTURE.md)
- [错误码规范](ERROR_CODES.md)
- [日志系统指南](LOGGING_GUIDE.md)
- [启动指南](../STARTUP_GUIDE.md)

---

**文档版本**: v1.0.0  
**最后更新**: 2025-09-18  
**维护者**: 开发团队
