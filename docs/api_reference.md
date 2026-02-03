# LOF Monitor API 接口文档

> 版本：1.0
> 更新时间：2026-02-01
> 适用对象：小程序开发人员、第三方集成人员

## 1. 接入指南

### 1.1 基础信息

- **服务器地址**: `http://154.8.205.159:8081`
- **协议**: HTTP

### 1.2 身份认证 (Authentication)

所有 API 接口（除 `/healthz` 外）均需要通过 **Bearer Token** 进行身份验证。

- **获取 Token**: 请联系服务器管理员获取 `API_TOKEN`（在服务器 `.env` 文件中配置）。
- **请求头设置**:
  在 HTTP 请求 Header 中添加 `Authorization` 字段：
  ```
  Authorization: Bearer <YOUR_API_TOKEN>
  ```

---

## 2. 接口列表

### 2.1 获取服务状态

查询系统的运行状态、最后一次数据更新时间及下次抓取计划。

- **接口地址**: `GET /api/status`
- **认证**: 需要

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "last_update": "2026-02-01T19:26:59.800318",    // 最后数据更新时间
    "last_status": "success",                       // 最后一次抓取状态 (success/failed)
    "last_error": null,                             // 如果失败，显示错误信息
    "record_count": 301,                            // 当前数据库中的记录总数
    "next_scrape": "2026-02-01T20:29:00.089945"     // 下一次计划抓取时间
  }
}
```

### 2.2 获取 LOF 溢价数据（推荐）

获取当前溢价率较高的 LOF 基金数据列表。

- **接口地址**: `GET /api/lof/list`
- **认证**: 需要

**请求参数 (Query Parameters)**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `min_premium` | float | 否 | (系统配置值) | 最小溢价率（例如 `5` 代表 5%）。只返回溢价率大于等于该值的记录。 |
| `status` | string | 否 | `all` | 申购状态筛选。可选值：`all` (全部), `open` (开放), `suspended` (暂停), `limited` (限制) |

**请求示例**:
```
GET /api/lof/list?min_premium=2&status=open
```

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "update_time": "2026-02-01T19:26:59.800318",
    "count": 1,
    "items": [
      {
        "fund_code": "161232",           // 基金代码
        "fund_name": "国投瑞盛LOF",      // 基金名称
        "fund_tags": [],                 // 标签 (如 T+0, QD)
        "price": 1.439,                  // 现价
        "nav": 1.3726,                   // 净值
        "premium_rate": 4.84,            // 溢价率 (%)
        "apply_fee": "1.50%",            // 申购费率
        "apply_status": "open",          // 申购状态
        "apply_limit": null,             // 申购限额
        "redeem_fee": "1.50%",           // 赎回费率
        "redeem_status": "开放赎回",     // 赎回状态
        "shares_change": -1.0,           // 份额变化
        "amount": 13.54,                 // 成交额 (万元)
        "styles": {                      // 样式信息 (原始展示风格)
          "change_pct": {
            "color": "#ff0000"           // 涨跌幅文字颜色 (HEX格式)
          },
          "premium_rate": {
            "color": "#ff0000"           // 溢价率文字颜色
          },
          "apply_status": {
            "color": "#008000",          // 申购状态文字颜色
            "backgroundColor": null      // 申购状态背景色
          }
        }
      }
    ]
  }
}
```

### 2.3 获取所有 LOF 数据

获取数据库中所有的 LOF 基金数据，不进行溢价率筛选。

- **接口地址**: `GET /api/lof/all`
- **认证**: 需要

**请求参数**:
- `status`: 申购状态筛选 (同上)

### 2.4 获取抓取日志

查看最近的后台抓取任务执行记录，用于监控或排查问题。

- **接口地址**: `GET /api/logs`
- **认证**: 需要

**请求参数**:
- `limit`: 返回记录数（默认 10，最大 50）

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "count": 10,
    "items": [
      {
        "id": 15,
        "scrape_time": "2026-02-01T19:26:59.800318",
        "status": "success",
        "new_records": 301,
        "duration_seconds": 42.26,
        "error_message": null
      }
    ]
  }
}
```

### 2.5 健康检查

用于负载均衡器或监控系统检查服务是否存活。

- **接口地址**: `GET /healthz`
- **认证**: **不需要**

**响应**:
```json
{"status": "ok"}
```

---

## 3. 标准响应结构

所有业务接口（除 `/healthz`）均遵循统一的 JSON 响应格式：

```json
{
  "code": 0,          // 状态码：0 表示成功，非 0 表示错误
  "message": "...",   // 状态描述
  "data": { ... }     // 业务数据
}
```

**错误响应示例**:
```json
{
  "detail": "Invalid token" // HTTP 401 Unauthorized
}
```

## 4. 常见问题

**Q: Token 无效怎么办？**
A: 请确认请求头中 `Authorization` 的格式是否严格为 `Bearer <TOKEN>`（注意中间的空格）。如果确认格式无误，请联系管理员重置 Token。

**Q: 为什么数据没有实时更新？**
A: 本服务依赖后台定时爬虫（默认每小时左右抓取一次）。请通过 `/api/status` 查看 `last_update` 确认数据时效性。
