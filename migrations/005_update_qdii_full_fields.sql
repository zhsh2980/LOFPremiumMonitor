-- 更新 qdii_data 表结构 - 添加全部字段
-- 执行方式: psql -U lof -d lof_monitor -f migrations/005_update_qdii_full_fields.sql

-- 添加缺失的字段
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS nav_date VARCHAR(50);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS valuation_date VARCHAR(50);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS apply_fee VARCHAR(50);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS redeem_fee VARCHAR(50);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS redeem_status VARCHAR(50);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS manage_fee VARCHAR(50);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS fund_company VARCHAR(100);

-- 添加字段注释
COMMENT ON COLUMN qdii_data.nav_date IS '净值日期';
COMMENT ON COLUMN qdii_data.valuation_date IS '估值日期';
COMMENT ON COLUMN qdii_data.apply_fee IS '申购费';
COMMENT ON COLUMN qdii_data.redeem_fee IS '赎回费';
COMMENT ON COLUMN qdii_data.redeem_status IS '赎回状态';
COMMENT ON COLUMN qdii_data.manage_fee IS '管托费';
COMMENT ON COLUMN qdii_data.fund_company IS '基金公司';
