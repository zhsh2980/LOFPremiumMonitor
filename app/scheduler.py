"""
定时任务调度模块
"""

import random
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from loguru import logger

from app.config import get_settings
from app.scraper import run_scrape


class ScrapeScheduler:
    """抓取任务调度器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.scheduler = BackgroundScheduler()
        self.next_run_time: datetime = None
    
    def _is_in_scrape_hours(self, dt: datetime = None) -> bool:
        """检查是否在允许抓取的时间段内"""
        if dt is None:
            dt = datetime.now()
        
        hour = dt.hour
        return self.settings.scrape_start_hour <= hour < self.settings.scrape_end_hour
    
    def _get_random_interval(self) -> int:
        """获取随机抓取间隔（分钟）"""
        return random.randint(
            self.settings.scrape_min_interval,
            self.settings.scrape_max_interval
        )
    
    def _calculate_next_run_time(self) -> datetime:
        """计算下一次运行时间"""
        now = datetime.now()
        
        # 如果当前不在抓取时间段，安排到下一个开始时间
        if not self._is_in_scrape_hours(now):
            if now.hour < self.settings.scrape_start_hour:
                # 今天的开始时间
                next_run = now.replace(
                    hour=self.settings.scrape_start_hour,
                    minute=random.randint(0, 30),
                    second=0,
                    microsecond=0
                )
            else:
                # 明天的开始时间
                next_run = (now + timedelta(days=1)).replace(
                    hour=self.settings.scrape_start_hour,
                    minute=random.randint(0, 30),
                    second=0,
                    microsecond=0
                )
        else:
            # 在抓取时间段内，随机间隔后执行
            interval_minutes = self._get_random_interval()
            next_run = now + timedelta(minutes=interval_minutes)
            
            # 如果计算出的时间超出了今天的抓取结束时间，安排到明天
            if next_run.hour >= self.settings.scrape_end_hour:
                next_run = (now + timedelta(days=1)).replace(
                    hour=self.settings.scrape_start_hour,
                    minute=random.randint(0, 30),
                    second=0,
                    microsecond=0
                )
        
        return next_run
    
    def _scrape_job(self):
        """抓取任务（在独立线程中执行以避免与 asyncio 冲突）"""
        import concurrent.futures
        
        logger.info("定时任务触发，开始抓取...")
        
        try:
            # 使用线程池执行抓取，避免 Playwright Sync API 与 asyncio 冲突
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_scrape)
                success = future.result(timeout=300)  # 5分钟超时
                
            if success:
                logger.info("抓取任务完成")
            else:
                logger.warning("抓取任务失败")
        except concurrent.futures.TimeoutError:
            logger.error("抓取任务超时")
        except Exception as e:
            logger.error(f"抓取任务异常: {e}")
        finally:
            # 安排下一次任务
            self._schedule_next()
    
    def _schedule_next(self):
        """安排下一次抓取任务"""
        self.next_run_time = self._calculate_next_run_time()
        
        # 添加新任务
        self.scheduler.add_job(
            self._scrape_job,
            trigger=DateTrigger(run_date=self.next_run_time),
            id="scrape_job",
            replace_existing=True
        )
        
        logger.info(f"下一次抓取时间: {self.next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def start(self, run_immediately: bool = True):
        """启动调度器"""
        logger.info("启动定时任务调度器...")
        
        # 启动调度器
        self.scheduler.start()
        
        # 如果需要且在抓取时间段内，延迟几秒后执行首次抓取（避免阻塞启动）
        if run_immediately and self._is_in_scrape_hours():
            logger.info("安排首次抓取（5秒后执行）...")
            self.next_run_time = datetime.now() + timedelta(seconds=5)
            self.scheduler.add_job(
                self._scrape_job,
                trigger=DateTrigger(run_date=self.next_run_time),
                id="scrape_job",
                replace_existing=True
            )
        else:
            # 安排下一次任务
            self._schedule_next()
    
    def stop(self):
        """停止调度器"""
        logger.info("停止定时任务调度器...")
        self.scheduler.shutdown()
    
    def get_next_run_time(self) -> datetime:
        """获取下一次运行时间"""
        return self.next_run_time


# 全局调度器实例
_scheduler: ScrapeScheduler = None


def get_scheduler() -> ScrapeScheduler:
    """获取调度器单例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = ScrapeScheduler()
    return _scheduler
