# 数据库迁移

此目录用于存放 Alembic 数据库迁移文件。

## 使用方法

### 初始化迁移环境
```bash
alembic init migrations
```

### 生成迁移文件
```bash
alembic revision --autogenerate -m "描述变更内容"
```

### 执行迁移
```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade <revision_id>

# 降级到上一个版本
alembic downgrade -1
```

### 查看迁移历史
```bash
alembic history
alembic current
```

## 注意事项

- 迁移文件一旦提交到版本控制，不要随意修改
- 在生产环境执行迁移前，请先在测试环境验证
- 重要的数据变更操作建议手动编写迁移脚本
