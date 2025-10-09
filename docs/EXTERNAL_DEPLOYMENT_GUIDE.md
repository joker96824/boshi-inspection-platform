# 博实智能巡检平台 - 外网部署指南

## 🎯 部署目标

将博实智能巡检平台部署到外网，供前端团队进行对接测试。

## 🚀 快速部署（推荐）

### 方法一：使用部署脚本

```bash
# 在WSL中执行
cd /mnt/d/Project/boshi/boshi-inspection-platform
chmod +x scripts/deploy_external.sh
bash scripts/deploy_external.sh
```

### 方法二：手动部署

## 📋 手动部署步骤

### 1. 环境准备

#### 1.1 复制生产环境配置
```bash
cp .env.production .env
```

#### 1.2 修改关键配置
编辑 `.env` 文件，修改以下关键配置：

```env
# 安全配置
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-at-least-32-characters-long

# 数据库配置（修改密码）
DATABASE_URL=mysql+aiomysql://root:your_strong_password@localhost:3306/boshirobot

# CORS配置（添加前端域名）
CORS_ORIGINS=["https://your-frontend-domain.com", "http://frontend-ip:port"]

# 性能配置
WORKERS=2
LOG_LEVEL=INFO
```

### 2. 网络配置

#### 2.1 配置防火墙

**Ubuntu/Debian (UFW)**:
```bash
# 允许API端口
sudo ufw allow 8000/tcp comment "博实智能巡检平台API"

# 允许ROS2端口
sudo ufw allow 9090/tcp comment "ROS2 Bridge"

# 允许SSH（重要！）
sudo ufw allow ssh

# 启用防火墙
sudo ufw enable
```

**CentOS/RHEL (Firewalld)**:
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload
```

#### 2.2 检查端口占用
```bash
# 检查端口是否被占用
netstat -tuln | grep :8000
netstat -tuln | grep :9090
```

### 3. 安全配置

#### 3.1 生成强密钥
```bash
# 生成32字符的随机密钥
openssl rand -hex 32
```

#### 3.2 数据库安全配置
```bash
# 设置MySQL root密码
sudo mysql_secure_installation

# 创建专用数据库用户（推荐）
mysql -u root -p << EOF
CREATE USER 'boshi_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON boshirobot.* TO 'boshi_user'@'localhost';
FLUSH PRIVILEGES;
EOF
```

### 4. 反向代理配置（推荐）

#### 4.1 安装Nginx
```bash
sudo apt update
sudo apt install -y nginx
```

#### 4.2 创建Nginx配置
```bash
sudo nano /etc/nginx/sites-available/boshi-inspection
```

配置内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名或IP
    
    # 限制请求大小
    client_max_body_size 100M;
    
    # API接口代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # WebSocket代理
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000/api/v1/system/health;
        access_log off;
    }
}
```

#### 4.3 启用配置
```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/boshi-inspection /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 5. 进程管理

#### 5.1 创建systemd服务
```bash
sudo nano /etc/systemd/system/boshi-inspection.service
```

服务配置：
```ini
[Unit]
Description=博实智能巡检平台
After=network.target mysql.service redis.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/boshi-inspection-platform
Environment=PATH=/path/to/boshi-inspection-platform/venv/bin
ExecStart=/path/to/boshi-inspection-platform/venv/bin/python -m app.main
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 5.2 启用服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable boshi-inspection.service
sudo systemctl start boshi-inspection.service
```

### 6. 启动应用

#### 6.1 手动启动（测试用）
```bash
cd /mnt/d/Project/boshi/boshi-inspection-platform

# 激活虚拟环境
source venv/bin/activate

# 加载ROS2环境
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

# 启动应用
python -m app.main
```

#### 6.2 使用systemd启动（生产用）
```bash
sudo systemctl start boshi-inspection
sudo systemctl status boshi-inspection
```

## 🌐 外网访问配置

### 路由器配置

如果你在家庭网络中，需要配置路由器端口转发：

1. **登录路由器管理界面**
2. **找到端口转发/虚拟服务器设置**
3. **添加端口转发规则**:
   - 外部端口: 8000
   - 内部端口: 8000
   - 内部IP: 你的电脑IP
   - 协议: TCP

### 云服务器配置

如果使用云服务器（阿里云、腾讯云等）：

1. **安全组配置**: 开放8000和9090端口
2. **防火墙配置**: 按照上述防火墙配置步骤
3. **域名配置**: 将域名解析到服务器IP

## 🔧 前端对接配置

### 前端环境变量配置

**开发环境** (`.env.development`):
```
REACT_APP_API_BASE_URL=http://your-server-ip:8000
REACT_APP_WS_URL=ws://your-server-ip:8000/ws
```

**生产环境** (`.env.production`):
```
REACT_APP_API_BASE_URL=https://your-domain.com
REACT_APP_WS_URL=wss://your-domain.com/ws
```

### 前端API调用示例

```javascript
// 配置API基础URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// API调用封装
const apiClient = {
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
      }
    });
    
    const result = await response.json();
    
    if (result.code === 410) {
      // Token过期，跳转登录
      localStorage.removeItem('token');
      window.location.href = '/login';
      return;
    }
    
    return result;
  },
  
  // 登录
  async login(username, password) {
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
  },
  
  // 获取用户列表
  async getUsers(page = 1, size = 20) {
    const skip = (page - 1) * size;
    return this.request(`/api/v1/users/?skip=${skip}&limit=${size}`);
  },
  
  // 下载日志
  async downloadLog(logDate, logType = 'app') {
    const token = localStorage.getItem('token');
    const response = await fetch(
      `${API_BASE_URL}/api/v1/logs/download?log_date=${logDate}&log_type=${logType}`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `boshi_${logDate}_${logType}.log`;
      link.click();
      window.URL.revokeObjectURL(url);
    }
  }
};
```

## 🔍 测试验证

### 1. 本地测试
```bash
# 测试API是否响应
curl http://localhost:8000/

# 测试登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### 2. 外网测试
```bash
# 替换为你的外网IP
curl http://your-external-ip:8000/

# 测试CORS
curl -H "Origin: https://your-frontend-domain.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  -X OPTIONS \
  http://your-external-ip:8000/api/v1/auth/login
```

## 🛡️ 安全注意事项

### 1. 生产环境安全
- ✅ 修改默认管理员密码
- ✅ 使用强JWT密钥
- ✅ 设置合适的Token过期时间
- ✅ 配置HTTPS（推荐）
- ✅ 限制CORS源域名

### 2. 网络安全
- ✅ 配置防火墙只开放必要端口
- ✅ 使用Nginx反向代理
- ✅ 配置访问日志监控
- ✅ 定期更新系统补丁

### 3. 数据安全
- ✅ 定期备份数据库
- ✅ 配置日志轮转和清理
- ✅ 监控系统资源使用

## 📞 前端对接信息

### 提供给前端团队的信息

**API基础信息**:
- **API地址**: `http://your-ip:8000` 或 `https://your-domain.com`
- **API文档**: `http://your-ip:8000/docs`
- **WebSocket**: `ws://your-ip:8000/ws`

**测试账号**:
- **用户名**: `admin`
- **密码**: `admin`
- **角色**: `super_admin`

**重要接口**:
- **登录**: `POST /api/v1/auth/login`
- **用户管理**: `/api/v1/users/*`
- **日志管理**: `/api/v1/logs/*`
- **ROS2通信**: `/api/v1/ros2/*`

**注意事项**:
- 所有接口（除登录外）都需要JWT Token认证
- 响应格式统一为JSON，包含code、message、data字段
- 支持CORS跨域访问
- 错误处理统一，详见API文档

## 🔧 故障排除

### 常见问题

**1. 外网无法访问**
- 检查防火墙配置
- 检查路由器端口转发
- 检查应用是否绑定到0.0.0.0

**2. CORS错误**
- 检查CORS_ORIGINS配置
- 确认前端域名已添加到白名单

**3. Token认证失败**
- 检查JWT密钥配置
- 确认Token格式正确
- 检查Token是否过期

**4. 数据库连接失败**
- 检查MySQL服务状态
- 验证数据库连接字符串
- 检查数据库用户权限

### 监控和维护

```bash
# 查看应用状态
sudo systemctl status boshi-inspection

# 查看应用日志
sudo journalctl -u boshi-inspection -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 查看应用日志
tail -f logs/$(date +%Y-%m-%d)/app.log
```

## 📊 性能优化

### 生产环境建议

1. **使用Nginx反向代理**
2. **配置SSL证书（HTTPS）**
3. **设置适当的Worker进程数**
4. **配置数据库连接池**
5. **启用日志轮转和清理**

---

**部署完成后，你的API将在以下地址可用**:
- **内网**: `http://内网IP:8000`
- **外网**: `http://外网IP:8000`
- **域名**: `http://your-domain.com` (如果配置了Nginx)

前端团队可以使用这些地址进行对接测试！🎉

