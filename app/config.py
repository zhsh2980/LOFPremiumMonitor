"""
配置管理模块
从环境变量加载配置
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用设置
    app_name: str = "LOF Premium Monitor"
    debug: bool = False
    
    # 集思录账号
    jisilu_username: str
    jisilu_password: str
    
    # API 认证
    api_token: str
    
    # 数据库
    database_url: str
    
    # 抓取配置
    scrape_min_interval: int = 50  # 最小抓取间隔（分钟）
    scrape_max_interval: int = 70  # 最大抓取间隔（分钟）
    scrape_start_hour: int = 7     # 开始抓取时间（小时）
    scrape_end_hour: int = 24      # 结束抓取时间（小时）
    
    # 默认筛选
    default_min_premium: float = 3.0  # 默认最小溢价率（%）
    
    # 安全配置
    allowed_ips: str = "*"  # 允许访问的 IP 列表，逗号分隔。* 表示允许所有

    @property
    def ip_list(self) -> list[str]:
        """解析 allowed_ips 为列表"""
        if not self.allowed_ips or self.allowed_ips == "*":
            return ["*"]
        return [ip.strip() for ip in self.allowed_ips.split(",") if ip.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
