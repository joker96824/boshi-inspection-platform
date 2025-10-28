# Docker 部署文件说明

## 📁 目录结构

```
docker/
├── Dockerfile           # Docker镜像构建文件
├── docker-compose.yml   # Docker编排配置
└── README.md           # 本文档
```

## 📝 文件说明

### Dockerfile
Docker 镜像构建配置，包含：
- 基础镜像：Ubuntu 22.04
- ROS2 Humble 安装
- Python 3.10 + 虚拟环境
- 应用依赖安装
- 应用代码复制

### docker-compose.yml
多容器编排配置，包含：
- MySQL 8.0 服务（端口 3307）
- Redis 7 服务（端口 6379）
- 应用服务（端口 8000）
- 网络配置
- 数据卷配置

## 🚀 使用方法

### 构建镜像
```bash
# 在项目根目录执行
docker build -f docker/Dockerfile -t boshi-inspection-platform:1.0 .
```

### 启动服务
```bash
# 使用 docker-compose（需要先将 docker-compose.yml 复制到部署目录）
docker-compose up -d
```

## ⚙️ 配置说明

### 支持的数据库
- ✅ MySQL 8.0（默认）
- ✅ 人大金仓/PostgreSQL（修改 DATABASE_URL 即可）

### 环境变量配置
所有配置通过外部 `.env` 文件控制，详见 `快速部署指南.md`。

## 📦 打包流程
使用项目根目录的 `build-and-package.ps1` 脚本一键打包。


