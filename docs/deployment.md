# LOF 溢价监控服务 - 部署文档

> 版本：1.0  
> 创建时间：2026-02-01  
> 作者：AI Assistant

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

# 时区
TZ=Asia/Shanghai
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

预期输出：
```json
{"status": "ok"}
```

3. 检查 API（需要 Token）：

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://localhost:8081/api/status
```

## 3. 日常运维

### 3.1 查看日志

```bash
# 查看 API 服务日志
docker logs lof-api --tail 100

# 实时跟踪日志
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

### 3.4 更新代码

```bash
cd /srv/lof-monitor
git pull
docker compose up -d --build
```

## 4. GitHub Actions CI/CD

本项目配置了手动触发的 CI/CD，可以通过 GitHub 页面触发部署。

### 4.1 配置 GitHub Secrets

在 GitHub 仓库的 `Settings > Secrets and variables > Actions` 中添加以下 Secrets：

| Secret 名称 | 说明 |
|-------------|------|
| SERVER_HOST | 服务器 IP：154.8.205.159 |
| SERVER_USER | SSH 用户：ubuntu |
| SERVER_SSH_KEY | SSH 私钥内容（ubuntu_beijing.pem 的内容） |
| DEPLOY_PATH | 部署路径：/srv/lof-monitor |

### 4.2 添加 SSH 私钥

将本地 SSH 密钥的**内容**复制到 Secrets：

```bash
cat /path/to/ubuntu_beijing.pem
```

复制全部内容（包括 `-----BEGIN RSA PRIVATE KEY-----` 和 `-----END RSA PRIVATE KEY-----`）。

### 4.3 触发部署

1. 打开 GitHub 仓库页面
2. 点击 `Actions` 标签
3. 选择 `Deploy to Server` 工作流
4. 点击 `Run workflow` 按钮
5. 选择分支，点击 `Run workflow` 确认

### 4.4 工作流文件

工作流配置位于 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Server

on:
  workflow_dispatch:  # 手动触发

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd ${{ secrets.DEPLOY_PATH }}
            git pull origin main
            docker compose up -d --build
```

## 5. 常见问题

### 5.1 容器启动失败

**问题**：`docker compose up` 后容器立即退出

**排查步骤**：

```bash
# 查看容器日志
docker logs lof-api

# 检查环境变量
docker compose config
```

**常见原因**：
- `.env` 文件配置错误
- 数据库连接字符串格式错误
- Python 依赖安装失败

### 5.2 无法访问 API

**问题**：`curl http://154.8.205.159:8081` 无响应

**排查步骤**：

```bash
# 检查容器端口映射
docker compose ps

# 检查防火墙（如果使用）
sudo ufw status

# 从容器内部测试
docker exec lof-api curl http://localhost:8000/healthz
```

### 5.3 抓取失败

**问题**：数据一直没有更新

**排查步骤**：

```bash
# 查看 API 日志中的抓取记录
docker logs lof-api 2>&1 | grep -i scrape

# 检查抓取日志表
docker exec lof-postgres psql -U lof_user -d lof_monitor -c "SELECT * FROM scrape_log ORDER BY scrape_time DESC LIMIT 5;"
```

**常见原因**：
- 集思录账号密码错误
- 集思录会员过期
- 网络问题
- Playwright 初始化失败

### 5.4 数据库连接失败

**问题**：应用无法连接数据库

**排查步骤**：

```bash
# 检查数据库容器状态
docker compose ps lof-postgres

# 尝试手动连接
docker exec -it lof-postgres psql -U lof_user -d lof_monitor

# 检查 DATABASE_URL 格式
# 正确格式：postgresql://user:password@host:port/database
```

## 6. 数据备份

### 6.1 备份数据库

```bash
docker exec lof-postgres pg_dump -U lof_user lof_monitor > backup_$(date +%Y%m%d).sql
```

### 6.2 恢复数据库

```bash
docker exec -i lof-postgres psql -U lof_user lof_monitor < backup_20260201.sql
```

## 7. 性能监控

### 7.1 查看资源使用

```bash
docker stats lof-api lof-postgres
```

### 7.2 查看磁盘使用

```bash
docker system df

# 清理未使用的镜像和容器
docker system prune -a
```

## 8. 与现有服务隔离

本项目与服务器上已有的 `opportunity-insight` 项目完全隔离：

| 项目 | 目录 | 端口 | 数据库容器 | 网络 |
|------|------|------|------------|------|
| opportunity-insight | /srv/opportunity-insight | 8080 | radar-postgres | radar-network |
| **lof-monitor** | /srv/lof-monitor | 8081 | lof-postgres | lof-network |

两个项目：
- 使用不同的目录
- 使用不同的端口
- 使用独立的 Docker 网络
- 使用独立的数据库容器和 Volume
- 互不影响
