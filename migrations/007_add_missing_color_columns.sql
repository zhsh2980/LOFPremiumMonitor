-- 补充遗漏的 fund_code_color 和 fund_name_color 字段
-- 执行方式: psql -U lof -d lof_monitor -f migrations/007_add_missing_color_columns.sql

-- 1. lof_data (LOF套利)
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS fund_code_color VARCHAR(30);
ALTER TABLE lof_data ADD COLUMN IF NOT EXISTS fund_name_color VARCHAR(30);

-- 2. qdii_data (QDII商品)
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS fund_code_color VARCHAR(30);
ALTER TABLE qdii_data ADD COLUMN IF NOT EXISTS fund_name_color VARCHAR(30);

-- 3. lof_index_data (指数LOF)
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS fund_code_color VARCHAR(30);
ALTER TABLE lof_index_data ADD COLUMN IF NOT EXISTS fund_name_color VARCHAR(30);
