"""
API 接口定义
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import get_settings
from app.database import get_db
from app.models import LOFData, ScrapeLog, QDIIData
from app.scheduler import get_scheduler

router = APIRouter()
security = HTTPBearer()
settings = get_settings()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证 API Token"""
    if credentials.credentials != settings.api_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials


def get_last_scrape_time(db: Session) -> Optional[datetime]:
    """获取最后一次成功抓取的时间"""
    log = db.query(ScrapeLog).filter(
        ScrapeLog.status == "success"
    ).order_by(desc(ScrapeLog.scrape_time)).first()
    
    return log.scrape_time if log else None


@router.get("/lof/list")
def get_lof_list(
    min_premium: float = Query(default=None, description="最小溢价率(%)，默认使用配置值"),
    status: str = Query(default="all", description="申购状态: all/limited/open/suspended"),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    获取 LOF 溢价数据
    
    - 默认筛选溢价率 >= 3% 的基金
    - 按溢价率倒序排列
    """
    # 使用默认最小溢价率
    if min_premium is None:
        min_premium = settings.default_min_premium
    
    # 构建查询
    query = db.query(LOFData).filter(LOFData.premium_rate >= min_premium)
    
    # 申购状态筛选
    if status != "all":
        query = query.filter(LOFData.apply_status == status)
    
    # 按溢价率倒序排列
    query = query.order_by(desc(LOFData.premium_rate))
    
    # 执行查询
    items = query.all()
    
    # 获取最后更新时间
    update_time = get_last_scrape_time(db)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "update_time": update_time.isoformat() if update_time else None,
            "count": len(items),
            "items": [item.to_dict() for item in items]
        }
    }


@router.get("/lof/all")
def get_lof_all(
    status: str = Query(default="all", description="申购状态: all/limited/open/suspended"),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    获取全部 LOF 数据
    
    - 不做溢价率筛选
    - 按溢价率倒序排列
    """
    # 构建查询
    query = db.query(LOFData)
    
    # 申购状态筛选
    if status != "all":
        query = query.filter(LOFData.apply_status == status)
    
    # 按溢价率倒序排列
    query = query.order_by(desc(LOFData.premium_rate))
    
    # 执行查询
    items = query.all()
    
    # 获取最后更新时间
    update_time = get_last_scrape_time(db)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "update_time": update_time.isoformat() if update_time else None,
            "count": len(items),
            "items": [item.to_dict() for item in items]
        }
    }


@router.get("/qdii/commodity")
def get_qdii_commodity(
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    获取 QDII 商品数据 (原始格式)
    """
    # 获取最后更新时间
    update_time = get_last_scrape_time(db)
    
    # 获取所有 QDII 商品数据
    items = db.query(QDIIData).all()
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "update_time": update_time.isoformat() if update_time else None,
            "count": len(items),
            "items": [item.to_dict() for item in items]
        }
    }


@router.get("/status")
def get_status(
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    获取服务状态
    
    - 最后更新时间
    - 最后抓取状态
    - 数据条数
    - 下次抓取时间
    """
    # 获取最后一次抓取记录
    last_log = db.query(ScrapeLog).order_by(
        desc(ScrapeLog.scrape_time)
    ).first()
    
    # 获取数据条数
    record_count = db.query(LOFData).count()
    
    # 获取下次抓取时间
    scheduler = get_scheduler()
    next_scrape = scheduler.get_next_run_time()
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "last_update": last_log.scrape_time.isoformat() if last_log else None,
            "last_status": last_log.status if last_log else None,
            "last_error": last_log.error_message if last_log and last_log.status == "failed" else None,
            "record_count": record_count,
            "next_scrape": next_scrape.isoformat() if next_scrape else None
        }
    }


@router.get("/logs")
def get_logs(
    limit: int = Query(default=10, le=50, description="返回记录数"),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    获取抓取日志
    """
    logs = db.query(ScrapeLog).order_by(
        desc(ScrapeLog.scrape_time)
    ).limit(limit).all()
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "count": len(logs),
            "items": [log.to_dict() for log in logs]
        }
    }
