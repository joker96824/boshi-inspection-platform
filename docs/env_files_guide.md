# 环境变量配置文件说明

## 📁 环境变量文件

项目中有以下环境变量相关的文件：

### ✅ `.env.example`（推荐使用）

**用途**：标准的环境变量配置示例文件

**特点**：
- ✅ 已提交到 Git 仓库
- ✅ 包含所有配置项的说明和示例
- ✅ 支持 MySQL 和 PostgreSQL
- ✅ Redis 配置可选（默认禁用）

**使用方式**：
```bash
# 复制为 .env 文件
cp .env.example .env

# 根据实际情况修改配置
nano .env
```

**适用场景**：
- 开发环境配置
- 生产环境配置模板
- Docker 部署配置模板

---

### ❓ `.env.backup`（已废弃）

**状态**：已废弃，不再使用

**原因**：
- 项目已改为使用外部数据库，不再需要在镜像中内置配置
- 环境变量通过 `docker-compose.yml` 的 `environment` 部分传递
- 已被 `.env.example` 替代

**处理建议**：
- 可以删除此文件
- 或保留作为个人备份（不提交到 Git）

**历史用途**：
- 之前用于 Docker 镜像构建时提供默认配置
- 之前用于打包脚本复制到部署目录

---

### ❓ `.env.develop`（已废弃）

**状态**：已废弃，不再使用

**原因**：
- 已被 `.env.example` 替代
- 统一使用 `.env.example` 作为所有环境的模板

**处理建议**：
- 可以删除此文件
- 或保留作为个人开发环境备份（不提交到 Git）

**历史用途**：
- 之前用于开发环境的快速配置

---

## 🔄 迁移指南

### 从 `.env.backup` 迁移

如果你之前使用 `.env.backup`：

1. **查看旧配置**（如果文件存在）：
```bash
cat .env.backup
```

2. **使用新模板**：
```bash
cp .env.example .env
```

3. **将旧配置中的值复制到新 `.env` 文件**

4. **更新数据库配置**（重要）：
   - 确保 `DATABASE_URL` 指向外部数据库
   - 如果使用 PostgreSQL，修改 URL 格式

### 从 `.env.develop` 迁移

如果你之前使用 `.env.develop`：

1. **查看旧配置**（如果文件存在）：
```bash
cat .env.develop
```

2. **使用新模板**：
```bash
cp .env.example .env
```

3. **将旧配置中的值复制到新 `.env` 文件**

---

## 📝 当前推荐的文件结构

```
项目根目录/
├── .env.example          # ✅ 标准配置模板（提交到 Git）
├── .env                  # ❌ 个人配置（不提交到 Git，由 .gitignore 忽略）
├── .env.backup          # ❓ 可删除（个人备份）
└── .env.develop         # ❓ 可删除（个人备份）
```

---

## ⚙️ 配置说明

### 必须配置的项

1. **`DATABASE_URL`** - 数据库连接（必须）
   ```env
   # MySQL
   DATABASE_URL=mysql+aiomysql://用户名:密码@主机:3306/数据库名
   
   # PostgreSQL
   DATABASE_URL=postgresql+asyncpg://用户名:密码@主机:5432/数据库名
   ```

2. **`SECRET_KEY`** - JWT 密钥（生产环境必须修改）

### 可选配置的项

1. **`REDIS_ENABLED`** - 是否启用 Redis（默认 `false`）
2. **`REDIS_URL`** - Redis 连接（仅在启用时生效）
3. **`DEBUG`** - 调试模式（生产环境建议 `false`）
4. **`NETWORK_MODE`** - Docker 网络模式（仅在 Docker 部署时使用）

---

## 🚀 快速开始

### 开发环境

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 修改数据库连接（指向本地数据库）
nano .env

# 3. 启动应用
python -m app.main
```

### Docker 部署

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 修改数据库连接（指向外部数据库）
nano .env

# 3. 启动容器
docker compose up -d
```

---

## ❓ 常见问题

### Q: 我应该使用哪个文件？

A: **始终使用 `.env.example` 作为模板**，复制为 `.env` 后根据实际情况修改。

### Q: `.env.backup` 和 `.env.develop` 可以删除吗？

A: **可以删除**。它们已被 `.env.example` 替代，保留它们只是为了向后兼容或作为个人备份。

### Q: 为什么 Dockerfile 不再复制 `.env.backup`？

A: 因为：
- 环境变量现在通过 `docker-compose.yml` 传递
- 不再需要在镜像中内置配置
- 更灵活，可以在部署时配置不同的环境

### Q: 如何确保配置安全？

A:
- ✅ `.env` 文件已被 `.gitignore` 忽略，不会提交到 Git
- ✅ 生产环境使用强密码和随机 `SECRET_KEY`
- ✅ 不要将 `.env` 文件分享给他人
- ✅ 使用环境变量管理工具（如 Docker secrets）管理敏感信息

