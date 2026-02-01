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

@app.middleware("http")
async def check_ip_middleware(request, call_next):
    """IP 白名单检查中间件"""
    ip_list = settings.ip_list
    
    # 如果允许所有，直接通过
    if "*" in ip_list:
        return await call_next(request)
    
    # 获取真实 IP (优先 X-Forwarded-For，适配 Docker/Nginx)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
        
    # 检查是否在白名单中
    if client_ip not in ip_list:
        logger.warning(f"拒绝非法 IP 访问: {client_ip}")
        # 这里返回 JSON 响应
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=403,
            content={"code": 403, "message": f"Access denied from {client_ip}"}
        )
        
    return await call_next(request)

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
