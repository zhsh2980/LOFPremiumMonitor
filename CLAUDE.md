# Project Context: LOF Premium Monitor

## 🔑 Credentials & Secrets
- **集思录账号密码**:
  - 存储位置: `/Users/zhangshan/Documents/AIProject/LOFPremiumMonitor/key/集思录账号.txt`
  - 使用说明: 仅用于 scraper 登录。账号通常为手机号。
- **Server SSH Key**:
  - 位置: `/Users/zhangshan/Documents/AIProject/LOFPremiumMonitor/key/ubuntu_beijing.pem`
  - 登录命令: `ssh -i key/ubuntu_beijing.pem ubuntu@154.8.205.159`
- **Environment Variables**:
  - 模板文件: `.env.example`
  - 实际配置: `.env` (不入库，包含 API_TOKEN 和 数据库密码)

## 🕷️ Scraping Workflow (集思录 LOF 套利)
本项目核心功能是抓取 [集思录 LOF 套利页面](https://www.jisilu.cn/data/lof/#arb)。

**1. Login Process**:
   - URL: `https://www.jisilu.cn/account/login/`
   - Action: 填写账号密码 -> 勾选"记住我" -> 提交。
   - Persistence: 登录成功后保存 Browser Context 到 `auth_state.json` 以复用 Session。

**2. Data Extraction**:
   - Target Page: `https://www.jisilu.cn/data/lof/#arb`
   - Table Selector: `#flex_arb`
   - **Fields Mapping**:
     - `fund_code`: cell[0]
     - `price` (现价): cell[2]
     - `change_pct` (涨幅): cell[3]
     - `premium_rate` (溢价率): cell[5]
     - `apply_status` (申购状态): cell[12]
   - **Style Extraction (Unique Feature)**:
     - 必须抓取原始样式（颜色）以在前端还原显示。
     - 使用 `window.getComputedStyle(el).color/backgroundColor`。
     - 格式: 必须转换为 HEX (`#RRGGBB`) 格式。
     - 涉及字段: `change_pct_color`, `premium_rate_color`, `apply_status_color`, `apply_status_bg_color`.

## 🛠️ Development & Deployment
- **Local Run**: `python -m app.run_scrape` (手动触发抓取)
- **Deployment**:
  - 使用 Docker Compose 部署。
  - 更新代码后必须重建: `docker compose up -d --build`
  - 数据库迁移: 手动执行 `psql -f migrations/xxx.sql`

## 📂 Project Structure
- `app/scraper.py`: 核心抓取逻辑 (Playwright).
- `app/models.py`: 数据库模型 (SQLAlchemy).
- `app/scheduler.py`: 定时任务 (subprocess 独立进程运行 scraper).
- `docs/`: 包含部署文档、API文档和安全指南.
