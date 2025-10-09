# 博实智能巡检平台 - 完整启动指南

## 项目简介

博实智能巡检平台是一个基于 FastAPI 和 ROS2 的智能巡检系统数据中台，采用现代化的分层架构设计，支持用户认证、权限管理、ROS2 通信和 WebSocket 实时通信。

由于项目需要使用 ROS2（Robot Operating System），必须在 Linux 环境中运行，因此在 Windows 环境下需要通过 WSL2 来模拟 Linux 环境。

## 系统要求

- Windows 10 版本 2004 及更高版本（内部版本 19041 及更高版本）或 Windows 11
- 启用虚拟化功能的 CPU
- 至少 4GB 内存
- 至少 2GB 可用磁盘空间

## 第一步：安装和配置 WSL2

### 1.1 启用 Windows 功能

以管理员身份打开 PowerShell，执行以下命令：

```powershell
# 启用适用于 Linux 的 Windows 子系统
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机功能
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

**重启计算机** 以完成功能启用。

### 1.2 下载并安装 WSL2 Linux 内核更新包

1. 下载适用于 x64 计算机的 WSL2 Linux 内核更新包：
   - 访问：https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
   - 下载并运行安装程序

### 1.3 设置 WSL2 为默认版本

```powershell
wsl --set-default-version 2
```

### 1.4 安装 Ubuntu 22.04

```powershell
# 安装 Ubuntu 22.04 LTS
wsl --install -d Ubuntu-22.04
```

或者通过 Microsoft Store 搜索 "Ubuntu 22.04 LTS" 并安装。

### 1.5 首次配置 Ubuntu

安装完成后，启动 Ubuntu，系统会要求：
1. 创建用户名（建议使用英文）
2. 设置密码
3. 确认密码

## 第二步：配置 Ubuntu 环境

### 2.1 更新系统包

```bash
# 更新包列表
sudo apt update

# 升级系统包
sudo apt upgrade -y
```

### 2.2 安装基础依赖

```bash
# 安装基础工具
sudo apt install -y curl wget git vim nano build-essential

# 安装网络工具
sudo apt install -y net-tools
```

## 第三步：安装 Python 环境

### 3.1 安装 Python 3.10

```bash
# Ubuntu 22.04 默认包含 Python 3.10，验证版本
python3 --version

# 安装 Python 开发包和 pip
sudo apt install -y python3-dev python3-pip python3-venv

# 升级 pip
pip3 install --upgrade pip
```

### 3.2 验证 Python 安装

```bash
# 检查 Python 版本（应该是 3.10.x）
python3 --version

# 检查 pip 版本
pip3 --version
```

## 第四步：安装 MySQL 数据库

### 4.1 安装 MySQL Server

```bash
# 安装 MySQL
sudo apt install -y mysql-server
```

### 4.2 启动 MySQL 服务

```bash
# 启动 MySQL 服务
sudo service mysql start

# 设置开机自启（可选）
sudo systemctl enable mysql
```

### 4.3 配置 MySQL

```bash
# 运行安全配置脚本
sudo mysql_secure_installation
```

配置过程中的选择：
- 是否安装验证密码插件：`n`（选择否）
- 设置 root 密码：`root`（或你喜欢的密码）
- 移除匿名用户：`y`
- 禁止 root 远程登录：`n`（选择否，因为需要本地连接）
- 移除测试数据库：`y`
- 重新加载权限表：`y`

### 4.4 测试 MySQL 连接

```bash
# 使用 root 用户连接 MySQL
mysql -u root -p

# 在 MySQL 命令行中执行
SHOW DATABASES;
EXIT;
```

## 第五步：安装 Redis

### 5.1 安装 Redis Server

```bash
# 安装 Redis
sudo apt install -y redis-server
```

### 5.2 启动 Redis 服务

```bash
# 启动 Redis 服务
sudo service redis-server start

# 设置开机自启（可选）
sudo systemctl enable redis-server
```

### 5.3 测试 Redis 连接

```bash
# 测试 Redis 连接
redis-cli ping
# 应该返回 PONG
```

## 第六步：安装 ROS2 Humble

### 6.1 设置 locale

```bash
# 确保系统支持 UTF-8
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

### 6.2 添加 ROS2 apt 源

```bash
# 安装必要的工具
sudo apt install -y software-properties-common
sudo add-apt-repository universe -y

# 添加 ROS2 GPG 密钥
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# 添加 ROS2 源到 sources.list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

### 6.3 安装 ROS2 Humble

```bash
# 更新包列表
sudo apt update

# 安装 ROS2 Humble Desktop（完整版）
sudo apt install -y ros-humble-desktop

# 安装开发工具
sudo apt install -y ros-dev-tools python3-rosdep
```

### 6.4 初始化 rosdep

```bash
# 初始化 rosdep（首次安装需要）
sudo rosdep init
rosdep update
```

### 6.5 设置 ROS2 环境

```bash
# 将 ROS2 环境加载命令添加到 bashrc
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

# 立即加载 ROS2 环境
source /opt/ros/humble/setup.bash
```

### 6.6 验证 ROS2 安装

```bash
# 检查 ROS2 版本
ros2 --version

# 列出可用的 ROS2 命令
ros2 --help
```

## 第七步：克隆和配置项目

### 7.1 进入项目目录

```bash
# 进入 Windows 项目目录（根据你的实际路径调整）
cd /mnt/d/Project/boshi/boshi-inspection-platform
```

### 7.2 创建 Python 虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证虚拟环境（提示符应该显示 (venv)）
which python
```

### 7.3 安装 Python 依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

## 第八步：配置数据库

### 8.1 创建项目数据库

```bash
# 连接到 MySQL
mysql -u root -p

# 在 MySQL 命令行中执行以下 SQL
CREATE DATABASE IF NOT EXISTS boshirobot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE boshirobot;
EXIT;
```

### 8.2 初始化数据库表

```bash
# 执行数据库初始化脚本
mysql -u root -p < scripts/init_database.sql
```

## 第九步：配置环境变量

### 9.1 创建环境配置文件

```bash
# 复制环境配置示例文件（如果存在）
cp .env.develop .env
```

或者手动创建 `.env` 文件：

```bash
# 创建 .env 文件
nano .env
```

在 `.env` 文件中添加以下内容：

```env
# 应用配置
APP_NAME=博实智能巡检平台
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# 服务器配置
HOST=0.0.0.0
PORT=8000
WORKERS=1
LOG_LEVEL=INFO

# 数据库配置
DATABASE_URL=mysql+aiomysql://root:root@localhost:3306/boshirobot

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=30
REFRESH_TOKEN_EXPIRE_DAYS=90

# ROS2配置
ROS_DOMAIN_ID=0
ROS_BRIDGE_PORT=9090
ROS_BRIDGE_HOST=localhost
```

## 第十步：启动项目

### 10.1 确保所有服务运行

```bash
# 检查并启动 MySQL
sudo service mysql start

# 检查并启动 Redis
sudo service redis-server start

# 验证服务状态
sudo service mysql status
sudo service redis-server status
```

### 10.2 加载 ROS2 环境

```bash
# 加载 ROS2 环境变量
source /opt/ros/humble/setup.bash

# 设置 ROS2 域 ID
export ROS_DOMAIN_ID=0
```

### 10.3 启动应用

```bash
# 确保在项目根目录
cd /mnt/d/Project/boshi/boshi-inspection-platform

# 激活虚拟环境
source venv/bin/activate

# 启动 FastAPI 应用
python3 -m app.main
```

## 第十一步：验证启动

### 11.1 检查应用状态

启动成功后，你应该看到类似以下的日志输出：

```
2025-09-18 08:22:55 - app - INFO - 应用启动中...
2025-09-18 08:22:55 - app - INFO - 数据库初始化完成
2025-09-18 08:22:55 - app - INFO - WebSocket连接管理器初始化完成
2025-09-18 08:22:55 - app.ros.ros2_bridge - INFO - ROS2 Bridge节点已启动
2025-09-18 08:22:55 - app - INFO - ROS2 Bridge初始化完成
2025-09-18 08:22:55 - app - INFO - WebSocket处理器初始化完成
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 11.2 测试访问

打开新的终端窗口（保持应用运行），测试 API：

```bash
# 测试根端点
curl http://localhost:8000/

# 应该返回类似：
# {"code":200,"message":"欢迎使用博实智能巡检平台","data":{"version":"1.0.0","docs":"/docs"}}
```

### 11.3 访问 Web 界面

在 Windows 浏览器中访问：

- **主页**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **WebSocket 测试**: ws://localhost:8000/ws

## 默认登录信息

系统预设了管理员账户：

- **用户名**: `admin`
- **密码**: `admin`
- **角色**: `super_admin`

## 常见问题解决

### WSL2 相关问题

**问题**: WSL 命令不可用  
**解决**: 确保已启用 WSL 功能并重启计算机

**问题**: Ubuntu 启动失败  
**解决**: 检查虚拟化是否启用，更新 WSL2 内核

### 数据库连接问题

**问题**: MySQL 连接被拒绝  
**解决**: 
```bash
sudo service mysql start
mysql -u root -p  # 测试连接
```

**问题**: 密码认证失败  
**解决**: 重置 root 密码或检查 .env 文件中的密码配置

### ROS2 环境问题

**问题**: ros2 命令不可用  
**解决**: 
```bash
source /opt/ros/humble/setup.bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

**问题**: ROS2 节点启动失败  
**解决**: 检查 ROS_DOMAIN_ID 设置和网络配置

### Python 依赖问题

**问题**: 模块导入失败  
**解决**: 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**问题**: 权限错误  
**解决**: 确保虚拟环境已激活，避免使用 sudo 安装包

## 停止应用

要停止应用，在运行应用的终端中按 `Ctrl+C`。

## 开发模式

在开发过程中，你可能需要：

1. **查看日志**: 日志文件位于 `logs/` 目录
2. **重启应用**: 按 `Ctrl+C` 停止，然后重新运行启动命令
3. **调试模式**: 在 `.env` 文件中设置 `DEBUG=true`

## 下一步

项目启动成功后，你可以：

1. 访问 API 文档了解接口详情
2. 使用默认账户登录系统
3. 测试 ROS2 通信功能
4. 开发自定义功能模块

恭喜！你已经成功启动了博实智能巡检平台。
