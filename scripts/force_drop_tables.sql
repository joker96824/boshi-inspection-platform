-- 强制删除所有表
USE boshirobot;

-- 禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- 删除所有表
DROP TABLE IF EXISTS tb_taskhistory;
DROP TABLE IF EXISTS tb_taskschedule;
DROP TABLE IF EXISTS tb_task;
DROP TABLE IF EXISTS tb_point;
DROP TABLE IF EXISTS tb_mapnet;
DROP TABLE IF EXISTS tb_robot;
DROP TABLE IF EXISTS tb_map;
DROP TABLE IF EXISTS tb_sessions;
DROP TABLE IF EXISTS tb_users;

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;
