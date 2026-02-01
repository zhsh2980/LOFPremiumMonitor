
import logging
import sys
import os

# 配置日志输出到 stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 确保当前目录在 python path 中
sys.path.append(os.getcwd())

from app.scraper import run_scrape, logger

if __name__ == "__main__":
    logger.info("Subprocess: 启动抓取任务...")
    try:
        success = run_scrape()
        if success:
            logger.info("Subprocess: 抓取任务成功")
            sys.exit(0)
        else:
            logger.error("Subprocess: 抓取任务失败")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Subprocess: 抓取任务异常: {e}")
        sys.exit(1)
