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
    
    # 样式信息（用于前端展示原始颜色）    # 样式信息 (全量字段)
    price_color = Column(String(30), nullable=True)
    change_pct_color = Column(String(30), nullable=True)
    volume_color = Column(String(30), nullable=True)
    amount_color = Column(String(30), nullable=True)
    premium_rate_color = Column(String(30), nullable=True)
    estimate_nav_color = Column(String(30), nullable=True)
    nav_color = Column(String(30), nullable=True)
    nav_date_color = Column(String(30), nullable=True)
    shares_color = Column(String(30), nullable=True)
    shares_change_color = Column(String(30), nullable=True)
    apply_fee_color = Column(String(30), nullable=True)
    apply_status_color = Column(String(30), nullable=True)
    apply_status_bg_color = Column(String(30), nullable=True)  # 保留特有的背景色
    redeem_fee_color = Column(String(30), nullable=True)
    redeem_status_color = Column(String(30), nullable=True)
    fund_company_color = Column(String(30), nullable=True)
    
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
                "price": { "color": self.price_color },
                "change_pct": { "color": self.change_pct_color },
                "volume": { "color": self.volume_color },
                "amount": { "color": self.amount_color },
                "premium_rate": { "color": self.premium_rate_color },
                "estimate_nav": { "color": self.estimate_nav_color },
                "nav": { "color": self.nav_color },
                "nav_date": { "color": self.nav_date_color },
                "shares": { "color": self.shares_color },
                "shares_change": { "color": self.shares_change_color },
                "apply_fee": { "color": self.apply_fee_color },
                "apply_status": { 
                    "color": self.apply_status_color,
                    "backgroundColor": self.apply_status_bg_color
                },
                "redeem_fee": { "color": self.redeem_fee_color },
                "redeem_status": { "color": self.redeem_status_color },
                "fund_company": { "color": self.fund_company_color }
            }
        }


class QDIIData(Base):
    """QDII 基金数据表（原始文本存储）"""
    __tablename__ = "qdii_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基础信息
    fund_code = Column(String(20), nullable=False, index=True, comment="基金代码")
    fund_name = Column(String(100), comment="基金名称")
    
    # 市场数据
    price = Column(String(50), comment="现价")
    change_pct = Column(String(50), comment="涨幅")
    volume = Column(String(50), comment="成交(万元)")
    shares = Column(String(50), comment="场内份额")
    shares_change = Column(String(50), comment="份额新增")
    
    # 净值/估值数据
    nav_t2 = Column(String(50), comment="T-2净值")
    nav_date = Column(String(50), comment="净值日期")
    valuation_t1 = Column(String(50), comment="T-1估值")
    valuation_date = Column(String(50), comment="估值日期")
    premium_rate_t1 = Column(String(50), comment="T-1溢价率")
    rt_valuation = Column(String(50), comment="实时估值")
    rt_premium_rate = Column(String(50), comment="实时溢价率")
    benchmark = Column(String(100), comment="相关标的")
    
    # 费率与状态
    apply_fee = Column(String(50), comment="申购费")
    apply_status = Column(String(50), comment="申购状态")
    redeem_fee = Column(String(50), comment="赎回费")
    redeem_status = Column(String(50), comment="赎回状态")
    manage_fee = Column(String(50), comment="管托费")
    fund_company = Column(String(100), comment="基金公司")
    
    # 样式信息 (全量字段)
    price_color = Column(String(30), nullable=True)
    change_pct_color = Column(String(30), nullable=True)
    volume_color = Column(String(30), nullable=True)
    shares_color = Column(String(30), nullable=True)
    shares_change_color = Column(String(30), nullable=True)
    nav_t2_color = Column(String(30), nullable=True)
    nav_date_color = Column(String(30), nullable=True)
    valuation_t1_color = Column(String(3(30), nullable=True))
    valuation_date_color = Column(String(30), nullable=True)
    premium_rate_t1_color = Column(String(30), nullable=True)
    rt_valuation_color = Column(String(30), nullable=True)
    rt_premium_rate_color = Column(String(30), nullable=True)
    benchmark_color = Column(String(30), nullable=True)
    apply_fee_color = Column(String(30), nullable=True)
    apply_status_color = Column(String(30), nullable=True)
    redeem_fee_color = Column(String(30), nullable=True)
    redeem_status_color = Column(String(30), nullable=True)
    manage_fee_color = Column(String(30), nullable=True)
    fund_company_color = Column(String(30), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "fund_code": self.fund_code,
            "fund_name": self.fund_name,
            "price": self.price,
            "change_pct": self.change_pct,
            "volume": self.volume,
            "shares": self.shares,
            "shares_change": self.shares_change,
            "nav_t2": self.nav_t2,
            "nav_date": self.nav_date,
            "valuation_t1": self.valuation_t1,
            "valuation_date": self.valuation_date,
            "premium_rate_t1": self.premium_rate_t1,
            "rt_valuation": self.rt_valuation,
            "rt_premium_rate": self.rt_premium_rate,
            "benchmark": self.benchmark,
            "apply_fee": self.apply_fee,
            "apply_status": self.apply_status,
            "redeem_fee": self.redeem_fee,
            "redeem_status": self.redeem_status,
            "manage_fee": self.manage_fee,
            "fund_company": self.fund_company,
            # 样式信息
            "styles": {
                "price": { "color": self.price_color },
                "change_pct": { "color": self.change_pct_color },
                "volume": { "color": self.volume_color },
                "shares": { "color": self.shares_color },
                "shares_change": { "color": self.shares_change_color },
                "nav_t2": { "color": self.nav_t2_color },
                "nav_date": { "color": self.nav_date_color },
                "valuation_t1": { "color": self.valuation_t1_color },
                "valuation_date": { "color": self.valuation_date_color },
                "premium_rate_t1": { "color": self.premium_rate_t1_color },
                "rt_valuation": { "color": self.rt_valuation_color },
                "rt_premium_rate": { "color": self.rt_premium_rate_color },
                "benchmark": { "color": self.benchmark_color },
                "apply_fee": { "color": self.apply_fee_color },
                "apply_status": { "color": self.apply_status_color },
                "redeem_fee": { "color": self.redeem_fee_color },
                "redeem_status": { "color": self.redeem_status_color },
                "manage_fee": { "color": self.manage_fee_color },
                "fund_company": { "color": self.fund_company_color }
            }
        }


class LOFIndexData(Base):
    """LOF 指数基金数据表（原始文本存储，按溢价率倒序）"""
    __tablename__ = "lof_index_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基础信息 (0-1)
    fund_code = Column(String(20), nullable=False, index=True, comment="基金代码")
    fund_name = Column(String(100), comment="基金名称")
    
    # 市场数据 (2-7)
    price = Column(String(50), comment="现价")
    change_pct = Column(String(50), comment="涨幅")
    volume = Column(String(50), comment="成交额(万元)")
    shares = Column(String(50), comment="场内份额(万份)")
    shares_change = Column(String(50), comment="场内新增(万份)")
    turnover_rate = Column(String(50), comment="换手率")
    
    # 净值数据 (8-10)
    nav = Column(String(50), comment="基金净值")
    nav_date = Column(String(50), comment="净值日期")
    rt_valuation = Column(String(50), comment="实时估值")
    
    # 溢价数据 (11)
    premium_rate = Column(String(50), comment="溢价率")
    
    # 指数相关 (12-13)
    tracking_index = Column(String(100), comment="跟踪指数")
    index_change_pct = Column(String(50), comment="指数涨幅")
    
    # 费率与状态 (14-17)
    apply_fee = Column(String(50), comment="申购费")
    apply_status = Column(String(50), comment="申购状态")
    redeem_fee = Column(String(50), comment="赎回费")
    redeem_status = Column(String(50), comment="赎回状态")
    
    # 其他信息 (18-19)
    fund_company = Column(String(100), comment="基金公司")
    remark = Column(String(200), comment="备注")
    
    # 样式信息 (全量字段)
    price_color = Column(String(30), nullable=True)
    change_pct_color = Column(String(30), nullable=True)
    volume_color = Column(String(30), nullable=True)
    shares_color = Column(String(30), nullable=True)
    shares_change_color = Column(String(30), nullable=True)
    turnover_rate_color = Column(String(30), nullable=True)
    nav_color = Column(String(30), nullable=True)
    nav_date_color = Column(String(30), nullable=True)
    rt_valuation_color = Column(String(30), nullable=True)
    premium_rate_color = Column(String(30), nullable=True)
    tracking_index_color = Column(String(30), nullable=True)
    index_change_pct_color = Column(String(30), nullable=True)
    apply_fee_color = Column(String(30), nullable=True)
    apply_status_color = Column(String(30), nullable=True)
    redeem_fee_color = Column(String(30), nullable=True)
    redeem_status_color = Column(String(30), nullable=True)
    fund_company_color = Column(String(30), nullable=True)
    remark_color = Column(String(30), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "fund_code": self.fund_code,
            "fund_name": self.fund_name,
            "price": self.price,
            "change_pct": self.change_pct,
            "volume": self.volume,
            "shares": self.shares,
            "shares_change": self.shares_change,
            "turnover_rate": self.turnover_rate,
            "nav": self.nav,
            "nav_date": self.nav_date,
            "rt_valuation": self.rt_valuation,
            "premium_rate": self.premium_rate,
            "tracking_index": self.tracking_index,
            "index_change_pct": self.index_change_pct,
            "apply_fee": self.apply_fee,
            "apply_status": self.apply_status,
            "redeem_fee": self.redeem_fee,
            "redeem_status": self.redeem_status,
            "fund_company": self.fund_company,
            "remark": self.remark,
            # 样式信息
            "styles": {
                "price": { "color": self.price_color },
                "change_pct": { "color": self.change_pct_color },
                "volume": { "color": self.volume_color },
                "shares": { "color": self.shares_color },
                "shares_change": { "color": self.shares_change_color },
                "turnover_rate": { "color": self.turnover_rate_color },
                "nav": { "color": self.nav_color },
                "nav_date": { "color": self.nav_date_color },
                "rt_valuation": { "color": self.rt_valuation_color },
                "premium_rate": { "color": self.premium_rate_color },
                "tracking_index": { "color": self.tracking_index_color },
                "index_change_pct": { "color": self.index_change_pct_color },
                "apply_fee": { "color": self.apply_fee_color },
                "apply_status": { "color": self.apply_status_color },
                "redeem_fee": { "color": self.redeem_fee_color },
                "redeem_status": { "color": self.redeem_status_color },
                "fund_company": { "color": self.fund_company_color },
                "remark": { "color": self.remark_color }
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
