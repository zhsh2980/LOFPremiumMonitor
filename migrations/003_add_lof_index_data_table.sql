-- 创建 lof_index_data 表
-- 执行方式: psql -U lof -d lof_monitor -f migrations/003_add_lof_index_data_table.sql

CREATE TABLE IF NOT EXISTS lof_index_data (
    id SERIAL PRIMARY KEY,
    
    -- 基础信息
    fund_code VARCHAR(20) NOT NULL,
    fund_name VARCHAR(100),
    
    -- 市场数据 (String)
    price VARCHAR(50),
    change_pct VARCHAR(50),
    volume VARCHAR(50),
    
    -- 净值与溢价
    premium_rate VARCHAR(50),
    
    -- 指数相关
    index_change_pct VARCHAR(50),
    
    -- 状态
    apply_status VARCHAR(50),
    
    -- 样式信息
    change_pct_color VARCHAR(30),
    premium_rate_color VARCHAR(30),
    index_change_pct_color VARCHAR(30),
    apply_status_color VARCHAR(30),
    
    -- 时间戳
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS ix_lof_index_data_id ON lof_index_data (id);
CREATE INDEX IF NOT EXISTS ix_lof_index_data_fund_code ON lof_index_data (fund_code);

-- 添加注释
COMMENT ON TABLE lof_index_data IS 'LOF 指数基金数据表（原始文本存储，按溢价率倒序）';
COMMENT ON COLUMN lof_index_data.fund_code IS '基金代码';
COMMENT ON COLUMN lof_index_data.fund_name IS '基金名称';
COMMENT ON COLUMN lof_index_data.price IS '现价';
COMMENT ON COLUMN lof_index_data.change_pct IS '涨幅';
COMMENT ON COLUMN lof_index_data.volume IS '成交额';
COMMENT ON COLUMN lof_index_data.premium_rate IS '溢价率';
COMMENT ON COLUMN lof_index_data.index_change_pct IS '指数涨幅';
COMMENT ON COLUMN lof_index_data.apply_status IS '申购状态';
COMMENT ON COLUMN lof_index_data.change_pct_color IS '涨幅颜色';
COMMENT ON COLUMN lof_index_data.premium_rate_color IS '溢价率颜色';
COMMENT ON COLUMN lof_index_data.index_change_pct_color IS '指数涨幅颜色';
COMMENT ON COLUMN lof_index_data.apply_status_color IS '申购状态颜色';
