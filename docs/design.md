# LOF 溢价监控服务 - 设计文档

> 版本：1.0  
> 创建时间：2026-02-01  
> 作者：AI Assistant

## 1. 项目概述

### 1.1 背景

LOF（Listed Open-Ended Fund，上市型开放式基金）在二级市场交易价格与基金净值之间可能存在溢价或折价。当溢价率较高时，存在套利机会。本项目旨在提供一个自动化监控服务，定时抓取 LOF 溢价数据，为微信小程序用户提供实时查询接口。

### 1.2 目标

1. **自动化抓取**：从集思录网站定时抓取 LOF 套利数据
2. **数据存储**：将最新数据存入数据库，供用户查询
3. **API 服务**：为微信小程序提供安全、稳定的数据接口
4. **避免限制**：通过合理的抓取策略，避免触发网站的访问限制

### 1.3 非目标

- 不存储历史数据（只保留最新一次抓取的数据）
- 不提供搜索和复杂筛选功能
- 不直接面向最终用户，仅作为微信小程序的后端服务

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   微信小程序     │────▶│   API 服务       │────▶│   PostgreSQL    │
│   (客户端)       │◀────│   (FastAPI)     │◀────│   (数据库)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               │ 定时触发
                               ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   定时任务       │────▶│   集思录网站     │
                        │   (Scheduler)   │◀────│   (数据源)       │
                        └─────────────────┘     └─────────────────┘
```

### 2.2 组件说明

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| API 服务 | FastAPI | 高性能异步 Web 框架，自动生成 OpenAPI 文档 |
| 数据库 | PostgreSQL | 可靠的关系型数据库 |
| 数据抓取 | Playwright | 支持动态页面渲染，可模拟登录 |
| 定时任务 | APScheduler | 轻量级调度器，内置于应用中 |
| 容器化 | Docker Compose | 简化部署和运维 |

### 2.3 技术选型理由

**FastAPI vs Flask/Django**
- FastAPI 原生支持异步，性能更好
- 自动生成 API 文档，便于调试
- 类型提示支持完善，代码更易维护

**Playwright vs Selenium/Requests**
- 集思录页面使用 JavaScript 动态加载数据，纯 HTTP 请求无法获取
- Playwright 比 Selenium 更现代，API 更简洁
- 支持 headless 模式，资源占用更少

**APScheduler vs Celery**
- 本项目定时任务简单，不需要分布式任务队列
- APScheduler 轻量，配置简单，适合单进程应用
- 减少部署复杂度（无需 Redis/RabbitMQ）

## 3. 数据库设计

### 3.1 数据表结构

#### lof_data 表（LOF 基金数据）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | SERIAL | 主键 |
| fund_code | VARCHAR(10) | 基金代码 |
| fund_name | VARCHAR(100) | 基金名称 |
| price | DECIMAL(10,4) | 场内价格 |
| nav | DECIMAL(10,4) | 基金净值 |
| nav_date | DATE | 净值日期 |
| premium_rate | DECIMAL(6,3) | 溢价率（%） |
| volume | BIGINT | 成交量 |
| amount | DECIMAL(15,2) | 成交额 |
| apply_status | VARCHAR(20) | 申购状态：open/limited/suspended |
| apply_limit | VARCHAR(50) | 限额说明 |
| redeem_status | VARCHAR(20) | 赎回状态 |
| created_at | TIMESTAMP | 创建时间 |

#### scrape_log 表（抓取日志）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | SERIAL | 主键 |
| scrape_time | TIMESTAMP | 抓取时间 |
| status | VARCHAR(20) | 状态：success/failed |
| record_count | INTEGER | 抓取记录数 |
| error_message | TEXT | 错误信息（如果失败） |
| duration_seconds | DECIMAL(6,2) | 耗时（秒） |

### 3.2 索引设计

```sql
-- 溢价率索引，用于筛选
CREATE INDEX idx_lof_premium_rate ON lof_data(premium_rate DESC);

-- 申购状态索引
CREATE INDEX idx_lof_apply_status ON lof_data(apply_status);

-- 抓取日志时间索引
CREATE INDEX idx_scrape_log_time ON scrape_log(scrape_time DESC);
```

### 3.3 数据更新策略

每次抓取成功后：
1. 清空 `lof_data` 表（使用 TRUNCATE）
2. 批量插入新数据
3. 记录抓取日志到 `scrape_log`

使用事务确保数据一致性。

## 4. API 设计

### 4.1 接口列表

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/lof/list | 获取溢价数据（默认 ≥3%） | ✅ |
| GET | /api/lof/all | 获取全部数据 | ✅ |
| GET | /api/status | 获取服务状态 | ✅ |
| GET | /healthz | 健康检查 | ❌ |

### 4.2 认证机制

使用 Bearer Token 认证：

```
Authorization: Bearer <API_TOKEN>
```

Token 通过环境变量 `API_TOKEN` 配置，所有请求（除 `/healthz`）都需要验证。

### 4.3 接口详细设计

#### GET /api/lof/list

**功能**：获取溢价率达到阈值的 LOF 数据

**请求参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| min_premium | float | 否 | 3.0 | 最小溢价率（%） |
| status | string | 否 | all | 申购状态筛选 |

**响应格式**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "update_time": "2026-02-01T15:30:00",
    "count": 5,
    "items": [
      {
        "fund_code": "161725",
        "fund_name": "招商中证白酒指数(LOF)A",
        "price": 1.234,
        "nav": 1.200,
        "nav_date": "2026-02-01",
        "premium_rate": 2.83,
        "volume": 12345678,
        "amount": 15234567.89,
        "apply_status": "limited",
        "apply_limit": "1000元"
      }
    ]
  }
}
```

#### GET /api/lof/all

与 `/api/lof/list` 相同，但不做溢价率筛选。

#### GET /api/status

**响应格式**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "last_update": "2026-02-01T15:30:00",
    "last_status": "success",
    "record_count": 150,
    "next_scrape": "2026-02-01T16:35:00"
  }
}
```

### 4.4 错误码设计

| code | 说明 |
|------|------|
| 0 | 成功 |
| 401 | 未授权（Token 无效或缺失） |
| 500 | 服务器内部错误 |

## 5. 抓取模块设计

### 5.1 抓取流程

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  启动    │────▶│  登录    │────▶│ 访问页面 │────▶│ 解析数据 │
│ 浏览器   │     │ 集思录   │     │ LOF套利  │     │ 表格内容 │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                                                      │
                                                      ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  记录    │◀────│  更新    │◀────│  验证    │◀────│  切换    │
│  日志    │     │  数据库  │     │  数据    │     │ 申购状态 │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### 5.2 登录流程

1. 访问登录页面 `https://www.jisilu.cn/account/login/`
2. 填入用户名和密码
3. 点击登录按钮
4. 等待登录成功，检查是否跳转
5. 保存登录状态（Cookie）

### 5.3 数据抓取

1. 访问 LOF 套利页面 `https://www.jisilu.cn/data/lof/#arb`
2. 等待表格数据加载完成
3. 切换到目标申购状态（限额/全部）
4. 提取表格中的数据
5. 解析并验证数据格式

### 5.4 异常处理

| 异常类型 | 处理方式 |
|----------|----------|
| 登录失败 | 记录错误日志，等待下次重试 |
| 页面加载超时 | 重试 3 次，失败后记录日志 |
| 数据解析错误 | 跳过错误行，记录警告日志 |
| 网络错误 | 重试 3 次，失败后记录日志 |

### 5.5 抓取策略

- **抓取时间**：7:00 - 24:00
- **抓取间隔**：随机 50-70 分钟（平均 60 分钟）
- **随机化目的**：避免固定时间点访问，降低被识别为爬虫的风险

## 6. 定时任务设计

### 6.1 调度器配置

使用 APScheduler 的 `IntervalTrigger`，配合自定义逻辑实现随机间隔：

```python
# 伪代码
def schedule_next_scrape():
    # 检查当前时间是否在抓取时段
    now = datetime.now()
    if 0 <= now.hour < 7:
        # 凌晨时段，安排到 7:00 后执行
        next_run = now.replace(hour=7, minute=random.randint(0, 30))
    else:
        # 正常时段，50-70 分钟后执行
        delay_minutes = random.randint(50, 70)
        next_run = now + timedelta(minutes=delay_minutes)
    
    scheduler.add_job(scrape_job, trigger='date', run_date=next_run)
```

### 6.2 任务生命周期

1. 应用启动时初始化调度器
2. 立即执行一次抓取（如果在允许时段）
3. 抓取完成后，安排下一次任务
4. 应用关闭时优雅停止调度器

## 7. 安全设计

### 7.1 敏感信息保护

- 集思录账号密码通过环境变量注入，不写入代码
- API Token 通过环境变量配置
- `.env` 文件不提交到 Git
- `key/` 目录已加入 `.gitignore`

### 7.2 API 安全

- 所有数据接口需要 Token 认证
- Token 验证失败返回 401 状态码
- 健康检查接口 `/healthz` 不需要认证（供 Docker 健康检查使用）

### 7.3 数据库安全

- 数据库不暴露公网端口
- 使用 Docker 内部网络通信
- 数据库密码通过环境变量配置

## 8. 部署架构

### 8.1 Docker 容器

| 容器名 | 镜像 | 说明 |
|--------|------|------|
| lof-api | 自定义构建 | FastAPI 应用 + 定时任务 + Playwright |
| lof-postgres | postgres:15 | PostgreSQL 数据库 |

### 8.2 Docker Compose 网络

```yaml
networks:
  lof-network:
    driver: bridge
```

两个容器通过 `lof-network` 内部网络通信，数据库仅在内部可访问。

### 8.3 端口映射

- API 服务：`8081:8000`（使用 8081 避免与现有服务冲突）

### 8.4 数据持久化

```yaml
volumes:
  lof-postgres-data:
```

PostgreSQL 数据存储在 Docker Volume 中，容器重启不会丢失数据。

## 9. 监控与日志

### 9.1 日志记录

- 应用日志输出到 stdout，由 Docker 收集
- 抓取结果记录到 `scrape_log` 表
- 错误日志包含详细的堆栈信息

### 9.2 健康检查

Docker 健康检查配置：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 10. 后续扩展

以下功能不在当前版本范围内，但设计时已考虑扩展性：

1. **历史数据**：可通过增加 `scrape_batch_id` 字段支持
2. **多数据源**：可扩展 scraper 模块支持其他数据源
3. **消息推送**：可增加溢价率预警推送功能
4. **用户系统**：可扩展为多用户多 Token 模式
