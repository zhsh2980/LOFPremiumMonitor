-- 补充遗漏的 style columns
-- 执行方式: psql -U lof -d lof_monitor -f migrations/008_fix_missing_columns.sql

-- lof_data
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS volume_color VARCHAR(30);

-- qdii_data
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS manage_fee_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS benchmark_color VARCHAR(30);

-- lof_index_data
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS turnover_rate_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS tracking_index_color VARCHAR(30);
