# 使用ROS2 Humble作为基础镜像
FROM ros:humble-desktop

# 设置非交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    curl \
    wget \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

# 安装Python包
RUN pip3 install --upgrade pip && \
    pip3 install \
    fastapi \
    uvicorn[standard] \
    pydantic \
    websockets \
    python-multipart \
    python-jose[cryptography] \
    passlib[bcrypt] \
    python-dotenv

# 创建工作目录
WORKDIR /workspace

# 复制项目文件
COPY . /workspace/

# 设置环境变量
ENV PYTHONPATH=/workspace
ENV ROS_DOMAIN_ID=0

# 暴露端口
EXPOSE 8000

# 创建启动脚本
RUN echo '#!/bin/bash\n\
source /opt/ros/humble/setup.bash\n\
cd /workspace\n\
exec "$@"' > /usr/local/bin/ros-entrypoint.sh && \
    chmod +x /usr/local/bin/ros-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/ros-entrypoint.sh"]
CMD ["bash"]

