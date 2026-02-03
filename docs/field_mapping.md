# 数据字段映射文档

本文档说明了从集思录网站抓取的各个数据源的字段对应关系。

## 1. QDII 商品数据 (表格 ID: `#flex_qdiic`)

**数据源**: https://www.jisilu.cn/data/qdii/#qdiie (商品标签)

| 列索引 | 表头名称 | 字段名 | 数据类型 | 说明 | 有样式 |
|--------|---------|--------|---------|------|--------|
| 0 | 代码 | `fund_code` | String | 基金代码 | ❌ |
| 1 | 名称 | `fund_name` | String | 基金名称 | ❌ |
| 2 | 现价 | `price` | String | 当前价格（原始文本） | ❌ |
| 3 | 涨幅 | `change_pct` | String | 涨跌幅百分比 | ✅ 颜色 |
| 4 | 成交(万元) | `volume` | String | 成交额（万元） | ❌ |
| 5 | 场内份额(万份) | `shares` | String | 场内份额 | ❌ |
| 6 | 场内新增(万份) | `shares_change` | String | 份额变化 | ❌ |
| 7 | T-2净值 | `nav_t2` | String | T-2日净值 | ❌ |
| 8 | 净值日期 | `nav_date` | String | 净值日期 | ❌ |
| 9 | T-1估值 | `valuation_t1` | String | T-1日估值 | ❌ |
| 10 | 估值日期 | `valuation_date` | String | 估值日期 | ❌ |
| 11 | T-1溢价率 | `premium_rate_t1` | String | T-1日溢价率 | ✅ 颜色 |
| 12 | 实时估值 | `rt_valuation` | String | 实时估值 | ❌ |
| 13 | 实时溢价率 | `rt_premium_rate` | String | 实时溢价率 | ✅ 颜色 |
| 14 | 相关标的/业绩比较 | `benchmark` | String | 相关指数或标的 | ❌ |
| 15 | 申购费 | `apply_fee` | String | 申购费率 | ❌ |
| 16 | 申购状态 | `apply_status` | String | 申购状态 | ✅ 颜色 |
| 17 | 赎回费 | `redeem_fee` | String | 赎回费率 | ❌ |
| 18 | 赎回状态 | `redeem_status` | String | 赎回状态 | ❌ |
| 19 | 管托费 | `manage_fee` | String | 基金管理费/托管费 | ❌ |
| 20 | 基金公司 | `fund_company` | String | 管理公司 | ❌ |
| 21 | 操作 | - | - | 操作列（不抓取） | ❌ |

**说明**:
- **共 21 列，全部抓取**
- 字段顺序已根据最新页面结构修正

**样式字段说明**:
- `change_pct_color`: 涨跌幅文字颜色 (HEX 格式，如 `#ff0000` 红色表示涨，`#008000` 绿色表示跌)
- `premium_rate_t1_color`: T-1溢价率文字颜色
- `rt_premium_rate_color`: 实时溢价率文字颜色
- `apply_status_color`: 申购状态文字颜色

**API 接口**: `GET /api/qdii/commodity`

---

## 2. 指数 LOF 数据 (表格 ID: `#flex_index`)

**数据源**: https://www.jisilu.cn/data/lof/#index

**特殊操作**: 抓取前会点击"溢价率"表头两次，实现按溢价率倒序排列

| 列索引 | 表头名称 | 字段名 | 数据类型 | 说明 | 有样式 |
|--------|---------|--------|---------|------|--------|
| 0 | 代码 | `fund_code` | String | 基金代码 | ❌ |
| 1 | 名称 | `fund_name` | String | 基金名称 | ❌ |
| 2 | 现价 | `price` | String | 当前价格（原始文本） | ❌ |
| 3 | 涨幅 | `change_pct` | String | 涨跌幅百分比 | ✅ 颜色 |
| 4 | 成交(万元) | `volume` | String | 成交额（万元） | ❌ |
| 5 | 场内份额(万份) | `shares` | String | 场内流通份额 | ❌ |
| 6 | 场内新增(万份) | `shares_change` | String | 场内份额变化 | ❌ |
| 7 | 换手率 | `turnover_rate` | String | 交易活跃度 | ❌ |
| 8 | 基金净值 | `nav` | String | 基金单位净值 | ❌ |
| 9 | 净值日期 | `nav_date` | String | 净值更新时间 | ❌ |
| 10 | 实时估值 | `rt_valuation` | String | 盘中估算净值 | ❌ |
| 11 | 溢价率 | `premium_rate` | String | 溢价率（**已倒序排序**） | ✅ 颜色 |
| 12 | 跟踪指数 | `tracking_index` | String | 目标指数名称 | ❌ |
| 13 | 指数涨幅 | `index_change_pct` | String | 对应指数涨跌幅 | ✅ 颜色 |
| 14 | 申购费 | `apply_fee` | String | 申购费率 | ❌ |
| 15 | 申购状态 | `apply_status` | String | 申购状态 | ✅ 颜色 |
| 16 | 赎回费 | `redeem_fee` | String | 赎回费率 | ❌ |
| 17 | 赎回状态 | `redeem_status` | String | 赎回状态 | ❌ |
| 18 | 基金公司 | `fund_company` | String | 管理公司 | ❌ |
| 19 | 备注 | `remark` | String | 相关提示 | ❌ |
| 20 | 操作 | - | - | 网页操作按钮（不抓取） | ❌ |

**说明**: 
- **共 21 列，全部抓取**（除操作列）
- 数据已按溢价率从高到低排序
- 包含完整的净值、费率、流动性等信息

**样式字段说明**:
- `change_pct_color`: 涨跌幅文字颜色
- `premium_rate_color`: 溢价率文字颜色
- `index_change_pct_color`: 指数涨幅文字颜色
- `apply_status_color`: 申购状态文字颜色

**API 接口**: `GET /api/lof/index`

---

## 3. LOF 套利数据 (表格 ID: `#flex_lof`)

**数据源**: https://www.jisilu.cn/data/lof/#arbitrage

该数据源抓取逻辑较复杂，包含多个字段的解析和转换。详细映射关系可参考 `app/scraper.py` 中的 `scrape_lof_data()` 方法。

**API 接口**: 
- `GET /api/lof/list` - 带溢价率筛选
- `GET /api/lof/all` - 全部数据

---

## 颜色样式规则

所有颜色值均为 HEX 格式（如 `#ff0000`），常见颜色含义：

| 颜色 | HEX 值 | 含义 |
|------|--------|------|
| 红色 | `#ff0000` | 上涨/正溢价 |
| 绿色 | `#008000` | 下跌/折价 |
| 黑色/深灰 | `#3d3d3d` | 中性/零 |
| 浅灰 | `#999999` | 暂停/限制状态 |

---

## 数据更新频率

所有数据源通过定时任务自动抓取，默认每天执行一次（可在 `app/scheduler.py` 中配置）。

抓取顺序：
1. LOF 套利数据
2. QDII 商品数据
3. 指数 LOF 数据

每次抓取会清空对应表中的旧数据，然后插入最新数据。
