
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, PropertyMock

# 设置环境变量以通过 Settings 验证
os.environ["JISILU_USERNAME"] = "test"
os.environ["JISILU_PASSWORD"] = "test"
os.environ["API_TOKEN"] = "testtoken"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/dbname"
os.environ["ALLOWED_IPS"] = "*"

from unittest.mock import MagicMock, patch
import sys

# Mock sqlalchemy 避免真实连接
mock_engine = MagicMock()
mock_session = MagicMock()
with patch("sqlalchemy.create_engine", return_value=mock_engine), \
     patch("sqlalchemy.orm.sessionmaker", return_value=mock_session):
    
    # 在 patch 上下文中导入
    from app.main import app
    from app.config import get_settings

# 覆盖 init_db 依赖
app.dependency_overrides = {}

client = TestClient(app)

def test_allow_all():
    """测试允许所有 IP"""
    # 模拟配置
    with patch("app.config.Settings.ip_list", new_callable=PropertyMock) as mock_ip:
        mock_ip.return_value = ["*"]
        
        response = client.get("/healthz", headers={"X-Forwarded-For": "1.2.3.4"})
        assert response.status_code == 200

def test_allow_specific_ip():
    """测试允许特定 IP"""
    with patch("app.config.Settings.ip_list", new_callable=PropertyMock) as mock_ip:
        mock_ip.return_value = ["1.2.3.4", "5.6.7.8"]
        
        # 允许的 IP
        response = client.get("/healthz", headers={"X-Forwarded-For": "1.2.3.4"})
        assert response.status_code == 200
        
        # 拒绝的 IP
        response = client.get("/healthz", headers={"X-Forwarded-For": "9.9.9.9"})
        assert response.status_code == 403
        assert response.json()["message"] == "Access denied from 9.9.9.9"

def test_no_x_forwarded_for():
    """测试无 X-Forwarded-For 头"""
    with patch("app.config.Settings.ip_list", new_callable=PropertyMock) as mock_ip:
        mock_ip.return_value = ["127.0.0.1"]
        
        # TestClient 的默认 client.host 是 testclient
        response = client.get("/healthz")
        # 此时 client.host 应该被拦截 (除非 mock 为 testclient)
        assert response.status_code == 403

if __name__ == "__main__":
    # 手动运行简单测试
    print("Running manual tests...")
    try:
        test_allow_all()
        print("✅ test_allow_all passed")
        test_allow_specific_ip()
        print("✅ test_allow_specific_ip passed")
        test_no_x_forwarded_for()
        print("✅ test_no_x_forwarded_for passed")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)
