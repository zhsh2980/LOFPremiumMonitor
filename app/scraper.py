"""
集思录数据抓取模块
使用 Playwright 模拟浏览器访问
支持登录状态持久化，减少重复登录
"""

import os
import re
import time
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from loguru import logger

from app.config import get_settings
from app.database import SessionLocal
from app.models import LOFData, ScrapeLog, QDIIData, LOFIndexData

# 登录状态保存路径
AUTH_STATE_FILE = Path("/tmp/jisilu_auth_state.json")


class JisiluScraper:
    """集思录数据抓取器"""
    
    LOGIN_URL = "https://www.jisilu.cn/account/login/"
    LOF_ARB_URL = "https://www.jisilu.cn/data/lof/#arb"
    
    def __init__(self):
        self.settings = get_settings()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def _parse_number(self, text: str) -> Optional[float]:
        """解析数字，处理百分号、万等单位"""
        if not text or text == "-" or text == "--":
            return None
        
        text = text.strip()
        
        # 移除百分号
        if text.endswith("%"):
            text = text[:-1]
        
        # 处理万单位
        multiplier = 1
        if text.endswith("万"):
            text = text[:-1]
            multiplier = 10000
        
        try:
            return float(text) * multiplier
        except ValueError:
            return None
    
    def _parse_date(self, text: str) -> Optional[date]:
        """解析日期，格式如 02-01 或 2026-02-01"""
        if not text or text == "-":
            return None
        
        text = text.strip()
        today = date.today()
        
        try:
            if len(text) == 5:  # MM-DD 格式
                month, day = text.split("-")
                return date(today.year, int(month), int(day))
            elif len(text) == 10:  # YYYY-MM-DD 格式
                return datetime.strptime(text, "%Y-%m-%d").date()
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _parse_apply_status(self, text: str) -> tuple[str, Optional[str]]:
        """
        解析申购状态
        返回: (status, limit_text)
        """
        if not text:
            return "unknown", None
        
        text = text.strip()
        
        if "暂停" in text:
            return "suspended", None
        elif "开放" in text:
            return "open", None
        elif text.startswith("限"):
            # 解析限额，如 "限100"、"限1万"
            return "limited", text
        else:
            return "unknown", text
    
    def _extract_tags(self, name_html: str) -> tuple[str, List[str]]:
        """
        从名称 HTML 中提取标签
        返回: (纯名称, 标签列表)
        """
        # 提取 <sup> 标签内容
        tags = re.findall(r'<sup[^>]*>([^<]+)</sup>', name_html)
        
        # 移除 HTML 标签，获取纯文本名称
        name = re.sub(r'<[^>]+>', '', name_html).strip()
        
        return name, tags
    
    def _extract_cell_style(self, cell) -> dict:
        """
        提取单元格的文字颜色和背景色
        返回: {"color": "#rrggbb", "backgroundColor": "#rrggbb"}
        颜色格式为 HEX（如 #ff0000）
        """
        try:
            style = cell.evaluate("""
                (el) => {
                    const computed = window.getComputedStyle(el);
                    
                    // 将 rgb/rgba 转换为 HEX 格式
                    function rgbToHex(rgbStr) {
                        if (!rgbStr || rgbStr === 'rgba(0, 0, 0, 0)') return null;
                        
                        const match = rgbStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
                        if (!match) return null;
                        
                        const r = parseInt(match[1]);
                        const g = parseInt(match[2]);
                        const b = parseInt(match[3]);
                        
                        return '#' + [r, g, b].map(x => {
                            const hex = x.toString(16);
                            return hex.length === 1 ? '0' + hex : hex;
                        }).join('');
                    }
                    
                    return {
                        color: rgbToHex(computed.color),
                        backgroundColor: rgbToHex(computed.backgroundColor)
                    };
                }
            """)
            return style
        except Exception as e:
            logger.warning(f"提取样式失败: {e}")
            return {"color": None, "backgroundColor": None}
    
    def _has_saved_auth_state(self) -> bool:
        """检查是否有保存的登录状态"""
        return AUTH_STATE_FILE.exists()
    
    def _load_auth_state(self, browser: Browser) -> BrowserContext:
        """加载已保存的登录状态创建浏览器上下文"""
        logger.info("加载已保存的登录状态...")
        return browser.new_context(storage_state=str(AUTH_STATE_FILE))
    
    def _save_auth_state(self, context: BrowserContext):
        """保存当前登录状态"""
        logger.info(f"保存登录状态到 {AUTH_STATE_FILE}")
        context.storage_state(path=str(AUTH_STATE_FILE))
    
    def _is_logged_in(self, page: Page) -> bool:
        """检查当前页面是否已登录"""
        try:
            # 访问需要登录才能看到完整数据的页面
            page.goto(self.LOF_ARB_URL, wait_until="networkidle", timeout=30000)
            
            # 检查是否有登录提示或者被重定向到登录页
            if "login" in page.url:
                logger.info("登录状态已失效，需要重新登录")
                return False
            
            # 检查页面是否有用户信息（已登录的标志）
            # 等待表格加载，如果能看到数据说明已登录
            try:
                page.wait_for_selector("#flex_arb tbody tr", timeout=10000)
                logger.info("登录状态有效，已成功加载数据页面")
                return True
            except:
                logger.info("无法加载数据，可能未登录或登录已过期")
                return False
                
        except Exception as e:
            logger.warning(f"检查登录状态时出错: {e}")
            return False
    
    def login(self, page: Page) -> bool:
        """登录集思录"""
        logger.info("正在登录集思录...")
        
        try:
            page.goto(self.LOGIN_URL, wait_until="networkidle", timeout=30000)
            
            # 填写用户名
            page.fill('input[name="user_name"]', self.settings.jisilu_username)
            
            # 填写密码
            page.fill('input[name="password"]', self.settings.jisilu_password)
            
            # 勾选"记住我"（如果有的话）
            remember_me = page.query_selector('input[name="auto_login"], input#auto_login, .remember-me input')
            if remember_me and not remember_me.is_checked():
                remember_me.click()
                logger.info("已勾选'记住我'")
            
            # 勾选同意协议（使用可见的复选框）
            checkbox = page.query_selector('.user_agree input[type="checkbox"]')
            if checkbox and not checkbox.is_checked():
                checkbox.click()
            
            # 点击登录按钮（是一个链接，不是 button）
            page.click('a.btn-jisilu[href*="login"]')
            
            # 等待页面跳转或登录完成
            page.wait_for_timeout(3000)
            
            # 验证登录成功：检查是否离开登录页面或者页面上有用户信息
            if "login" not in page.url:
                logger.info(f"登录成功，当前页面: {page.url}")
                return True
            else:
                # 可能登录后没有跳转，检查页面是否有登录成功的标志
                user_info = page.query_selector('.user-name, .nav-user')
                if user_info:
                    logger.info("登录成功（通过用户信息确认）")
                    return True
                logger.error("登录失败，仍在登录页面")
                return False
                
        except Exception as e:
            logger.error(f"登录异常: {e}")
            return False
    
    def scrape_lof_data(self, page: Page) -> List[Dict]:
        """抓取 LOF 套利数据"""
        logger.info("正在抓取 LOF 套利数据...")
        
        try:
            # 如果当前不在 LOF 套利页面，则跳转
            if "#arb" not in page.url:
                page.goto(self.LOF_ARB_URL, wait_until="networkidle", timeout=30000)
            
            # 等待表格加载（LOF套利页面使用 flex_arb 表格）
            page.wait_for_selector("#flex_arb tbody tr", timeout=30000)
            
            # 点击"全部"按钮，确保获取所有数据
            all_btn = page.query_selector("#apply_all")
            if all_btn:
                all_btn.click()
                time.sleep(2)  # 等待数据刷新
            
            # 提取表格数据
            rows = page.query_selector_all("#flex_arb tbody tr")
            logger.info(f"找到 {len(rows)} 行数据")
            
            data_list = []
            for row in rows:
                try:
                    cells = row.query_selector_all("td")
                    if len(cells) < 16:
                        continue
                    
                    # 获取各列数据
                    fund_code = cells[0].inner_text().strip()
                    name_html = cells[1].inner_html()
                    fund_name, fund_tags = self._extract_tags(name_html)
                    
                    price = self._parse_number(cells[2].inner_text())
                    change_pct = self._parse_number(cells[3].inner_text())
                    amount = self._parse_number(cells[4].inner_text())
                    premium_rate = self._parse_number(cells[5].inner_text())
                    estimate_nav = self._parse_number(cells[6].inner_text())
                    nav = self._parse_number(cells[7].inner_text())
                    nav_date = self._parse_date(cells[8].inner_text())
                    shares = self._parse_number(cells[9].inner_text())
                    shares_change = self._parse_number(cells[10].inner_text())
                    apply_fee = cells[11].inner_text().strip()
                    apply_status_text = cells[12].inner_text().strip()
                    apply_status, apply_limit = self._parse_apply_status(apply_status_text)
                    redeem_fee = cells[13].inner_text().strip()
                    redeem_status = cells[14].inner_text().strip()
                    fund_company = cells[15].inner_text().strip()
                    
                    # 提取样式信息
                    change_pct_style = self._extract_cell_style(cells[3])
                    premium_rate_style = self._extract_cell_style(cells[5])
                    apply_status_style = self._extract_cell_style(cells[12])
                    
                    # 跳过无效数据
                    if not fund_code or premium_rate is None:
                        continue
                    
                    data_list.append({
                        "fund_code": fund_code,
                        "fund_name": fund_name,
                        "fund_tags": ",".join(fund_tags) if fund_tags else None,
                        "price": price,
                        "change_pct": change_pct,
                        "amount": amount,
                        "premium_rate": premium_rate,
                        "estimate_nav": estimate_nav,
                        "nav": nav,
                        "nav_date": nav_date,
                        "shares": shares,
                        "shares_change": shares_change,
                        "apply_fee": apply_fee if apply_fee and apply_fee != "-" else None,
                        "apply_status": apply_status,
                        "apply_limit": apply_limit,
                        "redeem_fee": redeem_fee if redeem_fee and redeem_fee != "-" else None,
                        "redeem_status": redeem_status if redeem_status and redeem_status != "-" else None,
                        "fund_company": fund_company if fund_company else None,
                        # 样式信息
                        "change_pct_color": change_pct_style.get("color"),
                        "premium_rate_color": premium_rate_style.get("color"),
                        "apply_status_color": apply_status_style.get("color"),
                        "apply_status_bg_color": apply_status_style.get("backgroundColor"),
                    })
                    
                except Exception as e:
                    logger.warning(f"解析行数据失败: {e}")
                    continue
            
            logger.info(f"成功解析 {len(data_list)} 条数据")
            return data_list
            
        except Exception as e:
            logger.error(f"抓取数据异常: {e}")
            raise
    

    def scrape_qdii_data(self, page: Page) -> List[Dict]:
        """抓取 QDII 商品数据 (保持原始格式)"""
        logger.info("正在抓取 QDII 商品数据...")
        
        try:
            # 跳转到 QDII 页面
            qdii_url = "https://www.jisilu.cn/data/qdii/#qdiie"
            if page.url != qdii_url:
                page.goto(qdii_url, wait_until="networkidle", timeout=30000)
            
            # ⚠️ 关键步骤：滚动到页面底部
            # 商品表格在页面最底部，需要滚动才能看到
            logger.info("滚动到页面底部以加载商品表格...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)  # 等待滚动和表格加载
            
            # 等待商品表格加载
            page.wait_for_selector("#flex_qdiic tbody tr", timeout=30000)
            
            # 提取数据
            rows = page.query_selector_all("#flex_qdiic tbody tr")
            logger.info(f"找到 {len(rows)} 行 QDII 商品数据")
            
            data_list = []
            for row in rows:
                try:
                    cells = row.query_selector_all("td")
                    if len(cells) < 14:
                        continue
                        
                    # 提取原始文本 (innerText)
                    fund_code = cells[0].inner_text().strip()
                    fund_name = cells[1].inner_text().strip()
                    price = cells[2].inner_text().strip()
                    change_pct = cells[3].inner_text().strip()
                    volume = cells[4].inner_text().strip()
                    shares = cells[5].inner_text().strip()
                    shares_change = cells[6].inner_text().strip()
                    nav_t2 = cells[7].inner_text().strip()
                    valuation_t1 = cells[8].inner_text().strip()
                    premium_rate_t1 = cells[9].inner_text().strip()
                    rt_valuation = cells[10].inner_text().strip()
                    rt_premium_rate = cells[11].inner_text().strip()
                    apply_status = cells[12].inner_text().strip()
                    benchmark = cells[13].inner_text().strip()
                    
                    # 提取样式
                    change_pct_style = self._extract_cell_style(cells[3])
                    premium_rate_t1_style = self._extract_cell_style(cells[9])
                    rt_premium_rate_style = self._extract_cell_style(cells[11])
                    apply_status_style = self._extract_cell_style(cells[12])
                    
                    data_list.append({
                        "fund_code": fund_code,
                        "fund_name": fund_name,
                        "price": price,
                        "change_pct": change_pct,
                        "volume": volume,
                        "shares": shares,
                        "shares_change": shares_change,
                        "nav_t2": nav_t2,
                        "valuation_t1": valuation_t1,
                        "premium_rate_t1": premium_rate_t1,
                        "rt_valuation": rt_valuation,
                        "rt_premium_rate": rt_premium_rate,
                        "apply_status": apply_status,
                        "benchmark": benchmark,
                        # 样式字段
                        "change_pct_color": change_pct_style.get("color"),
                        "premium_rate_t1_color": premium_rate_t1_style.get("color"),
                        "rt_premium_rate_color": rt_premium_rate_style.get("color"),
                        "apply_status_color": apply_status_style.get("color")
                    })
                    
                except Exception as e:
                    logger.warning(f"解析 QDII 行数据失败: {e}")
                    continue
            
            return data_list

        except Exception as e:
            logger.error(f"抓取 QDII 数据异常: {e}")
            return []

    def save_lof_to_database(self, data_list: List[Dict]) -> int:
        """保存 LOF 数据到数据库"""
        logger.info(f"正在保存 LOF 数据: {len(data_list)} 条")
        
        db = SessionLocal()
        try:
            # 清空旧数据
            db.query(LOFData).delete()
            
            # 批量插入新数据
            for data in data_list:
                lof = LOFData(**data)
                db.add(lof)
            
            db.commit()
            logger.info(f"成功保存 LOF {len(data_list)} 条数据")
            return len(data_list)
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存 LOF 数据失败: {e}")
            raise
        finally:
            db.close()
    
    def save_qdii_to_database(self, data_list: List[Dict]) -> int:
        """保存 QDII 数据到数据库"""
        logger.info(f"正在保存 QDII 数据: {len(data_list)} 条")
        
        db = SessionLocal()
        try:
            # 清空旧数据
            db.query(QDIIData).delete()
            
            # 批量插入新数据
            for data in data_list:
                qdii = QDIIData(**data)
                db.add(qdii)
            
            db.commit()
            logger.info(f"成功保存 QDII {len(data_list)} 条数据")
            return len(data_list)
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存 QDII 数据失败: {e}")
            raise
        finally:
            db.close()
    
    def scrape_lof_index_data(self, page: Page) -> List[Dict]:
        """抓取 LOF 指数基金数据 (保持原始格式，按溢价率倒序，全字段)"""
        logger.info("正在抓取 LOF 指数基金数据...")
        
        try:
            # 跳转到指数 LOF 页面
            index_url = "https://www.jisilu.cn/data/lof/#index"
            if page.url != index_url:
                page.goto(index_url, wait_until="networkidle", timeout=30000)
            
            # 等待表格加载
            page.wait_for_selector("#flex_index tbody tr", timeout=30000)
            
            # 找到"溢价率"表头并点击两次进行倒序排序
            logger.info("点击溢价率表头进行排序...")
            premium_header = page.locator("th").filter(has_text="溢价率").first
            premium_header.click()
            page.wait_for_timeout(1000)  # 等待排序完成
            premium_header.click()  # 第二次点击，确保倒序
            page.wait_for_timeout(1000)  # 等待排序完成
            
            # 提取数据
            rows = page.query_selector_all("#flex_index tbody tr")
            logger.info(f"找到 {len(rows)} 行指数 LOF 数据")
            
            data_list = []
            for row in rows:
                try:
                    cells = row.query_selector_all("td")
                    if len(cells) < 20:  # 最少需要20列（索引0-19，索引20是操作列可忽略）
                        continue
                        
                    # 提取所有字段的原始文本 (共21列，索引0-20)
                    fund_code = cells[0].inner_text().strip()
                    fund_name = cells[1].inner_text().strip()
                    price = cells[2].inner_text().strip()
                    change_pct = cells[3].inner_text().strip()
                    volume = cells[4].inner_text().strip()
                    shares = cells[5].inner_text().strip()
                    shares_change = cells[6].inner_text().strip()
                    turnover_rate = cells[7].inner_text().strip()
                    nav = cells[8].inner_text().strip()
                    nav_date = cells[9].inner_text().strip()
                    rt_valuation = cells[10].inner_text().strip()
                    premium_rate = cells[11].inner_text().strip()
                    tracking_index = cells[12].inner_text().strip()
                    index_change_pct = cells[13].inner_text().strip()
                    apply_fee = cells[14].inner_text().strip()
                    apply_status = cells[15].inner_text().strip()
                    redeem_fee = cells[16].inner_text().strip()
                    redeem_status = cells[17].inner_text().strip()
                    fund_company = cells[18].inner_text().strip()
                    remark = cells[19].inner_text().strip()
                    
                    # 提取样式（保持原有的4个样式字段）
                    change_pct_style = self._extract_cell_style(cells[3])
                    premium_rate_style = self._extract_cell_style(cells[11])
                    index_change_pct_style = self._extract_cell_style(cells[13])
                    apply_status_style = self._extract_cell_style(cells[15])
                    
                    data_list.append({
                        "fund_code": fund_code,
                        "fund_name": fund_name,
                        "price": price,
                        "change_pct": change_pct,
                        "volume": volume,
                        "shares": shares,
                        "shares_change": shares_change,
                        "turnover_rate": turnover_rate,
                        "nav": nav,
                        "nav_date": nav_date,
                        "rt_valuation": rt_valuation,
                        "premium_rate": premium_rate,
                        "tracking_index": tracking_index,
                        "index_change_pct": index_change_pct,
                        "apply_fee": apply_fee,
                        "apply_status": apply_status,
                        "redeem_fee": redeem_fee,
                        "redeem_status": redeem_status,
                        "fund_company": fund_company,
                        "remark": remark,
                        # 样式字段
                        "change_pct_color": change_pct_style.get("color"),
                        "premium_rate_color": premium_rate_style.get("color"),
                        "index_change_pct_color": index_change_pct_style.get("color"),
                        "apply_status_color": apply_status_style.get("color")
                    })
                    
                except Exception as e:
                    logger.warning(f"解析指数 LOF 行数据失败: {e}")
                    continue
            
            logger.info(f"成功解析 {len(data_list)} 条指数 LOF 数据")
            return data_list

        except Exception as e:
            logger.error(f"抓取指数 LOF 数据异常: {e}")
            return []
    
    def save_lof_index_to_database(self, data_list: List[Dict]) -> int:
        """保存指数 LOF 数据到数据库"""
        logger.info(f"正在保存指数 LOF 数据: {len(data_list)} 条")
        
        db = SessionLocal()
        try:
            # 清空旧数据
            db.query(LOFIndexData).delete()
            
            # 批量插入新数据
            for data in data_list:
                lof_index = LOFIndexData(**data)
                db.add(lof_index)
            
            db.commit()
            logger.info(f"成功保存指数 LOF {len(data_list)} 条数据")
            return len(data_list)
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存指数 LOF 数据失败: {e}")
            raise
        finally:
            db.close()
    
    def log_scrape_result(self, status: str, record_count: int = 0, 
                          error_message: str = None, duration: float = None):
        """记录抓取日志"""
        db = SessionLocal()
        try:
            log = ScrapeLog(
                scrape_time=datetime.now(),
                status=status,
                record_count=record_count,
                error_message=error_message,
                duration_seconds=Decimal(str(round(duration, 2))) if duration else None
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"记录日志失败: {e}")
            db.rollback()
        finally:
            db.close()
    
    def run(self) -> bool:
        """执行抓取任务"""
        logger.info("=" * 50)
        logger.info("开始执行抓取任务")
        
        start_time = time.time()
        
        try:
            with sync_playwright() as p:
                # 启动浏览器
                self.browser = p.chromium.launch(headless=True)
                
                # 尝试使用已保存的登录状态
                need_login = True
                if self._has_saved_auth_state():
                    try:
                        self.context = self._load_auth_state(self.browser)
                        self.page = self.context.new_page()
                        
                        # 验证登录状态是否有效
                        if self._is_logged_in(self.page):
                            need_login = False
                            logger.info("使用已保存的登录状态，跳过登录步骤")
                        else:
                            # 登录状态失效，关闭当前上下文
                            self.context.close()
                    except Exception as e:
                        logger.warning(f"加载登录状态失败: {e}")
                
                # 需要重新登录
                if need_login:
                    logger.info("需要重新登录...")
                    self.context = self.browser.new_context()
                    self.page = self.context.new_page()
                    
                    if not self.login(self.page):
                        raise Exception("登录失败")
                    
                    # 保存登录状态供下次使用
                    self._save_auth_state(self.context)
                
                # 1. 抓取并保存 LOF 数据
                logger.info("=" * 30 + " LOF 数据 " + "=" * 30)
                lof_data = self.scrape_lof_data(self.page)
                
                if lof_data:
                    lof_count = self.save_lof_to_database(lof_data)
                    logger.info(f"LOF 数据抓取完成: {lof_count} 条")
                else:
                    logger.warning("未获取到 LOF 数据")
                    lof_count = 0
                
                # 2. 抓取并保存 QDII 数据
                logger.info("=" * 30 + " QDII 数据 " + "=" * 30)
                qdii_data = self.scrape_qdii_data(self.page)
                
                if qdii_data:
                    qdii_count = self.save_qdii_to_database(qdii_data)
                    logger.info(f"QDII 数据抓取完成: {qdii_count} 条")
                else:
                    logger.warning("未获取到 QDII 数据")
                    qdii_count = 0
                
                # 3. 抓取并保存指数 LOF 数据
                logger.info("=" * 30 + " 指数 LOF 数据 " + "=" * 30)
                lof_index_data = self.scrape_lof_index_data(self.page)
                
                if lof_index_data:
                    lof_index_count = self.save_lof_index_to_database(lof_index_data)
                    logger.info(f"指数 LOF 数据抓取完成: {lof_index_count} 条")
                else:
                    logger.warning("未获取到指数 LOF 数据")
                    lof_index_count = 0
                
                # 汇总
                total_count = lof_count + qdii_count + lof_index_count
                if total_count == 0:
                    raise Exception("未获取到任何数据")
                
                duration = time.time() - start_time
                self.log_scrape_result("success", total_count, duration=duration)
                
                logger.info(f"抓取完成，共 {total_count} 条数据 (LOF: {lof_count}, QDII: {qdii_count}, 指数LOF: {lof_index_count})，耗时 {duration:.2f} 秒")
                
                # 手动关闭资源
                if self.context:
                    self.context.close()
                if self.browser:
                    self.browser.close()
                    
                return True
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"抓取失败: {error_msg}")
            self.log_scrape_result("failed", error_message=error_msg, duration=duration)
            return False


def run_scrape():
    """执行抓取任务的入口函数"""
    scraper = JisiluScraper()
    return scraper.run()

