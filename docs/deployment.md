# LOF 溢价监控服务 - 部署文档

> 版本：1.1
> 更新时间：2026-02-01
> 说明：本文档包含服务的部署步骤、运维指南、技术架构说明及故障排查手册。

## 1. 服务器信息

| 项目 | 值 |
|------|-----|
| 服务器 IP | 154.8.205.159 |
| SSH 用户 | ubuntu |
| 部署目录 | /srv/lof-monitor |
| 应用端口 | 8081（映射容器内 8000） |

## 2. 首次部署

### 2.1 服务器准备

SSH 登录服务器：

```bash
ssh -i /path/to/ubuntu_beijing.pem ubuntu@154.8.205.159
```

创建部署目录：

```bash
sudo mkdir -p /srv/lof-monitor
sudo chown ubuntu:ubuntu /srv/lof-monitor
```

### 2.2 克隆代码

```bash
cd /srv/lof-monitor
git clone https://github.com/zhsh2980/LOFPremiumMonitor.git .
```

### 2.3 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
nano .env
```

填入以下配置：

```env
# 集思录账号（必填）
JISILU_USERNAME=你的集思录用户名
JISILU_PASSWORD=你的集思录密码

# API 访问令牌（必填，自行生成一个强密码）
API_TOKEN=your_secure_api_token_here

# 数据库配置（使用默认值即可）
POSTGRES_USER=lof_user
POSTGRES_PASSWORD=your_db_password_here
POSTGRES_DB=lof_monitor
DATABASE_URL=postgresql://lof_user:your_db_password_here@lof-postgres:5432/lof_monitor

# Python 日志缓冲配置（防止 Docker 查看日志延迟）
PYTHONUNBUFFERED=1

# 时区
TZ=Asia/Shanghai

# 安全配置：允许访问的 IP (用于后端中转场景)
# 多个 IP 用逗号分隔，如：127.0.0.1,1.2.3.4
# 默认为 * (允许所有)
ALLOWED_IPS=*
```

**生成 API Token 的方法**：

```bash
# 生成 32 位随机字符串
openssl rand -hex 16
```

### 2.4 启动服务

```bash
docker compose up -d --build
```

### 2.5 验证部署

1. 检查容器状态：

```bash
docker compose ps
```

预期输出：
```
NAME           STATUS          PORTS
lof-api        Up (healthy)    0.0.0.0:8081->8000/tcp
lof-postgres   Up              5432/tcp
```

2. 检查健康状态：

```bash
curl http://localhost:8081/healthz
```

3. 检查 API（需要 Token）：

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://localhost:8081/api/status
```

## 3. 日常运维

### 3.1 查看日志

```bash
# 查看 API 服务日志（查看抓取进度的主要方式）
docker logs -f lof-api

# 查看数据库日志
docker logs lof-postgres --tail 50
```

### 3.2 重启服务

```bash
cd /srv/lof-monitor
docker compose restart
```

### 3.3 停止服务

```bash
cd /srv/lof-monitor
docker compose down
```

### 3.4 更新代码（重要）

由于本项目包含 Python 依赖及底层驱动变化，更新代码后**建议强制重建镜像**，以确保新代码生效：

```bash
cd /srv/lof-monitor
git pull

# 强制重建并启动 API 服务
docker compose up -d --build api
```

## 4. 技术架构说明

本节解释了部署架构中的关键设计决策，主要解决 Playwright 在 Docker 环境下的兼容性问题。

### 4.1 抓取任务隔离（Subprocess 模式）

**背景**：
在 Docker 环境中，Playwright 的同步 API (Sync API) 与 FastAPI (基于 uvicorn/asyncio) 的事件循环存在严重的兼容性冲突，常导致 `Event loop is closed` 错误或进程卡死。

**解决方案**：
采用 `subprocess` 模式彻底隔离抓取环境。
- **独立入口**：使用 `app/run_scrape.py` 作为独立的同步脚本入口。
- **进程隔离**：调度器 (`scheduler.py`) 通过 `subprocess.run()` 启动全新的 Python 进程来执行该脚本。

**优势**：
- 即使抓取任务崩溃，也不会影响主 API 服务的稳定性。
- 规避了 Python asyncio与 Playwright 的所有底层冲突。

### 4.2 Docker 日志配置

为了解决 Python 在 Docker 容器中日志输出缓冲（导致长时间看不到日志）的问题，环境变量中配置了 `PYTHONUNBUFFERED=1`。这确保了 Python 的标准输出是实时刷新的。

## 5. 故障排查 (Troubleshooting)

### 5.1 抓取任务卡住 / 日志无输出

**现象**：任务开始后长时间可以在 `docker top` 看到进程但无日志输出，或根本无输出。
**排查**：
1. 确认 `.env` 或 `docker-compose.yml` 中配置了 `PYTHONUNBUFFERED=1`。
2. 检查是否有僵尸进程：`docker top lof-api`。
3. 尝试重启应用：`docker compose restart api`。

### 5.2 "Event loop is closed" 错误

**现象**：日志中出现此错误，通常伴随抓取失败。
**原因**：在 FastAPI 的异步上下文中直接调用了同步的 Playwright 代码。
**解决**：确保始终通过 `app/run_scrape.py` 独立进程运行抓取任务。

### 5.3 代码更新未生效

**现象**：`git pull` 成功且重启容器后，运行的逻辑仍是旧版。
**原因**：Docker 镜像缓存，`COPY` 指令未重新执行。
**解决**：使用 `docker compose up -d --build api` 强制构建。

### 5.4 容器启动失败

**排查**：
```bash
# 查看容器日志
docker logs lof-api
# 检查配置
docker compose config
```

### 5.5 数据库连接失败

**检查命令**：
```bash
# 检查数据库容器状态
docker compose ps lof-postgres
# 尝试手动连接
docker exec -it lof-postgres psql -U lof_user -d lof_monitor
```

## 6. GitHub Actions CI/CD

本项目配置了手动触发的部署工作流。

### 6.1 Secrets 配置
在 GitHub 仓库设置中添加：
- `SERVER_HOST`: 154.8.205.159
- `SERVER_USER`: ubuntu
- `SERVER_SSH_KEY`: (私钥内容)
- `DEPLOY_PATH`: /srv/lof-monitor

### 6.2 触发方式
在 GitHub Actions 页面选择 "Deploy to Server" 手动运行。

## 7. 数据备份与性能

### 7.1 数据库备份
```bash
docker exec lof-postgres pg_dump -U lof_user lof_monitor > backup_$(date +%Y%m%d).sql
```

### 7.2 资源监控
```bash
docker stats lof-api lof-postgres
```
