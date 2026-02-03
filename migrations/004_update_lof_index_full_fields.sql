-- 更新 lof_index_data 表结构 - 添加全部字段
-- 执行方式: psql -U lof -d lof_monitor -f migrations/004_update_lof_index_full_fields.sql

-- 添加缺失的字段
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS shares VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS shares_change VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS turnover_rate VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS nav VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS nav_date VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS rt_valuation VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS tracking_index VARCHAR(100);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS apply_fee VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS redeem_fee VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS redeem_status VARCHAR(50);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS fund_company VARCHAR(100);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS remark VARCHAR(200);

-- 添加字段注释
COMMENT ON COLUMN lof_index_data.shares IS '场内份额(万份)';
COMMENT ON COLUMN lof_index_data.shares_change IS '场内新增(万份)';
COMMENT ON COLUMN lof_index_data.turnover_rate IS '换手率';
COMMENT ON COLUMN lof_index_data.nav IS '基金净值';
COMMENT ON COLUMN lof_index_data.nav_date IS '净值日期';
COMMENT ON COLUMN lof_index_data.rt_valuation IS '实时估值';
COMMENT ON COLUMN lof_index_data.tracking_index IS '跟踪指数';
COMMENT ON COLUMN lof_index_data.apply_fee IS '申购费';
COMMENT ON COLUMN lof_index_data.redeem_fee IS '赎回费';
COMMENT ON COLUMN lof_index_data.redeem_status IS '赎回状态';
COMMENT ON COLUMN lof_index_data.fund_company IS '基金公司';
COMMENT ON COLUMN lof_index_data.remark IS '备注';
