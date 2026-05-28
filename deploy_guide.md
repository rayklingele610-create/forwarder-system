# 货代信息查询系统 - 免费公网部署指南

## 方案选择：frp 内网穿透（国内可用，免费）

### 原理
- 在本地运行 frp 客户端，连接到一个公网 frp 服务器
- 公网服务器将流量转发到你的本地 `localhost:5000`
- 用户访问公网域名即可访问你的系统

### 步骤

#### 1. 获取免费 frp 服务器
国内有几个提供免费 frp 服务的平台：

| 平台 | 地址 | 特点 |
|------|------|------|
| frp.freefrp.net | https://frp.freefrp.net | 免费，国内节点，需注册 |
| frps.cn | https://frps.cn | 免费额度，简单易用 |
| 自建（可选） | 租用一台国内云服务器（约50元/月） | 完全控制 |

推荐 **frp.freefrp.net**，注册后：
1. 登录控制台
2. 创建一个隧道（Tunnel）
3. 类型：HTTP
4. 本地端口：5000
5. 获取：服务器地址、端口、token

#### 2. 下载 frp 客户端
访问：https://github.com/fatedier/frp/releases
下载 `frp_0.xx.x_windows_amd64.zip`，解压到项目目录。

#### 3. 配置 frpc.ini
在 `output` 目录创建 `frpc.ini`：

```ini
[common]
server_addr = 你的服务器地址
server_port = 你的服务器端口
token = 你的token

[web]
type = http
local_port = 5000
custom_domains = 你分配的子域名
```

#### 4. 启动 frp 和系统
创建启动脚本 `start.bat`：

```batch
@echo off
cd /d "C:\Users\Administrator\AppData\Roaming\Tencent\Marvis\User\oAN1i2dbhPbk2vUBQt4MbxT5Kny8\workspace\conv_19e66fb76dd_230d268090ea\output"
start python server.py
timeout /t 3
start frpc.exe -c frpc.ini
```

双击运行即可。

#### 5. 访问地址
用户访问：`http://你分配的子域名.frp.freefrp.net`

## 备选方案：使用现成的国内免费托管

### 1. 腾讯云 CloudBase（云开发）
- 免费额度：1GB存储，2GB流量/月
- 支持静态网站 + 云函数（可运行 Python）
- 国内访问速度快
- 步骤：
  1. 注册腾讯云账号
  2. 开通云开发 CloudBase
  3. 上传 `index.html` 到静态托管
  4. 将后端 API 改写成云函数

### 2. 阿里云函数计算 FC
- 每月免费调用次数 100万次
- 支持 Python 运行时
- 可搭配 API 网关提供 HTTP 服务
- 需要将 Flask 应用改造成函数

### 3. 华为云 FunctionGraph
- 类似阿里云函数计算
- 免费额度充足

## 最简单方案：使用现成的 Python 托管平台

### PythonAnywhere（国外，但国内可访问）
1. 注册免费账号
2. 上传 `server.py` 和 `index.html`
3. 配置 Web App
4. 获得 `xxx.pythonanywhere.com` 域名

### Render.com（国外，国内访问较慢）
免费计划，每月750小时，支持 Python。

## 推荐流程

1. **立即可用**：局域网 `http://192.168.0.190:5000`
2. **短期公网**：用 **frp.freefrp.net**（30分钟搞定）
3. **长期稳定**：申请 **腾讯云 CloudBase** 免费额度

## 注意事项
- 免费服务可能有带宽/流量限制
- 国内平台需实名认证
- 数据库文件（forwarders.db）需定期备份
- 多人同时编辑时建议设置操作权限

## 一键部署脚本（frp方案）
我已创建了配置文件模板，你只需：
1. 注册 frp.freefrp.net
2. 填写 `frpc.ini` 中的三个参数
3. 运行 `start.bat`

系统将同时启动本地服务和 frp 穿透，获得公网访问地址。