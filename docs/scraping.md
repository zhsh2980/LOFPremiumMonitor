# 集思录数据抓取技术文档

> 版本：1.0  
> 更新时间：2026-02-01  
> 分析工具：Playwright + Chrome

## 1. 目标页面

| 项目 | 值 |
|------|-----|
| 页面名称 | LOF 套利 |
| URL | https://www.jisilu.cn/data/lof/#arb |
| 登录页面 | https://www.jisilu.cn/account/login/ |
| 数据加载方式 | AJAX 异步加载（Flexigrid） |

## 2. 登录流程

### 2.1 登录页面元素

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 用户名输入框 | `input[name="user_name"]` | 手机号/邮箱 |
| 密码输入框 | `input[name="password"]` | 密码 |
| 同意协议 | `input[type="checkbox"]` | 需要勾选 |
| 登录按钮 | `button[type="submit"]` 或 `.login-btn` | 提交登录 |

### 2.2 登录步骤

1. 访问 `https://www.jisilu.cn/account/login/`
2. 填入用户名（手机号）
3. 填入密码
4. 勾选"同意用户协议"
5. 点击登录按钮
6. 等待页面跳转（成功后跳转到首页）
7. 验证登录状态（检查用户名显示）

### 2.3 注意事项

- 需要**会员账号**才能看到完整的套利数据
- 登录成功后 Cookie 有效，后续请求自动携带
- 暂未发现验证码（2026-02-01 测试时）

## 3. 数据表格结构

### 3.1 表格基本信息

| 项目 | 值 |
|------|-----|
| 表格 ID | `flex_arb`（注意：不同标签页使用不同表格ID） |
| 表格框架 | Flexigrid（jQuery 插件） |
| 数据行数 | 约 300+ 行（全部模式） |
| 分页 | 无分页，一次性加载全部 |

> **重要**：不同标签页的表格 ID 不同：
> - 股票 LOF → `flex_stock`
> - 指数 LOF → `flex_index`  
> - **LOF 套利** → `flex_arb`（我们使用这个）

### 3.2 申购状态筛选按钮

| ID | 文本 | 功能 |
|----|------|------|
| `apply_lmt` | 限额 | 只显示有申购限额的基金 |
| `apply_stp` | 暂停 | 只显示暂停申购的基金 |
| `apply_opn` | 开放 | 只显示开放申购的基金 |
| `apply_all` | 全部 | 显示所有基金 |

**触发方式**：点击按钮后调用 `tableArbLOF.reload()` 刷新表格

### 3.3 表格列定义

| 列索引 | 字段名 | 数据示例 | 说明 |
|--------|--------|----------|------|
| 0 | 代码 | `161725` | 基金代码（6位） |
| 1 | 名称 | `招商中证白酒A` | 含 `<sup>T+0</sup>` 等标签 |
| 2 | 现价 | `1.234` | 场内最新价格 |
| 3 | 涨幅 | `2.35%` | 今日涨跌幅 |
| 4 | 成交(万元) | `12345` | 成交金额 |
| 5 | **溢价率** | `5.23%` | **核心指标** |
| 6 | 估值 | `1.180` | 实时估值 |
| 7 | 基金净值 | `1.173` | 最新公布净值 |
| 8 | 净值日期 | `02-01` | 净值更新日期 |
| 9 | 场内份额(万份) | `50000` | 场内流通份额 |
| 10 | 场内新增(万份) | `1000` | 今日新增份额 |
| 11 | 申购费 | `1.50%` | 申购费率 |
| 12 | **申购状态** | `限100` | 申购限额/状态 |
| 13 | 赎回费 | `0.50%` | 赎回费率 |
| 14 | 赎回状态 | `开放` | 赎回状态 |
| 15 | 基金公司 | `招商基金` | 管理公司 |
| 16 | 操作 | - | 操作按钮，可忽略 |

### 3.4 特殊字段处理

#### 名称字段（列1）

名称中可能包含特殊标签，以 `<sup>` 标签形式存在：

```html
<a href="/data/lof/detail/162719">广发资源优选A<sup>T+0</sup><sup>QD</sup></a>
```

- `T+0`：支持 T+0 交易
- `QD`：QDII 基金

**解析建议**：提取纯文本名称 + 单独提取标签

#### 溢价率字段（列5）

```
34.38%  →  34.38（浮点数）
-1.23%  →  -1.23（浮点数）
```

**解析建议**：去除 `%` 符号，转为浮点数

#### 申购状态字段（列12）

| 原始值 | 解析后 |
|--------|--------|
| `限10` | status=`limited`, limit=`10` |
| `限100` | status=`limited`, limit=`100` |
| `限1万` | status=`limited`, limit=`10000` |
| `暂停申购` | status=`suspended`, limit=`null` |
| `开放申购` | status=`open`, limit=`null` |

**解析建议**：使用正则表达式 `限(\d+(?:万)?)`

## 4. 数据抓取策略

### 4.1 推荐方案

使用 **Playwright** 模拟浏览器访问：

```python
# 伪代码
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    
    # 登录
    await page.goto("https://www.jisilu.cn/account/login/")
    await page.fill('input[name="user_name"]', username)
    await page.fill('input[name="password"]', password)
    await page.click('checkbox')
    await page.click('button[type="submit"]')
    
    # 访问数据页
    await page.goto("https://www.jisilu.cn/data/lof/#arb")
    await page.wait_for_selector("#flex_index tbody tr")
    
    # 提取数据
    rows = await page.query_selector_all("#flex_index tbody tr")
    for row in rows:
        cells = await row.query_selector_all("td")
        # 提取各列数据...
```

### 4.2 数据选择器

| 用途 | CSS 选择器 |
|------|------------|
| 数据表格 | `#flex_index` |
| 所有数据行 | `#flex_index tbody tr` |
| 某行的所有单元格 | `tr td` |
| 切换到"全部" | `#apply_all` |
| 切换到"限额" | `#apply_lmt` |

### 4.3 等待策略

页面使用 AJAX 加载数据，需要等待：

```python
# 等待表格数据加载完成
await page.wait_for_selector("#flex_index tbody tr", timeout=30000)

# 或等待行数大于某个值
await page.wait_for_function("document.querySelectorAll('#flex_index tbody tr').length > 10")
```

## 5. 风险与应对

| 风险 | 应对措施 |
|------|----------|
| 登录失败 | 检查账号密码，记录错误日志 |
| 页面结构变化 | 抓取失败时发送告警，人工检查 |
| 访问频率限制 | 随机间隔抓取（50-70分钟） |
| Cookie 过期 | 每次抓取重新登录 |
| 验证码出现 | 目前未遇到，后续如遇到需人工处理 |

## 6. 测试记录

| 日期 | 测试内容 | 结果 |
|------|----------|------|
| 2026-02-01 | 登录测试 | ✅ 成功 |
| 2026-02-01 | 页面结构分析 | ✅ 完成 |
| 2026-02-01 | 数据抓取测试 | 待测试 |

## 7. 页面截图

抓取分析过程中的页面截图：

![LOF 套利表格](../.gemini/antigravity/brain/451134dd-1215-491f-8d9c-287a1f172136/lof_table_view_1769939682372.png)

> 注：截图路径为本地分析时保存，部署时可删除此节
