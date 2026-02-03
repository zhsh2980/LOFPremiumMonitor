# 数据源访问指南

本文档说明如何访问和定位三个数据源页面，以及各自的抓取要点。

## 1. LOF 套利数据

### 访问方式
- **URL**: https://www.jisilu.cn/data/lof/#arb
- **表格 ID**: `#flex_arb`
- **需要登录**: 是

### 页面特点
- 页面加载后直接显示表格
- 有"全部"/"开放"等筛选按钮，需点击"全部"获取完整数据
- 表格使用 flexigrid 组件

### 抓取步骤
1. 访问 URL
2. 等待 `#flex_arb tbody tr` 加载
3. 点击 `#apply_all` 按钮（全部）
4. 等待 2 秒让数据刷新
5. 提取表格数据

### 表头信息（共 16 列）
| 索引 | 表头 | 字段名 | 说明 |
|------|------|--------|------|
| 0 | 代码 | fund_code | 基金代码 |
| 1 | 名称 | fund_name | 基金名称（包含标签） |
| 2 | 现价 | price | 当前价格 |
| 3 | 涨幅 | change_pct | 涨跌幅 |
| 4 | 成交(万元) | amount | 成交额 |
| 5 | 溢价率 | premium_rate | 溢价率 |
| 6 | 估值 | estimate_nav | 估算净值 |
| 7 | 净值 | nav | 基金净值 |
| 8 | 更新时间 | nav_date | 净值日期 |
| 9 | 份额(万份) | shares | 场内份额 |
| 10 | 新增(万份) | shares_change | 份额变化 |
| 11 | 申购费 | apply_fee | 申购费率 |
| 12 | 申购状态 | apply_status | 申购状态（含限额） |
| 13 | 赎回费 | redeem_fee | 赎回费率 |
| 14 | 赎回状态 | redeem_status | 赎回状态 |
| 15 | 基金公司 | fund_company | 管理公司 |

**状态**: ✅ 已全量抓取（16/16 列）

---

## 2. 指数 LOF 数据

### 访问方式
- **URL**: https://www.jisilu.cn/data/lof/#index
- **表格 ID**: `#flex_index`
- **需要登录**: 是

### 页面特点
- 页面加载后直接显示表格
- 需要点击"溢价率"表头两次进行倒序排序

### 抓取步骤
1. 访问 URL
2. 等待 `#flex_index tbody tr` 加载
3. 找到表头"溢价率"（`th` 包含文本"溢价率"）
4. 点击该表头
5. 等待 1 秒
6. 再次点击该表头（实现倒序）
7. 等待 1 秒
8. 提取表格数据

### 表头信息（共 21 列）
| 索引 | 表头 | 字段名 | 说明 |
|------|------|--------|------|
| 0 | 代码 | fund_code | 基金代码 |
| 1 | 名称 | fund_name | 基金名称 |
| 2 | 现价 | price | 当前价格 |
| 3 | 涨幅 | change_pct | 涨跌幅 |
| 4 | 成交(万元) | volume | 成交额 |
| 5 | 场内份额(万份) | shares | 场内份额 |
| 6 | 场内新增(万份) | shares_change | 份额变化 |
| 7 | 换手率 | turnover_rate | 换手率 |
| 8 | 基金净值 | nav | 净值 |
| 9 | 净值日期 | nav_date | 净值日期 |
| 10 | 实时估值 | rt_valuation | 实时估值 |
| 11 | 溢价率 | premium_rate | 溢价率（倒序） |
| 12 | 跟踪指数 | tracking_index | 跟踪指数 |
| 13 | 指数涨幅 | index_change_pct | 指数涨幅 |
| 14 | 申购费 | apply_fee | 申购费率 |
| 15 | 申购状态 | apply_status | 申购状态 |
| 16 | 赎回费 | redeem_fee | 赎回费率 |
| 17 | 赎回状态 | redeem_status | 赎回状态 |
| 18 | 基金公司 | fund_company | 基金公司 |
| 19 | 备注 | remark | 备注 |
| 20 | 操作 | - | 操作按钮（不抓取） |

**状态**: ✅ 已全量抓取（20/21 列，操作列除外）

---

## 3. QDII 商品数据

### 访问方式
- **URL**: https://www.jisilu.cn/data/qdii/#qdiie
- **表格 ID**: `#flex_qdiic`
- **需要登录**: 是

### 页面特点 ⚠️
- **关键**: 商品表格在页面最底部，需要向下滚动才能看到
- 页面默认显示"欧美市场"标签内容
- 商品相关的表格不是通过标签切换，而是直接在页面底部

### 抓取步骤
1. 访问 URL（带 hash `#qdiie` 或 `#qdiic`）
2. **向下滚动页面到底部**（重要！）
   - 方法: `page.evaluate("window.scrollTo(0, document.body.scrollHeight)")`
3. 等待 `#flex_qdiic tbody tr` 加载
4. 提取表格数据

### 表头信息（共 14 列）
| 索引 | 表头 | 字段名 | 说明 |
|------|------|--------|------|
| 0 | 代码 | fund_code | 基金代码 |
| 1 | 名称 | fund_name | 基金名称 |
| 2 | 现价 | price | 当前价格 |
| 3 | 涨幅 | change_pct | 涨跌幅 |
| 4 | 成交(万元) | volume | 成交额 |
| 5 | 场内份额 | shares | 场内份额 |
| 6 | 份额新增 | shares_change | 份额变化 |
| 7 | T-2净值 | nav_t2 | T-2净值 |
| 8 | T-1估值 | valuation_t1 | T-1估值 |
| 9 | T-1溢价率 | premium_rate_t1 | T-1溢价率 |
| 10 | 实时估值 | rt_valuation | 实时估值 |
| 11 | 实时溢价率 | rt_premium_rate | 实时溢价率 |
| 12 | 申购状态 | apply_status | 申购状态 |
| 13 | 相关标的 | benchmark | 相关指数 |

**状态**: ✅ 已全量抓取（14/14 列）

---

## 常见问题

### Q: 为什么有时找不到表格？
A: 
1. **LOF 套利/指数**: 确保 URL 包含正确的 hash（#arb 或 #index）
2. **QDII 商品**: 必须滚动到页面底部，否则表格可能不在视口内

### Q: 如何确认表格已加载？
A: 使用 `page.wait_for_selector("#表格ID tbody tr", timeout=30000)`

### Q: 抓取失败怎么办？
A: 
1. 检查是否已登录
2. 检查 URL 是否正确
3. 检查是否需要点击按钮或滚动页面
4. 查看浏览器控制台错误日志

---

## 数据更新频率

所有数据源的更新频率：
- **集思录数据更新**: 交易日实时更新
- **本地抓取频率**: 默认每天一次（可配置）
- **抓取顺序**: LOF 套利 → QDII 商品 → 指数 LOF

---

## 技术细节

### 登录状态
- 使用 Playwright 的 `storageState` 保存登录状态
- 登录状态文件: `/tmp/jisilu_auth_state.json`
- 有效期: 通常数天到数周

### 表格组件
- 所有表格都使用 flexigrid jQuery 插件
- 数据通过 AJAX 动态加载
- 需要等待 DOM 元素出现后再提取

### 样式提取
- 使用 `window.getComputedStyle()` 获取单元格颜色
- RGB 颜色转换为 HEX 格式
- 主要提取文字颜色和背景色
