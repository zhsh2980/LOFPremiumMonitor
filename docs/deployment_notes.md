# LOF Monitor 部署技术备忘录

> 创建时间：2026-02-01
> 说明：本文档记录了项目部署过程中遇到的技术难点、解决方案及特殊的架构设计，旨在为后续维护提供参考。

## 1. 架构设计决策

### 1.1 抓取任务隔离方案

在将服务部署到 Docker 环境时，我们发现 Playwright 的同步 API (Sync API) 与 FastAPI (基于 uvicorn/asyncio) 的事件循环存在严重的兼容性冲突。

**问题现象**：
- 直接在 FastAPI 应用中运行抓取任务会导致 asyncio 事件循环被阻塞或抛出 `Event loop is closed` 错误。
- 尝试使用 `concurrent.futures.ThreadPoolExecutor` 在独立线程中运行，虽然解决了事件循环冲突，但在 Docker 容器中导致 Playwright 驱动进程挂起（可能是信号处理冲突）。
- 使用 `concurrent.futures.ProcessPoolExecutor` 也因为环境隔离不彻底而表现不稳定。

**最终方案：Subprocess 模式**
为了彻底隔离抓取环境与 Web 服务环境，我们采用了 `subprocess` 模式：
1.  **独立入口**：创建了专门的脚本 `app/run_scrape.py`，它是一个纯粹的同步脚本，没有任何异步代码。
2.  **子进程调用**：调度器 (`scheduler.py`) 通过 `subprocess.run()` 启动一个新的 Python 进程来执行该脚本。

**优点**：
- **完全隔离**：抓取进程与 Web 服务进程互不干扰，即使抓取崩溃也不会影响 API 服务。
- **环境纯净**：每个抓取任务都在一个全新的进程中运行，避免了资源泄漏或状态污染。
- **日志可控**：可以独立捕获子进程的标准输出和错误输出。

### 1.2 Docker 日志配置

为了解决 Python 在 Docker 容器中日志输出缓冲（导致长时间看不到日志）的问题，我们在 `docker-compose.yml` 中设置了环境变量：

```yaml
environment:
  - PYTHONUNBUFFERED=1
```

这确保了 Python 的标准输出（stdout）和标准错误（stderr）是实时刷新的，对于长时间运行的抓取任务尤为重要。

---

## 2. 部署与更新指南

### 2.1 强制重建镜像

由于项目代码包含 Python 依赖变化或 `Dockerfile` 修改，单纯使用 `docker compose restart` 可能不会生效。建议在更新代码后始终使用以下命令：

```bash
# 进入部署目录
cd /srv/lof-monitor

# 拉取最新代码
git pull

# 强制重建并启动 API 服务
docker compose up -d --build api
```

### 2.2 验证部署

部署完成后，可以通过以下步骤验证服务的完整性：

1.  **检查容器状态**：
    ```bash
    docker compose ps
    ```
    确认 `lof-api` 和 `lof-postgres` 状态均为 `healthy`。

2.  **验证抓取日志**：
    监视 API 容器日志，确认子进程成功启动并执行：
    ```bash
    docker logs -f lof-api
    ```
    看到类似 `Subprocess: 抓取任务成功` 的日志即表示正常。

3.  **API 数据检查**：
    请求数据接口，确认返回了最新的抓取数据：
    ```bash
    curl -H "Authorization: Bearer <API_TOKEN>" "http://localhost:8081/api/lof/list?limit=1"
    ```

---

## 3. 故障排查 (Troubleshooting)

### Q1: 抓取任务卡住，日志无输出
**原因**：可能是 Docker 日志缓冲或 Playwright 进程挂起。
**解决**：
1. 确认 `PYTHONUNBUFFERED=1` 已配置。
2. 检查 `docker top lof-api`，看是否有挂起的 `playwright` 进程。
3. 尝试重启容器：`docker compose restart api`。

### Q2: `Event loop is closed` 错误
**原因**：如果在非 Subprocess 模式下使用 Playwright Sync API，通常会遇到此错误。
**解决**：确保始终通过 `app/run_scrape.py` 独立进程运行抓取任务，不要在 FastAPI 的路由或回调中直接调用抓取函数。

### Q3: 容器内代码未更新
**原因**：Docker 镜像缓存。
**解决**：使用 `docker compose up -d --build` 强制构建。

---

## 4. 相关文件

- `app/run_scrape.py`: 独立的抓取脚本入口。
- `app/scheduler.py`: 负责调度任务并启动子进程。
- `app/scraper.py`: 核心抓取逻辑（被 `run_scrape.py` 导入使用）。
- `docker-compose.yml`: 服务编排配置。
