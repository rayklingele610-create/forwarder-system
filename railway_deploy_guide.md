# Railway + Neon 持久化部署指南

## 方案优势
- ✅ **免费 PostgreSQL 1GB**（Neon 提供）
- ✅ **文件上传持久化**（Railway 持久化存储）
- ✅ **自动部署**（GitHub 集成）
- ✅ **现代云原生架构**

## 第一步：创建 PostgreSQL 数据库（Neon）

### 1.1 注册 Neon
1. 访问：https://neon.tech
2. 点击 "Start for Free"
3. 使用 GitHub 账号登录

### 1.2 创建数据库
1. 登录后点击 "Create Project"
2. 项目名：`forwarder-system`
3. 点击 "Create Project"
4. 等待数据库创建完成

### 1.3 获取连接信息
1. 在 Dashboard 找到你的项目
2. 点击 "Connection Details"
3. 复制 **Connection String**，格式：
```
postgresql://username:password@ep-cool-bird-123456.us-east-2.aws.neon.tech/dbname
```

## 第二步：修改代码支持 PostgreSQL

### 2.1 创建新版本 server_postgres.py

需要将 SQLite 改为 PostgreSQL，主要修改：

```python
# 数据库连接部分
import os
import psycopg2
from psycopg2.extras import Json

# 从环境变量获取连接字符串
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode='require')
```

### 2.2 修改数据库操作
- 所有 `sqlite3.connect()` 改为 `get_conn()`
- JSON 字段使用 `Json()` 包装
- 表结构需要调整

## 第三步：部署到 Railway

### 3.1 注册 Railway
1. 访问：https://railway.app
2. 点击 "Start for Free"
3. 使用 GitHub 账号登录

### 3.2 创建项目
1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 授权访问你的仓库

### 3.3 配置环境变量
1. 在 Railway Dashboard 点击你的项目
2. 选择 "Variables"
3. 添加：
   - `DATABASE_URL`: 你的 Neon 连接字符串
   - `PORT`: `8000`

### 3.4 配置部署
Railway 会自动检测并部署，如果需要手动配置：

1. 创建 `railway.json`：
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn server_postgres:app",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## 第四步：配置持久化存储（文件上传）

### 4.1 Railway Volumes
1. 在 Railway Dashboard 点击 "New" → "Volume"
2. 名称：`uploads-volume`
3. 挂载路径：`/app/static/uploads`
4. 大小：1GB（免费）

### 4.2 修改上传路径
在 `server_postgres.py` 中：
```python
UPLOAD_FOLDER = '/app/static/uploads'
```

## 第五步：访问地址
部署完成后，Railway 会提供：
- `https://forwarder-system.up.railway.app`

## 免费额度
- **Railway**：$5 信用（约 500 小时/月）
- **Neon**：1GB PostgreSQL 免费
- **存储**：1GB 持久化卷

## 注意事项
1. 需要修改代码支持 PostgreSQL
2. 免费额度足够个人项目使用
3. 国内访问速度一般
4. 需要一定的技术调整

## 简化方案：使用 PythonAnywhere
如果不想修改代码，**PythonAnywhere 是更好的选择**，它：
- ✅ 原生支持 SQLite（无需修改代码）
- ✅ 文件系统持久化
- ✅ 无需信用卡
- ✅ 部署更简单

建议先尝试 PythonAnywhere，如果不能满足需求再考虑 Railway + Neon。
