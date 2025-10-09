#!/bin/bash

# 博实智能巡检平台 - 外网部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "================================"
echo "博实智能巡检平台 - 外网部署脚本"
echo "================================"

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}项目根目录: $PROJECT_ROOT${NC}"

# 1. 检查系统环境
echo -e "\n${YELLOW}1. 检查系统环境...${NC}"

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠ 检测到root用户，建议使用普通用户运行${NC}"
fi

# 检查防火墙状态
echo -e "${YELLOW}检查防火墙状态...${NC}"
if command -v ufw &> /dev/null; then
    ufw status | grep -q "Status: active" && echo -e "${GREEN}✓ UFW防火墙已启用${NC}" || echo -e "${YELLOW}⚠ UFW防火墙未启用${NC}"
elif command -v firewall-cmd &> /dev/null; then
    systemctl is-active --quiet firewalld && echo -e "${GREEN}✓ Firewalld已启用${NC}" || echo -e "${YELLOW}⚠ Firewalld未启用${NC}"
fi

# 2. 配置防火墙
echo -e "\n${YELLOW}2. 配置防火墙规则...${NC}"

if command -v ufw &> /dev/null; then
    echo -e "${YELLOW}配置UFW防火墙...${NC}"
    sudo ufw allow 8000/tcp comment "博实智能巡检平台API端口"
    sudo ufw allow 9090/tcp comment "ROS2 Bridge端口"
    sudo ufw allow ssh
    echo -e "${GREEN}✓ UFW防火墙规则已配置${NC}"
elif command -v firewall-cmd &> /dev/null; then
    echo -e "${YELLOW}配置Firewalld...${NC}"
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --permanent --add-port=9090/tcp
    sudo firewall-cmd --reload
    echo -e "${GREEN}✓ Firewalld规则已配置${NC}"
else
    echo -e "${RED}✗ 未检测到防火墙管理工具${NC}"
fi

# 3. 配置生产环境
echo -e "\n${YELLOW}3. 配置生产环境...${NC}"

# 复制生产环境配置
if [ ! -f ".env" ]; then
    cp .env.production .env
    echo -e "${GREEN}✓ 生产环境配置已创建${NC}"
    echo -e "${YELLOW}⚠ 请编辑 .env 文件修改数据库密码和JWT密钥${NC}"
else
    echo -e "${GREEN}✓ 环境配置文件已存在${NC}"
fi

# 4. 安装和配置Nginx（可选）
echo -e "\n${YELLOW}4. 配置Nginx反向代理（可选）...${NC}"
read -p "是否安装和配置Nginx反向代理? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 安装Nginx
    if ! command -v nginx &> /dev/null; then
        echo -e "${YELLOW}安装Nginx...${NC}"
        sudo apt update
        sudo apt install -y nginx
    fi
    
    # 创建Nginx配置
    sudo tee /etc/nginx/sites-available/boshi-inspection > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;  # 请修改为你的域名或IP
    
    # API接口代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 支持大文件上传
        client_max_body_size 100M;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # WebSocket代理
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 静态文件（如果有前端）
    location / {
        try_files \$uri \$uri/ @backend;
    }
    
    # 后端代理
    location @backend {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/boshi-inspection /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    
    echo -e "${GREEN}✓ Nginx配置完成${NC}"
    echo -e "${BLUE}请修改 /etc/nginx/sites-available/boshi-inspection 中的域名${NC}"
else
    echo -e "${YELLOW}跳过Nginx配置${NC}"
fi

# 5. 配置systemd服务
echo -e "\n${YELLOW}5. 配置systemd服务...${NC}"
read -p "是否创建systemd服务自动启动? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo tee /etc/systemd/system/boshi-inspection.service > /dev/null << EOF
[Unit]
Description=博实智能巡检平台
After=network.target mysql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_ROOT
Environment=PATH=$PROJECT_ROOT/venv/bin
ExecStart=$PROJECT_ROOT/venv/bin/python -m app.main
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable boshi-inspection.service
    
    echo -e "${GREEN}✓ systemd服务已配置${NC}"
    echo -e "${BLUE}使用以下命令管理服务:${NC}"
    echo -e "${BLUE}  启动: sudo systemctl start boshi-inspection${NC}"
    echo -e "${BLUE}  停止: sudo systemctl stop boshi-inspection${NC}"
    echo -e "${BLUE}  状态: sudo systemctl status boshi-inspection${NC}"
else
    echo -e "${YELLOW}跳过systemd服务配置${NC}"
fi

# 6. 获取外网IP
echo -e "\n${YELLOW}6. 获取网络信息...${NC}"

# 获取内网IP
INTERNAL_IP=$(hostname -I | awk '{print $1}')
echo -e "${GREEN}内网IP: $INTERNAL_IP${NC}"

# 获取外网IP
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "获取失败")
echo -e "${GREEN}外网IP: $EXTERNAL_IP${NC}"

# 7. 启动应用
echo -e "\n${YELLOW}7. 启动应用...${NC}"

# 激活虚拟环境
source venv/bin/activate

# 启动应用
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}🚀 博实智能巡检平台已配置完成${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "${BLUE}内网访问地址:${NC}"
echo -e "${BLUE}  - API: http://$INTERNAL_IP:8000${NC}"
echo -e "${BLUE}  - 文档: http://$INTERNAL_IP:8000/docs${NC}"
echo -e "${BLUE}  - WebSocket: ws://$INTERNAL_IP:8000/ws${NC}"
echo ""
if [ "$EXTERNAL_IP" != "获取失败" ]; then
    echo -e "${BLUE}外网访问地址:${NC}"
    echo -e "${BLUE}  - API: http://$EXTERNAL_IP:8000${NC}"
    echo -e "${BLUE}  - 文档: http://$EXTERNAL_IP:8000/docs${NC}"
    echo -e "${BLUE}  - WebSocket: ws://$EXTERNAL_IP:8000/ws${NC}"
    echo ""
fi
echo -e "${BLUE}默认管理员账号:${NC}"
echo -e "${BLUE}  - 用户名: admin${NC}"
echo -e "${BLUE}  - 密码: admin${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

# 启动FastAPI应用
python -m app.main

