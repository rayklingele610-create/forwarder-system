# Railway + Neon 持久化部署完整指南

## 你的项目文件清单（已生成）

| 文件 | 说明 | 状态 |
|------|------|------|
| `server_postgres.py` | PostgreSQL 版本服务器（主文件）| ✅ 已创建 |
| `requirements.txt` | 依赖包（含 psycopg2-binary）| ✅ 已更新 |
| `railway.json` | Railway 部署配置 | ✅ 已创建 |
| `Procfile` | 备用启动配置 | ✅ 已创建 |
| `init_neon_db.py` | 一键初始化数据库脚本 | ✅ 已创建 |
| `index.html` | 前端页面 | ✅ 已存在 |

---

## 你的 Neon 连接字符串

```
postgresql://neondb_owner:npg_BqC60vlNfPEX@ep-cold-bread-aov27ss0-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

> ⚠️ 注意：此字符串含密码，请勿分享给他人

---

## 第二步：上传代码到 GitHub

### 方法一：新建 GitHub 仓库（推荐）

1. 访问 https://github.com/new
2. 仓库名：`forwarder-system`
3. 选择 **Private**（私有，保护代码）
4. 点击 "Create repository"

### 上传文件（网页端）

1. 点击 "uploading an existing file"
2. 把以下文件拖进去：
   - `server_postgres.py`
   - `requirements.txt`
   - `railway.json`
   - `Procfile`
   - `index.html`
   - `static/` 文件夹
3. 点击 "Commit changes"

---

## 第三步：Railway 部署

### 3.1 创建新项目

1. 访问 https://railway.app
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub repo"**
4. 授权并选择你的 `forwarder-system` 仓库
5. 点击 **"Deploy Now"**

### 3.2 添加环境变量（关键步骤）

Railway 自动部署后，需要添加数据库连接：

1. 点击你的服务（service）
2. 顶部选择 **"Variables"** 标签
3. 点击 **"New Variable"**，依次添加：

| 变量名 | 值 |
|--------|-----|
| `DATABASE_URL` | `postgresql://neondb_owner:npg_BqC60vlNfPEX@ep-cold-bread-aov27ss0-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require` |
| `PORT` | `8000` |

4. 添加后 Railway 会自动重新部署

### 3.3 获取访问地址

1. 点击 **"Settings"** 标签
2. 找到 **"Networking"** 区域
3. 点击 **"Generate Domain"** 
4. 得到类似：`https://forwarder-system-xxx.up.railway.app`

---

## 第四步：配置 Railway Volume（文件持久化）

> 如果你需要上传二维码图片，需要配置 Volume，否则重启后图片会丢失

1. 在 Railway Dashboard 点击 **"New"** → **"Volume"**
2. 填写：
   - Name: `uploads-volume`
   - Mount Path: `/app/static/uploads`
3. 点击创建
4. 将 Volume 关联到你的服务

---

## 第五步：验证部署

部署完成后访问：
- 前端页面：`https://你的域名.up.railway.app/`
- API 测试：`https://你的域名.up.railway.app/api/forwarders`

---

## 常见问题

### Q: 部署后页面空白？
检查 Railway Logs：服务 → "Deployments" → 最新部署 → "View Logs"

### Q: 数据库连接失败？
确认 DATABASE_URL 变量已正确添加，Neon 控制台确认数据库处于 Active 状态

### Q: 首次访问很慢？
Railway 免费版有冷启动，30秒内正常。升级 $5/月计划可消除冷启动

---

*文件生成时间：2026-05-28*
