"""
LOF 溢价监控服务 - 主入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.config import get_settings
from app.database import init_db
from app.api.endpoints import router as api_router
from app.scheduler import get_scheduler


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("应用启动中...")
    
    # 初始化数据库
    logger.info("初始化数据库...")
    init_db()
    
    # 启动定时任务
    logger.info("启动定时任务调度器...")
    scheduler = get_scheduler()
    scheduler.start(run_immediately=True)
    
    logger.info("应用启动完成")
    
    yield
    
    # 关闭时
    logger.info("应用关闭中...")
    scheduler.stop()
    logger.info("应用已关闭")


# 创建 FastAPI 应用
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="LOF 基金溢价监控服务 API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/healthz")
def health_check():
    """健康检查接口（无需认证）"""
    return {"status": "ok"}


@app.get("/")
def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
