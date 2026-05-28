# 腾讯云部署方案详细指南

## 方案对比

| 方案 | 费用 | 代码改动 | 持久化 | 适合 |
|------|------|----------|--------|------|
| 🌟 **轻量应用服务器** | ~50元/月 | 无需改动 | ✅ | 最推荐（简单稳定） |
| CloudBase 云托管 | 19.9元/月起 | 需改数据库 | ✅ | 预算有限 |
| CloudBase 云函数 | 按量计费 | 需大幅改造 | ✅ | 不太适合 |
| PythonAnywhere | 免费 | 无需改动 | ✅ | 零成本 |

> **关键问题**：你的系统使用 SQLite 数据库。CloudBase 云托管的容器是临时的，重启后 SQLite 数据会丢失，必须改用云数据库（MySQL）。轻量应用服务器是完整的虚拟机，SQLite 直接可用，代码零改动。

---

## 推荐：腾讯云轻量应用服务器（最简单，代码零改动）

### 购买配置
| 项目 | 配置 |
|------|------|
| CPU | 2核 |
| 内存 | 2GB |
| 系统盘 | 40GB SSD |
| 带宽 | 3Mbps |
| 系统 | Ubuntu 22.04 或 Windows Server |
| 价格 | 约 50-68 元/月（新用户首年优惠） |

### 第一步：购买服务器

1. 访问：https://cloud.tencent.com/product/lighthouse
2. 点击"立即选购"
3. 选择配置：
   - 地域：选择离你最近的（如广州、上海）
   - 镜像：Ubuntu 22.04（推荐）或 Windows Server
   - 套餐：2核2GB（够用）
4. 设置 root 密码
5. 完成购买

### 第二步：连接到服务器

**Windows 系统**（如果服务器也是 Windows）：
- 使用远程桌面连接（RDP）
- 在腾讯云控制台点击"登录" → "远程桌面"

**Linux 系统**（推荐，更省资源）：
- 下载 FinalShell：http://www.hostbuf.com
- 或使用自带的远程登录（浏览器内）

### 第三步：安装环境（Ubuntu 为例）

SSH 登录后执行：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3 和 pip
sudo apt install python3 python3-pip -y

# 安装 Git
sudo apt install git -y

# 安装依赖
sudo apt install python3-flask python3-flask-cors -y
```

### 第四步：上传代码

**方法一：使用 FinalShell（推荐）**

1. 打开 FinalShell，连接服务器
2. 在左侧文件管理器，进入 `/home/ubuntu/`
3. 创建文件夹：`forwarder-system`
4. 从本地拖拽文件到服务器

**方法二：使用 Git**

```bash
# 在服务器上
cd /home/ubuntu
git clone https://github.com/你的用户名/forwarder-system.git
cd forwarder-system
```

### 第五步：安装 Python 依赖

```bash
cd /home/ubuntu/forwarder-system
pip3 install flask flask-cors gunicorn
```

### 第六步：启动应用

```bash
# 方式一：直接运行（测试用）
python3 server.py

# 方式二：使用 gunicorn（生产环境）
gunicorn -w 2 -b 0.0.0.0:8000 server:app --daemon

# 方式三：使用 nohup 后台运行
nohup gunicorn -w 2 -b 0.0.0.0:8000 server:app > app.log 2>&1 &
```

### 第七步：配置防火墙

1. 在腾讯云控制台 → 轻量应用服务器
2. 点击你的服务器 → "防火墙"
3. 添加规则：
   - 应用类型：自定义
   - 协议：TCP
   - 端口：8000
   - 策略：允许

### 第八步：配置 Nginx（可选，推荐）

```bash
# 安装 Nginx
sudo apt install nginx -y

# 创建配置
sudo nano /etc/nginx/sites-available/forwarder
```

写入以下内容：
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/forwarder-system/static/;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/forwarder /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 第九步：访问应用

```
http://你的服务器公网IP
或
http://你的服务器公网IP:8000
```

### 第十步：设置开机自启

创建 systemd 服务：

```bash
sudo nano /etc/systemd/system/forwarder.service
```

写入：
```ini
[Unit]
Description=Forwarder Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/forwarder-system
ExecStart=/usr/local/bin/gunicorn -w 2 -b 0.0.0.0:8000 server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable forwarder
sudo systemctl start forwarder
sudo systemctl status forwarder
```

---

## 方案二：CloudBase 云托管（已创建 Dockerfile）

### 第一步：开通 CloudBase

1. 访问：https://console.cloud.tencent.com/tcb
2. 点击"新建环境"
3. 选择"按量计费"（新用户有免费额度）
4. 环境名称：`forwarder-system`
5. 点击"立即开通"

### 第二步：部署到云托管

1. 进入你的环境 → "云托管"
2. 点击"新建服务"
3. 服务名称：`forwarder`
4. 上传方式：本地代码
5. 上传整个项目文件夹（已包含 Dockerfile）
6. 端口：8000
7. 点击"部署"

### 第三步：配置云数据库（解决 SQLite 持久化问题）

> ⚠️ CloudBase 容器重启后 SQLite 数据会丢失，需要改用云数据库

1. 进入"云数据库" → "新建集合"
2. 修改 server.py 使用 MySQL
3. 需要添加 `pymysql` 依赖

**改造 server.py 示例**：
```python
import pymysql
import os

# 从环境变量获取数据库配置
DB_HOST = os.environ.get('MYSQL_HOST', 'localhost')
DB_PORT = int(os.environ.get('MYSQL_PORT', 3306))
DB_USER = os.environ.get('MYSQL_USER', 'root')
DB_PASS = os.environ.get('MYSQL_PASS', '')
DB_NAME = os.environ.get('MYSQL_DB', 'forwarder')

def get_conn():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, charset='utf8mb4'
    )
```

### 第四步：配置云存储（文件上传持久化）

1. 进入"云存储"
2. 创建存储桶
3. 修改 server.py 中的上传逻辑

---

## 方案三：免费方案 PythonAnywhere（零成本）

如果不想花钱，这是**唯一真正免费且支持 SQLite 持久化**的方案。

### 快速步骤

1. 注册：https://www.pythonanywhere.com
2. 上传文件到 `/home/你的用户名/`
3. 配置 Web App（Manual configuration → Python 3.11）
4. 修改 WSGI 文件指向 `server.py`
5. 重启应用

访问：`https://你的用户名.pythonanywhere.com`

### 优点
- ✅ 完全免费，无时间限制
- ✅ SQLite 持久化存储
- ✅ 文件上传永久保存
- ✅ 无需信用卡

### 缺点
- ❌ 国外服务器，国内访问稍慢
- ❌ 免费版不支持自定义域名
- ❌ 每 3 个月需点击一次"续期"

---

## 立即行动建议

| 预算 | 推荐方案 | 代码改动 | 持久化 | 速度 |
|------|----------|----------|--------|------|
| **0 元** | PythonAnywhere | 无需改动 | ✅ | 慢 |
| **50元/月** | 轻量应用服务器 | 无需改动 | ✅ | 快 |
| **20元/月** | CloudBase 云托管 | 需要改 | ✅ | 极快 |

**个人建议**：先用 PythonAnywhere 免费部署测试，稳定后再考虑升级到腾讯云轻量服务器。

---

## 已创建的部署文件

本项目已包含以下部署文件：

- `Dockerfile`：CloudBase 云托管所需的容器配置
- `.dockerignore`：排除不需要打包的文件
- `requirements.txt`：Python 依赖列表