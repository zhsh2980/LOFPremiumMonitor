-- 创建 qdii_data 表
-- 执行方式: psql -U lof -d lof_monitor -f migrations/002_add_qdii_data_table.sql

CREATE TABLE IF NOT EXISTS qdii_data (
    id SERIAL PRIMARY KEY,
    
    -- 基础信息
    fund_code VARCHAR(20) NOT NULL,
    fund_name VARCHAR(100),
    
    -- 市场数据 (String)
    price VARCHAR(50),
    change_pct VARCHAR(50),
    volume VARCHAR(50),
    shares VARCHAR(50),
    shares_change VARCHAR(50),
    
    -- 净值/估值数据 (String)
    nav_t2 VARCHAR(50),
    valuation_t1 VARCHAR(50),
    premium_rate_t1 VARCHAR(50),
    rt_valuation VARCHAR(50),
    rt_premium_rate VARCHAR(50),
    
    -- 状态
    apply_status VARCHAR(50),
    benchmark VARCHAR(100),
    
    -- 样式信息
    change_pct_color VARCHAR(30),
    premium_rate_t1_color VARCHAR(30),
    rt_premium_rate_color VARCHAR(30),
    apply_status_color VARCHAR(30),
    
    -- 时间戳
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS ix_qdii_data_id ON qdii_data (id);
CREATE INDEX IF NOT EXISTS ix_qdii_data_fund_code ON qdii_data (fund_code);

-- 添加注释
COMMENT ON TABLE qdii_data IS 'QDII 基金数据表（原始文本存储）';
COMMENT ON COLUMN qdii_data.fund_code IS '基金代码';
COMMENT ON COLUMN qdii_data.fund_name IS '基金名称';
COMMENT ON COLUMN qdii_data.price IS '现价';
COMMENT ON COLUMN qdii_data.change_pct IS '涨幅';
COMMENT ON COLUMN qdii_data.volume IS '成交(万元)';
COMMENT ON COLUMN qdii_data.shares IS '场内份额';
COMMENT ON COLUMN qdii_data.shares_change IS '份额新增';
COMMENT ON COLUMN qdii_data.nav_t2 IS 'T-2净值';
COMMENT ON COLUMN qdii_data.valuation_t1 IS 'T-1估值';
COMMENT ON COLUMN qdii_data.premium_rate_t1 IS 'T-1溢价率';
COMMENT ON COLUMN qdii_data.rt_valuation IS '实时估值';
COMMENT ON COLUMN qdii_data.rt_premium_rate IS '实时溢价率';
COMMENT ON COLUMN qdii_data.apply_status IS '申购状态';
COMMENT ON COLUMN qdii_data.benchmark IS '相关标的';
COMMENT ON COLUMN qdii_data.change_pct_color IS '涨幅颜色';
COMMENT ON COLUMN qdii_data.premium_rate_t1_color IS 'T-1溢价率颜色';
COMMENT ON COLUMN qdii_data.rt_premium_rate_color IS '实时溢价率颜色';
COMMENT ON COLUMN qdii_data.apply_status_color IS '申购状态颜色';
