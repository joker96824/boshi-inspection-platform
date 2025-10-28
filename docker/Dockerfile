# 博实智能巡检平台 - Docker镜像
# 基于Ubuntu 22.04 + ROS2 Humble + Python 3.10

# ============ 第一阶段：构建阶段 ============
FROM ubuntu:22.04 AS builder

# 安装ROS2 Humble
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null \
    && apt-get update && apt-get install -y \
    ros-humble-ros-base \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_DISTRO=humble

# 设置工作目录
WORKDIR /build

# 安装Python和系统依赖
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    build-essential \
    libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装Python依赖
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============ 第二阶段：运行阶段 ============
FROM ubuntu:22.04

# 安装ROS2 Humble
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null \
    && apt-get update && apt-get install -y \
    ros-humble-ros-base \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_DISTRO=humble

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    ROS_DISTRO=humble \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libmysqlclient21 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 设置Python虚拟环境
ENV PATH="/opt/venv/bin:$PATH"

# 创建应用目录
WORKDIR /app

    # 复制应用代码
    COPY app ./app
    COPY .env.backup .env

# 创建必要的目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/system/health || exit 1

# 启动ROS2环境并运行应用
CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && python -m app.main"]

