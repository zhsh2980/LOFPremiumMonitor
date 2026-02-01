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
from app.models import LOFData, ScrapeLog

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
                    })
                    
                except Exception as e:
                    logger.warning(f"解析行数据失败: {e}")
                    continue
            
            logger.info(f"成功解析 {len(data_list)} 条数据")
            return data_list
            
        except Exception as e:
            logger.error(f"抓取数据异常: {e}")
            raise
    
    def save_to_database(self, data_list: List[Dict]) -> int:
        """保存数据到数据库"""
        logger.info(f"正在保存 {len(data_list)} 条数据到数据库...")
        
        db = SessionLocal()
        try:
            # 清空旧数据
            db.query(LOFData).delete()
            
            # 批量插入新数据
            for data in data_list:
                lof = LOFData(**data)
                db.add(lof)
            
            db.commit()
            logger.info(f"成功保存 {len(data_list)} 条数据")
            return len(data_list)
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存数据失败: {e}")
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
                
                # 抓取数据
                data_list = self.scrape_lof_data(self.page)
                
                if not data_list:
                    raise Exception("未获取到任何数据")
                
                # 保存到数据库
                count = self.save_to_database(data_list)
                
                duration = time.time() - start_time
                self.log_scrape_result("success", count, duration=duration)
                
                logger.info(f"抓取完成，共 {count} 条数据，耗时 {duration:.2f} 秒")
                
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

