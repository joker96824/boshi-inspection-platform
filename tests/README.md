# 测试工具说明

## 📋 可视化测试页面

本目录包含两个HTML可视化测试页面，用于快速测试和验证API功能。

---

## 🔐 登录功能测试页面

### 文件
`login_test.html`

### 功能
- 🔐 用户登录测试
- 💾 Token自动存储到localStorage
- 📊 显示登录响应数据（包括expires_in、last_login_at等字段）
- 🔧 提供控制台测试函数

### 使用方法

1. **启动后端服务**
   ```bash
   cd D:\Project\boshi\boshi-inspection-platform
   python -m app.main
   ```

2. **打开测试页面**
   - 双击或在浏览器中打开 `tests/login_test.html`
   - 默认账号已填充：admin / admin

3. **测试登录**
   - 点击"登录"按钮
   - 查看响应数据
   - Token会自动保存到localStorage

4. **控制台测试函数**（F12打开开发者工具）
   ```javascript
   // 测试健康检查接口
   testHealthAPI()
   
   // 测试获取用户信息（需要先登录）
   testMe()
   
   // 刷新访问令牌
   refreshToken()
   
   // 用户登出
   logout()
   
   // 查看保存的Token
   localStorage.getItem("access_token")
   ```

### 测试的API接口
- ✅ `POST /api/v1/auth/login` - 用户登录
- ✅ `POST /api/v1/auth/logout` - 用户登出
- ✅ `POST /api/v1/auth/refresh` - 刷新令牌
- ✅ `GET /api/v1/auth/me` - 获取当前用户信息
- ✅ `GET /api/v1/system/health` - 系统健康检查

### 验证要点
- ✅ `expires_in` 字段：2592000秒（30天）
- ✅ `last_login_at` 字段：最后登录时间
- ✅ `token_type` 字段：bearer
- ✅ Token格式：JWT格式

---

## 📄 日志管理测试页面

### 文件
`log_download_test.html`

### 功能
- 📋 查询日志文件列表
- 📖 在线阅读日志内容
- ⬇️ 下载日志文件
- 🔍 搜索日志内容（按关键词）
- 🗑️ 清理旧日志

### 使用方法

1. **获取Token**
   - 先使用 `login_test.html` 登录
   - 复制获取的 access_token

2. **打开测试页面**
   - 在浏览器中打开 `tests/log_download_test.html`
   - 粘贴Token到输入框

3. **测试日志功能**
   - 查询日志文件列表
   - 选择日志文件在线阅读
   - 下载日志文件到本地
   - 搜索特定关键词

### 测试的API接口
- ✅ `GET /api/v1/logs/files` - 获取日志文件列表
- ✅ `GET /api/v1/logs/read` - 在线阅读日志
- ✅ `GET /api/v1/logs/download` - 下载日志文件
- ✅ `GET /api/v1/logs/search` - 搜索日志内容
- ✅ `DELETE /api/v1/logs/cleanup` - 清理旧日志
- ✅ `GET /api/v1/logs/stats` - 日志统计

### 验证要点
- ✅ 日志文件按日期分类
- ✅ 支持日期范围查询
- ✅ 文件大小人性化显示
- ✅ 下载功能正常
- ✅ 搜索功能准确

---

## 🔐 权限要求

| 测试页面 | 所需权限 | 可用账号 |
|---------|---------|---------|
| login_test.html | 🌐 无需认证 | 任意账号 |
| log_download_test.html | 👑 admin+ | superadmin, admin |

---

## 🎯 测试场景

### 基础场景
1. **登录流程**
   - 使用不同角色账号登录
   - 验证Token获取和存储
   - 验证expires_in字段（30天）

2. **令牌刷新**
   - 刷新Token
   - 验证新Token有效性
   - 验证旧Token失效

3. **用户信息**
   - 获取当前用户信息
   - 验证last_login_at字段

### 高级场景
1. **日志查询**
   - 按日期查询日志文件
   - 按日期范围查询
   - 验证分页功能

2. **日志阅读**
   - 在线阅读不同类型的日志
   - 验证日志格式（业务审计格式）

3. **日志下载**
   - 下载小文件（<1MB）
   - 下载大文件（>5MB）
   - 验证文件完整性

---

## 📞 技术支持

如测试中发现问题，请参考：
- **API文档**: `docs/API_REFERENCE.md`
- **详细文档**: `docs/api/01-18.md`
- **字段参考**: `docs/API_FIELDS_REFERENCE.md`
- **快速参考**: `docs/API_QUICK_REFERENCE.md`

---

**最后更新**: 2024-01-16