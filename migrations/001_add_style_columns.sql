-- 添加样式字段到 lof_data 表
-- 执行方式: psql -U lof_user -d lof_monitor -f migrations/001_add_style_columns.sql

ALTER TABLE lof_data 
ADD COLUMN IF NOT EXISTS change_pct_color VARCHAR(30),
ADD COLUMN IF NOT EXISTS premium_rate_color VARCHAR(30),
ADD COLUMN IF NOT EXISTS apply_status_color VARCHAR(30),
ADD COLUMN IF NOT EXISTS apply_status_bg_color VARCHAR(30);

-- 添加注释
COMMENT ON COLUMN lof_data.change_pct_color IS '涨跌幅文字颜色(RGB)';
COMMENT ON COLUMN lof_data.premium_rate_color IS '溢价率文字颜色(RGB)';
COMMENT ON COLUMN lof_data.apply_status_color IS '申购状态文字颜色(RGB)';
COMMENT ON COLUMN lof_data.apply_status_bg_color IS '申购状态背景色(RGB)';
