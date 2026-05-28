# Render.com 部署详细步骤

## 第一步：准备 GitHub 仓库

### 1.1 注册 GitHub 账号
- 访问：https://github.com
- 点击 "Sign up" 注册新账号（如果已有账号则登录）

### 1.2 创建新仓库
1. 登录后点击右上角 "+" → "New repository"
2. 填写仓库信息：
   - **Repository name**：`forwarder-system`（或自定义名称）
   - **Description**：货代信息查询系统
   - 选择 **Public**（公开仓库）
   - **不要勾选**：
     - ☐ Add a README file
     - ☐ Add .gitignore
     - ☐ Choose a license
3. 点击 "Create repository"

### 1.3 获取仓库地址
创建成功后，你会看到类似这样的地址：
```
https://github.com/你的用户名/forwarder-system.git
```
复制这个地址，后面会用到。

## 第二步：上传代码到 GitHub

### 2.1 安装 Git
- 下载地址：https://git-scm.com/download/win
- 安装时一路点击 "Next" 即可

### 2.2 使用 Git Bash 上传代码

打开 Git Bash（在开始菜单搜索），依次执行以下命令：

```bash
# 1. 进入项目目录
cd "C:\Users\Administrator\AppData\Roaming\Tencent\Marvis\User\oAN1i2dbhPbk2vUBQt4MbxT5Kny8\workspace\conv_19e66fb76dd_230d268090ea\output"

# 2. 初始化 Git
git init

# 3. 添加所有文件
git add .

# 4. 提交更改
git commit -m "Initial commit: 货代信息查询系统"

# 5. 连接到 GitHub（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/forwarder-system.git

# 6. 推送代码
git branch -M main
git push -u origin main
```

**注意**：执行第5、6步时，会弹出 GitHub 登录窗口，输入你的 GitHub 账号密码。

## 第三步：部署到 Render.com

### 3.1 注册 Render 账号
1. 访问：https://render.com
2. 点击 "Get Started"
3. 选择 "Sign up with GitHub"（推荐，最简单）
4. 授权 Render 访问你的 GitHub 账号

### 3.2 创建 Web Service

1. 登录后点击右上角 "New" → "Web Service"

2. 连接 GitHub 仓库：
   - 点击 "Connect account" 连接 GitHub（如果还没连接）
   - 选择你的仓库：`forwarder-system`

3. 配置部署设置：
   - **Name**：`forwarder-system`
   - **Region**：选择 **Singapore**（新加坡，国内访问相对快）
   - **Branch**：`main`
   - **Runtime**：`Python 3`
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`gunicorn server:app`
   - **Plan**：选择 **Free**

4. 点击 "Create Web Service"

## 第四步：等待部署完成

### 4.1 查看部署状态
- Render 会自动开始构建和部署
- 构建过程约 2-5 分钟
- 可以在 Dashboard 看到 "Building" → "Deploying" → "Live" 状态

### 4.2 获取访问地址
部署成功后，你会看到：
- **URL**：`https://forwarder-system.onrender.com`
- 点击这个链接即可访问你的系统

### 4.3 首次访问
首次访问可能需要等待 30-60 秒（免费计划有冷启动时间），之后访问会变快。

## 第五步：验证部署

访问你的系统地址，检查功能是否正常：

1. **首页**：`https://forwarder-system.onrender.com`
2. **API 测试**：`https://forwarder-system.onrender.com/api/forwarders`
3. **标签管理**：点击侧栏齿轮图标，测试增删改功能

## 常见问题解决

### Q1：构建失败怎么办？
检查 Render 的 Build Logs，常见原因：
- 缺少依赖：确保 `requirements.txt` 存在且正确
- Python 版本问题：确保 `requirements.txt` 中的包版本兼容

### Q2：访问显示 502 Bad Gateway？
- 等待 1-2 分钟，免费计划有冷启动
- 检查 Start Command 是否正确：`gunicorn server:app`

### Q3：数据库不工作？
- Render 每次重启会重新初始化数据库
- 这是正常现象，免费计划不支持持久化存储
- 如果需要持久化，可考虑升级到付费计划或使用外部数据库

### Q4：上传图片失败？
- 确保 `static/uploads/` 目录存在
- Render 的免费计划文件系统是临时的，重启后文件会丢失

## Render 免费计划限制

- **运行时间**：每月 750 小时（约 31 天，足够 24/7 运行）
- **带宽**：100GB/月
- **存储**：临时文件系统（重启会丢失）
- **冷启动**：15 分钟无访问后会自动休眠，下次访问需等待 30-60 秒启动
- **自定义域名**：支持，但需要验证域名所有权

## 后续维护

### 更新代码
1. 本地修改代码
2. 执行：
   ```bash
   git add .
   git commit -m "更新描述"
   git push
   ```
3. Render 会自动检测并重新部署

### 查看日志
- 在 Render Dashboard 点击你的 Service
- 选择 "Logs" 标签页
- 可查看实时日志和错误信息

### 监控状态
- Render Dashboard 显示服务状态
- 免费计划支持基本的监控和告警

## 备选方案

如果 Render 访问太慢，可考虑：
1. **Railway**：https://railway.app（类似 Render，国内访问可能稍快）
2. **PythonAnywhere**：https://www.pythonanywhere.com（传统托管，稳定但功能有限）

## 一键部署脚本

我已经为你准备好了所有必要的文件：
- `requirements.txt` - Python 依赖
- `render.yaml` - Render 配置文件
- `server.py` - 已适配 Render 的服务器代码
- `.gitignore` - Git 忽略文件

现在只需按照上述步骤操作即可完成部署！
