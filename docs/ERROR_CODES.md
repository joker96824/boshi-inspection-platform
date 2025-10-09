# 🔢 错误码规范文档

## 📋 概述

本文档定义了博实智能巡检平台的统一错误码规范。采用简化的分类体系，具体错误信息通过 `message` 字段传达。

## 🎯 错误码分类

### 📊 简化的错误码规则

| 错误码范围 | 含义 | HTTP状态码 | 说明 |
|-----------|------|-----------|------|
| **200** | 请求成功 | 200 | 正常成功响应 |
| **210** | 登录成功，但需要重置密码 | 200 | 特殊成功状态 |
| **100** | 请求失败，请求数据有误 | 400 | 数据验证、格式等问题 |
| **301** | 请求参数错误 | 400 | URL参数、查询参数问题 |
| **4XX** | 认证授权和业务错误 | 401/403/404/429 | 用户权限、业务逻辑问题 |
| **999** | 系统异常 | 500 | 服务器内部错误 |

## 📝 详细错误码定义

### ✅ 成功状态码

| 错误码 | 含义 | HTTP状态码 | 说明 |
|-------|------|-----------|------|
| **200** | 请求成功 | 200 | 正常的成功响应 |
| **210** | 登录成功，但需要重置密码 | 200 | 首次登录或密码过期 |

### ❌ 数据和参数错误

| 错误码 | 含义 | HTTP状态码 | 使用场景 |
|-------|------|-----------|---------|
| **100** | 请求数据有误 | 400 | 数据验证失败、格式错误、必填字段缺失等 |
| **301** | 请求参数错误 | 400 | URL参数错误、查询参数缺失等 |

### 🔐 认证授权错误

| 错误码 | 含义 | HTTP状态码 | 使用场景 |
|-------|------|-----------|---------|
| **410** | token验证失败 | 401 | JWT令牌过期、无效、不存在等所有token相关问题 |
| **414** | 登录失败 | 401 | 用户名或密码错误 |

### 🏢 业务错误

| 错误码 | 含义 | HTTP状态码 | 使用场景 |
|-------|------|-----------|---------|
| **400** | 业务处理失败 | 400 | 通用业务逻辑错误 |
| **403** | 权限不足 | 403 | 用户权限不够执行操作 |
| **404** | 资源不存在 | 404 | 请求的资源不存在 |

### 💥 系统异常

| 错误码 | 含义 | HTTP状态码 | 使用场景 |
|-------|------|-----------|---------|
| **999** | 系统异常 | 500 | 数据库异常、ROS2异常、系统内部错误等 |

## 📤 响应格式规范

### ✅ 成功响应格式

```json
{
  "code": 200,
  "message": "请求成功",
  "data": {
    // 具体的响应数据
  }
}
```

### ❌ 错误响应格式

```json
{
  "code": 414,
  "message": "用户名或密码错误",
  "details": {
    "field": "password",
    "additional_info": "..."
  }
}
```

### 📄 分页响应格式

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [...],
    "pagination": {
      "total": 100,
      "page": 1,
      "size": 10,
      "pages": 10,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## 🎨 使用示例

### 后端异常使用

```python
from app.core.exceptions import (
    ValidationError, BusinessError, TokenError, LoginFailedError,
    PermissionDeniedError, ResourceNotFoundError, SystemError
)

# 数据验证错误 - 具体信息在message中
raise ValidationError("用户名格式不正确，只能包含字母和数字")
raise ValidationError("密码修改失败，新密码不能与旧密码相同")

# 业务逻辑错误 - 具体信息在message中
raise BusinessError("用户名 'admin' 已存在")

# Token相关错误 - 具体信息在message中
raise TokenError("用户登录信息过期，需要重新登录")
raise TokenError("不合法的token")

# 登录失败 - 具体信息在message中
raise LoginFailedError("用户名或密码错误")

# 权限不足 - 具体信息在message中
raise PermissionDeniedError("当前用户无权限删除其他管理员")

# 资源不存在 - 具体信息在message中
raise ResourceNotFoundError("用户 'user123' 不存在")

# 系统异常 - 具体信息在message中
raise SystemError("数据库连接超时")
```

### 前端错误处理

```javascript
function handleApiError(response) {
  const { code, message, details } = response;
  
  switch (code) {
    // 认证相关错误 - 跳转登录
    case 410:
      redirectToLogin(message);
      break;
      
    // 登录失败
    case 414:
      showLoginError(message);
      break;
      
      
    // 权限不足
    case 403:
      showPermissionError(message);
      break;
      
    // 数据验证错误
    case 100:
      showValidationError(message, details);
      break;
      
    // 参数错误
    case 301:
      showParameterError(message, details);
      break;
      
    // 业务错误
    case 400:
      showBusinessError(message);
      break;
      
    // 资源不存在
    case 404:
      showNotFoundError(message);
      break;
      
    // 系统异常
    case 999:
      showSystemError(message);
      break;
      
    default:
      showGenericError(message);
  }
}
```

## 📋 最佳实践

### 1. 错误码选择原则
- **优先使用通用错误码**：如 100、400、403、404、999
- **具体错误信息写在message中**：如 "用户名 'admin' 已存在"
- **特殊场景使用专用错误码**：如 410（token过期）、414（登录失败）

### 2. 消息编写原则
- **用户友好**：避免技术术语，使用用户能理解的语言
- **信息明确**：提供足够信息帮助用户了解问题
- **统一格式**：同类错误使用统一的消息格式

### 3. 异常抛出原则
```python
# ✅ 推荐：使用通用异常 + 具体消息
raise BusinessError("用户名 'admin' 已存在")
raise ValidationError("手机号格式不正确，请输入11位数字")
raise PermissionDeniedError("当前用户角色 'user' 无权限管理 'admin' 用户")

# ❌ 不推荐：创建过多具体异常类
raise UsernameExistsError("admin")  # 过于细化
raise PhoneFormatError("13800138000")  # 过于细化
```

### 4. 前端处理原则
- **按错误码分类处理**：相同错误码使用统一的处理逻辑
- **显示具体消息**：直接显示后端返回的message内容
- **提供用户指导**：根据错误类型提供相应的操作建议

## 🔄 版本更新

| 版本 | 更新日期 | 更新内容 |
|------|---------|----------|
| v2.0.0 | 2025-09-17 | 简化错误码分类，减少细分类型 |
| v1.0.0 | 2025-09-17 | 初始版本，详细错误码规范 |

---

**设计理念**: 简化分类，明确消息。通过减少错误码种类，降低系统复杂度，同时通过详细的错误消息确保信息的准确传达。