# Scripts目录说明

## 📋 脚本文件列表

### 数据库脚本

#### 1. `init_database.sql` - 数据库初始化脚本
**功能**: 初始化完整的数据库结构和示例数据
- 🗑️ 删除现有表（按外键依赖顺序）
- 🏗️ 创建所有数据表（15个表）
- 📊 插入示例数据（用户、地图、机器人、任务等）

**使用方法**:
```bash
# 在WSL中执行
mysql -u root -p < scripts/init_database.sql
```

**创建的表**:
1. `tb_users` - 用户表
2. `tb_sessions` - 会话表
3. `tb_map` - 地图表
4. `tb_mapnet` - 地图路网表
5. `tb_robot` - 机器人表
6. `tb_point` - 巡检点表
7. `tb_item` - 巡检项目表
8. `tb_point_item` - 点-项关联表
9. `tb_task` - 任务表
10. `tb_taskschedule` - 任务日程表
11. `tb_taskhistory` - 任务记录表
12. `tb_taskresult` - 任务结果表
13. `tb_itemhistory` - 巡检记录表
14. `tb_alarmrule` - 报警规则表
15. `tb_alarminfo` - 报警信息表

**示例数据**:
- 3个默认用户（superadmin, admin, operator）
- 3个地图（一楼、二楼、室外）
- 3个机器人
- 8个巡检点
- 8个巡检项目
- 多条点-项关联
- 3个任务
- 多条任务记录和结果

---

### 部署脚本

#### 2. `deploy_external.sh` - 外网部署脚本
**功能**: 自动化部署到外网，供前端测试访问

**主要步骤**:
1. ✅ 检查系统环境
2. ✅ 配置防火墙（开放8000、9090端口）
3. ✅ 创建生产环境配置
4. ✅ [可选] 安装配置Nginx反向代理
5. ✅ [可选] 配置systemd开机自启
6. ✅ 获取内网IP和外网IP
7. ✅ 启动FastAPI应用

**使用方法**:
```bash
# 在WSL或Linux中执行
cd /mnt/d/Project/boshi/boshi-inspection-platform
bash scripts/deploy_external.sh
```

**部署后访问地址**:
```
内网访问:
- API: http://内网IP:8000
- 文档: http://内网IP:8000/docs
- WebSocket: ws://内网IP:8000/ws

外网访问:
- API: http://外网IP:8000
- 文档: http://外网IP:8000/docs
- WebSocket: ws://外网IP:8000/ws
```

**配置选项**:
- Nginx反向代理（推荐生产环境）
- systemd服务（实现开机自启和自动重启）

**systemd服务管理**:
```bash
# 启动服务
sudo systemctl start boshi-inspection

# 停止服务
sudo systemctl stop boshi-inspection

# 重启服务
sudo systemctl restart boshi-inspection

# 查看状态
sudo systemctl status boshi-inspection

# 查看日志
sudo journalctl -u boshi-inspection -f
```

---

## 🚀 快速开始

### 初次部署

#### 1. 初始化数据库
```bash
# 在WSL中执行
mysql -u root -p < scripts/init_database.sql
```

#### 2. 本地启动（测试）
```bash
# 启动开发服务器
cd /mnt/d/Project/boshi/boshi-inspection-platform
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0
python3 -m app.main
```

#### 3. 外网部署（生产）
```bash
# 自动化部署
bash scripts/deploy_external.sh
```

---

## 📊 数据库说明

### 表结构关系

```
用户系统:
├── tb_users (用户表)
└── tb_sessions (会话表)

地图系统:
├── tb_map (地图表)
├── tb_mapnet (路网表) → tb_map
└── tb_point (巡检点表) → tb_map

巡检系统:
├── tb_item (巡检项目表)
└── tb_point_item (点-项关联表) → tb_point, tb_item

任务系统:
├── tb_task (任务表) → tb_map, tb_robot
├── tb_taskschedule (任务日程表) → tb_task
├── tb_taskhistory (任务记录表) → tb_task
├── tb_taskresult (任务结果表) → tb_taskhistory
└── tb_itemhistory (巡检记录表) → tb_taskhistory, tb_item

报警系统:
├── tb_alarmrule (报警规则表) → tb_item
└── tb_alarminfo (报警信息表) → tb_alarmrule, tb_itemhistory

机器人系统:
└── tb_robot (机器人表)
```

### 默认账号

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| superadmin | superadmin | super_admin | 超级管理员 |
| admin | admin | admin | 管理员 |
| operator | operator | operator | 操作员 |

---

## 🔧 维护脚本

### 数据库重置

完全重置数据库（**慎用，会删除所有数据**）:
```bash
mysql -u root -p < scripts/init_database.sql
```

### 查看表结构
```bash
mysql -u root -p boshi_inspection -e "SHOW TABLES;"
```

### 查看用户列表
```bash
mysql -u root -p boshi_inspection -e "SELECT id, username, role FROM tb_users WHERE is_deleted=0;"
```

---

## 📦 依赖要求

### 系统依赖
- MySQL 8.0+
- Python 3.10+
- ROS2 Humble（可选）

### Python依赖
- FastAPI
- SQLAlchemy
- PyMySQL
- 其他依赖见 `requirements.txt`

---

## 🔐 安全注意事项

### 生产环境部署前

1. **修改默认密码**
   ```sql
   -- 重置admin密码
   UPDATE tb_users SET password_hash = '$2b$12$...' WHERE username = 'admin';
   ```

2. **修改JWT密钥**
   ```bash
   # 编辑 .env 文件
   SECRET_KEY=your-secret-key-here
   ```

3. **配置防火墙**
   - 只开放必要端口（8000）
   - 限制SSH访问IP

4. **配置HTTPS**
   - 使用Nginx配置SSL证书
   - 强制HTTPS访问

---

## 📞 技术支持

### 相关文档
- **API文档**: `docs/API_REFERENCE.md`
- **模块详细文档**: `docs/api/01-18.md`
- **部署指南**: `docs/EXTERNAL_DEPLOYMENT_GUIDE.md`
- **日志指南**: `docs/LOGGING_GUIDE.md`
- **错误码说明**: `docs/ERROR_CODES.md`

### 问题排查
1. 查看应用日志：`logs/YYYY-MM-DD/app.log`
2. 查看错误日志：`logs/YYYY-MM-DD/error.log`
3. 查看调试日志：`logs/YYYY-MM-DD/debug.log`

---

## 🔄 版本更新

### 数据库迁移
如需更新数据库结构：
1. 修改 `scripts/init_database.sql`
2. 创建迁移SQL文件到 `migrations/` 目录
3. 参考 `migrations/README.md` 执行迁移

---

**最后更新**: 2024-01-16  
**维护者**: 博实智能巡检平台开发团队