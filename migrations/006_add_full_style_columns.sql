-- 更新所有表结构 - 添加全量样式字段
-- 执行方式: psql -U lof -d lof_monitor -f migrations/006_add_full_style_columns.sql

-- 1. lof_data (LOF套利)
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS price_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS amount_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS estimate_nav_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS nav_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS nav_date_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS shares_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS shares_change_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS apply_fee_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS redeem_fee_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS redeem_status_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS fund_company_color VARCHAR(30);

-- 2. qdii_data (QDII商品)
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS price_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS volume_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS shares_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS shares_change_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS nav_t2_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS nav_date_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS valuation_t1_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS valuation_date_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS rt_valuation_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS benchmark_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS apply_fee_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS redeem_fee_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS redeem_status_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS manage_fee_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS fund_company_color VARCHAR(30);

-- 3. lof_index_data (指数LOF)
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS price_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS volume_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS shares_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS shares_change_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS turnover_rate_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS nav_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS nav_date_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS rt_valuation_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS tracking_index_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS apply_fee_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS redeem_fee_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS redeem_status_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS fund_company_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS remark_color VARCHAR(30);
