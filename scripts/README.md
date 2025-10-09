# 测试脚本使用说明

## 概述

本目录包含了博实智能巡检平台的完整测试套件，用于验证系统功能和权限控制。

## 测试脚本列表

### 1. 快速测试 (`quick_test.py`)
- **功能**: 快速验证基本功能
- **适用**: 开发调试、快速验证
- **时间**: 约30秒
- **测试内容**:
  - 服务器连接
  - 用户登录
  - 基本API调用
  - 创建和查询资源

### 2. 权限测试 (`test_permissions.py`)
- **功能**: 专门测试权限控制
- **适用**: 安全验证、权限测试
- **时间**: 约1分钟
- **测试内容**:
  - 不同角色的权限验证
  - 查询权限（所有用户）
  - 增删改权限（只有operator+）
  - 权限拒绝场景

### 3. 全面测试 (`test_all_apis.py`)
- **功能**: 全面测试所有API
- **适用**: 完整功能验证、回归测试
- **时间**: 约5-10分钟
- **测试内容**:
  - 所有API接口
  - 所有用户角色
  - 完整CRUD操作
  - 详细测试报告

## 使用方法

### Windows用户
```cmd
# 运行测试菜单
scripts\run_tests.bat

# 或直接运行特定测试
python scripts\quick_test.py
python scripts\test_permissions.py
python scripts\test_all_apis.py
```

### Linux/WSL用户
```bash
# 运行测试菜单
bash scripts/run_tests.sh

# 或直接运行特定测试
python3 scripts/quick_test.py
python3 scripts/test_permissions.py
python3 scripts/test_all_apis.py
```

## 测试前准备

### 1. 启动服务器
```bash
# 在WSL中启动
cd /mnt/d/Project/boshi/boshi-inspection-platform
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0
export HOST=0.0.0.0
python3 -m app.main
```

### 2. 确保数据库已初始化
```bash
mysql -u root -proot < scripts/init_database.sql
```

### 3. 确保测试用户存在
测试需要以下用户：
- `admin` / `admin` (super_admin)
- `testadmin` / `123456` (admin)  
- `testoperator` / `123456` (operator)
- `testviewer` / `123456` (viewer)
- `testuser` / `123456` (user)

## 测试结果

### 快速测试结果
```
🚀 快速功能测试...
==================================================
1. 测试服务器连接...
   ✅ 服务器运行正常

2. 测试用户登录...
   ✅ 管理员登录成功

3. 测试获取用户信息...
   ✅ 获取用户信息成功: admin (super_admin)

4. 测试获取用户列表...
   ✅ 获取用户列表成功: 共 5 个用户
      - admin (super_admin)
      - testadmin (admin)
      - testoperator (operator)

5. 测试创建地图...
   ✅ 创建地图成功: 550e8400-e29b-41d4-a716-446655440000

6. 测试获取地图列表...
   ✅ 获取地图列表成功: 共 1 个地图
      - 快速测试地图_1703123456

7. 测试创建机器人...
   ✅ 创建机器人成功: 550e8400-e29b-41d4-a716-446655440001

8. 测试获取机器人列表...
   ✅ 获取机器人列表成功: 共 1 个机器人
      - 快速测试机器人_1703123456

==================================================
🎉 快速测试完成！
如果所有测试都通过，说明系统基本功能正常。
可以运行 scripts/test_all_apis.py 进行完整测试。
```

### 权限测试结果
```
🔐 权限测试开始...
================================================================================
📊 测试结果:
--------------------------------------------------------------------------------
✅ super_admin  GET  /api/v1/users/                    - 成功 (期望: 成功)
✅ admin        GET  /api/v1/users/                    - 成功 (期望: 成功)
✅ operator     GET  /api/v1/users/                    - 成功 (期望: 成功)
✅ viewer       GET  /api/v1/users/                    - 成功 (期望: 成功)
✅ user         GET  /api/v1/users/                    - 成功 (期望: 成功)
✅ super_admin  POST /api/v1/maps/                     - 成功 (期望: 成功)
✅ admin        POST /api/v1/maps/                     - 成功 (期望: 成功)
✅ operator     POST /api/v1/maps/                     - 成功 (期望: 成功)
❌ viewer       POST /api/v1/maps/                     - 失败 (期望: 失败)
❌ user         POST /api/v1/maps/                     - 失败 (期望: 失败)
================================================================================
📊 测试完成: 10/10 通过 (100.0%)
🎉 所有权限测试通过！
```

### 全面测试结果
```
🚀 开始全面API测试...
测试目标: http://localhost:8000
测试时间: 2024-01-01 10:00:00

🔐 测试认证API...
✅ super_admin 登录成功
✅ admin 登录成功
✅ operator 登录成功
✅ viewer 登录成功
✅ user 登录成功

👥 测试用户管理API...
✅ PASS 创建用户-super_admin - super_admin POST /api/v1/users/ (状态码: 200)
✅ PASS 创建用户-admin - admin POST /api/v1/users/ (状态码: 200)
✅ PASS 获取用户列表-super_admin - super_admin GET /api/v1/users/ (状态码: 200)

🗺️ 测试地图管理API...
✅ PASS 创建地图-super_admin - super_admin POST /api/v1/maps/ (状态码: 200)
✅ PASS 创建地图-admin - admin POST /api/v1/maps/ (状态码: 200)
✅ PASS 创建地图-operator - operator POST /api/v1/maps/ (状态码: 200)
✅ PASS 获取地图列表-super_admin - super_admin GET /api/v1/maps/ (状态码: 200)

... (更多测试结果)

================================================================================
📊 测试报告
================================================================================
总测试数: 150
通过数: 148
失败数: 2
通过率: 98.7%

❌ 失败的测试:
  - 创建用户-viewer (viewer) - 状态码: 403
  - 创建用户-user (user) - 状态码: 403

📄 详细报告已保存到: test_report_20240101_100000.json
```

## 测试报告文件

全面测试会生成详细的JSON报告文件：
- 文件名: `test_report_YYYYMMDD_HHMMSS.json`
- 包含: 测试摘要、详细结果、创建的资源等
- 用途: 问题分析、回归测试、CI/CD集成

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 确保服务器已启动
   - 检查端口8000是否被占用

2. **登录失败**
   - 检查用户名密码
   - 确保用户已创建

3. **权限错误**
   - 检查用户角色
   - 验证权限配置

4. **数据库错误**
   - 确保MySQL运行
   - 检查数据库初始化

### 调试技巧

1. **查看详细错误**
   ```python
   # 在测试脚本中添加调试信息
   print(f"响应状态: {response.status}")
   print(f"响应内容: {await response.text()}")
   ```

2. **检查服务器日志**
   ```bash
   # 查看服务器输出
   tail -f logs/app.log
   ```

3. **验证API文档**
   ```bash
   # 访问API文档
   curl http://localhost:8000/docs
   ```

## 持续集成

可以将测试集成到CI/CD流程：

```yaml
# GitHub Actions 示例
- name: Run Tests
  run: |
    python scripts/quick_test.py
    python scripts/test_permissions.py
    python scripts/test_all_apis.py
```

## 贡献

如需添加新的测试用例：
1. 在相应的测试脚本中添加测试方法
2. 更新测试文档
3. 确保测试覆盖所有场景
4. 验证测试结果正确性