"""
数据库模型定义
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Date, BigInteger
from app.database import Base


class LOFData(Base):
    """LOF 基金数据表"""
    __tablename__ = "lof_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基金基本信息
    fund_code = Column(String(10), nullable=False, index=True, comment="基金代码")
    fund_name = Column(String(100), nullable=False, comment="基金名称")
    fund_tags = Column(String(50), nullable=True, comment="基金标签，如 T+0,QD")
    
    # 价格信息
    price = Column(Numeric(10, 4), nullable=True, comment="场内价格")
    change_pct = Column(Numeric(6, 3), nullable=True, comment="涨跌幅(%)")
    volume = Column(BigInteger, nullable=True, comment="成交量")
    amount = Column(Numeric(15, 2), nullable=True, comment="成交额(万元)")
    
    # 净值信息
    nav = Column(Numeric(10, 4), nullable=True, comment="基金净值")
    nav_date = Column(Date, nullable=True, comment="净值日期")
    estimate_nav = Column(Numeric(10, 4), nullable=True, comment="估值")
    
    # 溢价信息
    premium_rate = Column(Numeric(6, 3), nullable=False, index=True, comment="溢价率(%)")
    
    # 份额信息
    shares = Column(Numeric(15, 2), nullable=True, comment="场内份额(万份)")
    shares_change = Column(Numeric(15, 2), nullable=True, comment="场内新增(万份)")
    
    # 申购赎回信息
    apply_fee = Column(String(20), nullable=True, comment="申购费")
    apply_status = Column(String(20), nullable=True, comment="申购状态: open/limited/suspended")
    apply_limit = Column(String(50), nullable=True, comment="申购限额说明")
    redeem_fee = Column(String(20), nullable=True, comment="赎回费")
    redeem_status = Column(String(20), nullable=True, comment="赎回状态")
    
    # 基金公司
    fund_company = Column(String(50), nullable=True, comment="基金公司")
    
    # 样式信息（用于前端展示原始颜色）
    change_pct_color = Column(String(30), nullable=True, comment="涨跌幅文字颜色(RGB)")
    premium_rate_color = Column(String(30), nullable=True, comment="溢价率文字颜色(RGB)")
    apply_status_color = Column(String(30), nullable=True, comment="申购状态文字颜色(RGB)")
    apply_status_bg_color = Column(String(30), nullable=True, comment="申购状态背景色(RGB)")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "fund_code": self.fund_code,
            "fund_name": self.fund_name,
            "fund_tags": self.fund_tags.split(",") if self.fund_tags else [],
            "price": float(self.price) if self.price else None,
            "change_pct": float(self.change_pct) if self.change_pct else None,
            "volume": self.volume,
            "amount": float(self.amount) if self.amount else None,
            "nav": float(self.nav) if self.nav else None,
            "nav_date": self.nav_date.isoformat() if self.nav_date else None,
            "estimate_nav": float(self.estimate_nav) if self.estimate_nav else None,
            "premium_rate": float(self.premium_rate) if self.premium_rate else None,
            "shares": float(self.shares) if self.shares else None,
            "shares_change": float(self.shares_change) if self.shares_change else None,
            "apply_fee": self.apply_fee,
            "apply_status": self.apply_status,
            "apply_limit": self.apply_limit,
            "redeem_fee": self.redeem_fee,
            "redeem_status": self.redeem_status,
            "fund_company": self.fund_company,
            # 样式信息
            "styles": {
                "change_pct": {
                    "color": self.change_pct_color
                },
                "premium_rate": {
                    "color": self.premium_rate_color
                },
                "apply_status": {
                    "color": self.apply_status_color,
                    "backgroundColor": self.apply_status_bg_color
                }
            }
        }


class ScrapeLog(Base):
    """抓取日志表"""
    __tablename__ = "scrape_log"
    
    id = Column(Integer, primary_key=True, index=True)
    scrape_time = Column(DateTime, default=datetime.now, index=True, comment="抓取时间")
    status = Column(String(20), nullable=False, comment="状态: success/failed")
    record_count = Column(Integer, default=0, comment="抓取记录数")
    error_message = Column(Text, nullable=True, comment="错误信息")
    duration_seconds = Column(Numeric(6, 2), nullable=True, comment="耗时(秒)")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "scrape_time": self.scrape_time.isoformat() if self.scrape_time else None,
            "status": self.status,
            "record_count": self.record_count,
            "error_message": self.error_message,
            "duration_seconds": float(self.duration_seconds) if self.duration_seconds else None,
        }
