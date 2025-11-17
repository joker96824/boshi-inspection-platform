-- 为任务表添加总用时字段
-- 执行时间：2025-01-XX
-- 说明：为 tb_task 表添加 total_duration 字段，用于记录任务总用时（单位：分钟）

USE boshirobot;

-- 添加 total_duration 字段
ALTER TABLE tb_task 
ADD COLUMN total_duration INT NULL COMMENT '任务总用时（分钟）' 
AFTER task_int_prior;

-- 验证字段是否添加成功
-- SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_COMMENT 
-- FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_SCHEMA = 'boshirobot' 
--   AND TABLE_NAME = 'tb_task' 
--   AND COLUMN_NAME = 'total_duration';

