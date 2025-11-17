# 数据库切换指南

本项目支持在 **MySQL** 和 **PostgreSQL** 之间随时切换，无需修改代码，只需更改环境变量配置即可。

## 快速切换

### 切换到 MySQL

在 `.env` 文件中设置：

```env
DATABASE_URL=mysql+aiomysql://用户名:密码@主机:端口/数据库名
```

**示例：**
```env
DATABASE_URL=mysql+aiomysql://boshi:password123@192.168.1.100:3306/boshirobot
```

### 切换到 PostgreSQL

在 `.env` 文件中设置：

```env
DATABASE_URL=postgresql+asyncpg://用户名:密码@主机:端口/数据库名
```

**示例：**
```env
DATABASE_URL=postgresql+asyncpg://boshi:password123@192.168.1.100:5432/boshirobot
```

## 工作原理

系统会根据 `DATABASE_URL` 的格式自动识别数据库类型：

- **MySQL**: URL 中包含 `mysql`、`aiomysql` 或 `pymysql`
- **PostgreSQL**: URL 中包含 `postgresql`、`postgres` 或 `asyncpg`

识别后会自动执行相应的初始化逻辑：

- **MySQL**: 创建表结构（需要先手动创建数据库）
- **PostgreSQL**: 创建表结构（需要先手动创建数据库）

## 数据库初始化

### MySQL 初始化

1. **创建数据库**（如果不存在）：
```sql
CREATE DATABASE IF NOT EXISTS boshirobot 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

2. **执行初始化脚本**（可选，用于创建初始数据）：
```bash
mysql -u root -p boshirobot < scripts/init_database.sql
mysql -u root -p boshirobot < scripts/init_sample_data.sql
```

### PostgreSQL 初始化

1. **创建数据库**（如果不存在）：
```sql
CREATE DATABASE boshirobot;
```

2. **执行初始化脚本**（需要先转换为 PostgreSQL 语法）：
```bash
# 注意：需要将 MySQL 语法转换为 PostgreSQL 语法
psql -U postgres -d boshirobot -f scripts/init_database_postgresql.sql
psql -U postgres -d boshirobot -f scripts/init_sample_data_postgresql.sql
```

## 注意事项

### 1. 数据库驱动

项目已包含两种数据库的驱动：
- **MySQL**: `aiomysql`、`pymysql`
- **PostgreSQL**: `asyncpg`、`psycopg2-binary`

无需额外安装。

### 2. SQL 初始化脚本

- **MySQL**: 使用 `scripts/init_database.sql` 和 `scripts/init_sample_data.sql`
- **PostgreSQL**: 需要将 MySQL 语法转换为 PostgreSQL 语法

主要差异：
- `AUTO_INCREMENT` → `SERIAL` 或 `GENERATED ALWAYS AS IDENTITY`
- `ENGINE=InnoDB` → 不需要
- `DATETIME` → `TIMESTAMP` 或 `TIMESTAMPTZ`
- `JSON` → `JSONB`（推荐）

### 3. ORM 层兼容性

SQLAlchemy ORM 层是数据库无关的，所有模型代码无需修改即可在两种数据库上运行。

### 4. 数据库特定功能

如果使用了数据库特定的功能（如 MySQL 的 `JSON_EXTRACT`），需要：
- 使用 SQLAlchemy 的 `text()` 函数执行原生 SQL
- 根据数据库类型条件执行不同的 SQL

## 验证切换

应用启动时，日志会显示检测到的数据库类型：

```
INFO: 检测到数据库类型: mysql, 数据库名称: boshirobot
INFO: MySQL 表结构初始化完成
```

或

```
INFO: 检测到数据库类型: postgresql, 数据库名称: boshirobot
INFO: PostgreSQL 表结构初始化完成
```

## 常见问题

### Q: 切换数据库后需要重新初始化吗？

A: 是的，需要在新的数据库中执行初始化脚本创建表结构和初始数据。

### Q: 可以在运行时切换数据库吗？

A: 不可以。`DATABASE_URL` 在应用启动时读取，运行时切换需要重启应用。

### Q: 两种数据库的数据可以互相迁移吗？

A: 可以，但需要注意：
- 数据类型差异（如 JSON、时间类型）
- 字符集和排序规则
- 索引和约束的差异

建议使用数据库迁移工具（如 `pgloader`）进行数据迁移。

### Q: 如何检查当前使用的数据库类型？

A: 查看应用启动日志，或调用系统健康检查接口查看数据库信息。

