-- 博实智能巡检平台 - 示例数据初始化SQL
USE boshirobot;

-- 更新数据库表结构（如果字段不存在则添加）
-- 为巡检项目表添加机器人ID字段
SET @dbname = DATABASE();
SET @tablename = 'tb_item';
SET @columnname = 'robot_id';
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE
            (TABLE_SCHEMA = @dbname)
            AND (TABLE_NAME = @tablename)
            AND (COLUMN_NAME = @columnname)
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(36) NULL COMMENT ''关联机器人ID'' AFTER device_id')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 为巡检项目表添加检测类型ID字段
SET @tablename = 'tb_item';
SET @columnname = 'detection_type_id';
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE
            (TABLE_SCHEMA = @dbname)
            AND (TABLE_NAME = @tablename)
            AND (COLUMN_NAME = @columnname)
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(36) NULL COMMENT ''检测类型ID'' AFTER robot_id, ADD INDEX idx_detection_type_id (detection_type_id), ADD FOREIGN KEY (detection_type_id) REFERENCES tb_detection_type(id) ON DELETE SET NULL')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 添加外键约束（如果不存在）
SET @constraintname = 'fk_item_robot';
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE
            (TABLE_SCHEMA = @dbname)
            AND (TABLE_NAME = @tablename)
            AND (CONSTRAINT_NAME = @constraintname)
            AND (CONSTRAINT_TYPE = 'FOREIGN KEY')
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD CONSTRAINT ', @constraintname, ' FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE SET NULL')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 添加索引（如果不存在）
SET @indexname = 'idx_robot_id';
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
        WHERE
            (TABLE_SCHEMA = @dbname)
            AND (TABLE_NAME = @tablename)
            AND (INDEX_NAME = @indexname)
    ) > 0,
    'SELECT 1',
    CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(robot_id)')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 清空所有示例数据（如果存在）
-- 注意：使用 SET FOREIGN_KEY_CHECKS = 0 来禁用外键检查，以便可以按任意顺序删除数据
SET FOREIGN_KEY_CHECKS = 0;

-- 按外键依赖顺序删除数据（从子表到父表）
DELETE FROM tb_alarm_info;
DELETE FROM tb_alarm_rule_relation;
DELETE FROM tb_alarm_rule;
DELETE FROM tb_taskresult;
DELETE FROM tb_itemhistory;
DELETE FROM tb_item;
DELETE FROM tb_detection_type;
DELETE FROM tb_taskhistory;
DELETE FROM tb_taskschedule;
DELETE FROM tb_task;
DELETE FROM tb_point;
DELETE FROM tb_mapnet;
DELETE FROM tb_robot_map;
DELETE FROM tb_robot;
DELETE FROM tb_gimbalhistory;
DELETE FROM tb_gimbalschedule;
DELETE FROM tb_gimbal_inspection_project_preset_point;
DELETE FROM tb_gimbal_preset_point;
DELETE FROM tb_gimbal_inspection_project;
DELETE FROM tb_gimbaltask;
DELETE FROM tb_gimbal;
DELETE FROM tb_sensorhistory;
DELETE FROM tb_sensor;
DELETE FROM tb_device;
DELETE FROM cfg_vehicle_controller;
DELETE FROM cfg_environment_sensor;
DELETE FROM cfg_dual_ptz;
DELETE FROM cfg_motor_status;
DELETE FROM cfg_lidar;
DELETE FROM cfg_robot_arm;
DELETE FROM cfg_ultrasonic;
DELETE FROM cfg_depth_camera;
DELETE FROM cfg_navigation_controller;
DELETE FROM tb_operation_record;
DELETE FROM tb_manual_operation;
DELETE FROM tb_map;
DELETE FROM tb_factory;
DELETE FROM tb_sessions;
DELETE FROM tb_users;

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 插入默认用户
-- superadmin/superadmin (超级管理员)
-- admin/admin (管理员)
-- operator/operator (操作员)
INSERT INTO tb_users (id, username, password_hash, role, created_at, updated_at, created_by) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'superadmin', '$2b$12$kRjLRFxYlP1B/cSdwWiyMuUyBhVO3JoKrnl2k9kQfwPvqbqxgG8mu', 'super_admin', NOW(), NOW(), 'system'),
('550e8400-e29b-41d4-a716-446655440101', 'admin', '$2b$12$aO5ac829bmhgt8.3Bszrq.ByPvri0qLi1fN9gGgmpShzSF3yGiqle', 'admin', NOW(), NOW(), 'system'),
('550e8400-e29b-41d4-a716-446655440102', 'operator', '$2b$12$iaUv0/mZ1YaPJIl3e9G48uac9xTPzUzuM7miyvP5MS7z4Kflmttvy', 'operator', NOW(), NOW(), 'system');

-- 插入示例厂区数据
INSERT INTO tb_factory (id, factory_name, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440000', '厂区一', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440001', '厂区二', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例地图数据
INSERT INTO tb_map (id, map_name, map_image_url, map_scale, map_center_x, map_center_y, factory_id, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440010', '厂区一地图', '/uploads/maps/factory1_map.png', 1.0, 100.0, 100.0, '550e8400-e29b-41d4-a716-446655440000', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440011', '厂区二地图一', '/uploads/maps/factory2_map1.png', 1.0, 100.0, 100.0, '550e8400-e29b-41d4-a716-446655440001', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440012', '厂区二地图二', '/uploads/maps/factory2_map2.png', 1.0, 100.0, 100.0, '550e8400-e29b-41d4-a716-446655440001', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例地图路网数据
-- 厂区一地图路网
INSERT INTO tb_mapnet (id, map_id, map_net_type, map_net_properties, map_net_geometry, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440501', '550e8400-e29b-41d4-a716-446655440010', 'point', '{"name": "导航点A", "type": "navigation"}', '{"x": 50.0, "y": 50.0}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440502', '550e8400-e29b-41d4-a716-446655440010', 'line', '{"name": "巡检路径1", "width": 2, "color": "blue"}', '{"start": {"x": 50.0, "y": 50.0}, "end": {"x": 150.0, "y": 50.0}}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440503', '550e8400-e29b-41d4-a716-446655440010', 'rect', '{"name": "禁区范围", "type": "restricted"}', '{"x": 80.0, "y": 80.0, "width": 40.0, "height": 30.0}', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例机器人数据
INSERT INTO tb_robot (id, robot_name, robot_info, factory_id, preview_url, control_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440020', '厂区一机器人001', '{"model": "BOSHI-RB-01", "battery": 100, "status": "idle"}', '550e8400-e29b-41d4-a716-446655440000', NULL, NULL, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440021', '厂区一机器人002', '{"model": "BOSHI-RB-02", "battery": 85, "status": "working"}', '550e8400-e29b-41d4-a716-446655440000', NULL, NULL, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440022', '厂区一机器人003', '{"model": "BOSHI-RB-03", "battery": 95, "status": "idle"}', '550e8400-e29b-41d4-a716-446655440000', NULL, NULL, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440023', '厂区一机器人004', '{"model": "BOSHI-RB-04", "battery": 90, "status": "idle"}', '550e8400-e29b-41d4-a716-446655440000', NULL, NULL, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440024', '厂区二机器人001', '{"model": "BOSHI-RB-05", "battery": 100, "status": "idle"}', '550e8400-e29b-41d4-a716-446655440001', NULL, NULL, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440025', '厂区二机器人002', '{"model": "BOSHI-RB-06", "battery": 88, "status": "working"}', '550e8400-e29b-41d4-a716-446655440001', NULL, NULL, NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入机器人-地图关联数据
-- 厂区一：4个机器人都关联到1个地图
INSERT INTO tb_robot_map (id, robot_id, map_id, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440501', '550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440010', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440502', '550e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440010', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440503', '550e8400-e29b-41d4-a716-446655440022', '550e8400-e29b-41d4-a716-446655440010', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440504', '550e8400-e29b-41d4-a716-446655440023', '550e8400-e29b-41d4-a716-446655440010', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440505', '550e8400-e29b-41d4-a716-446655440024', '550e8400-e29b-41d4-a716-446655440011', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440506', '550e8400-e29b-41d4-a716-446655440025', '550e8400-e29b-41d4-a716-446655440012', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例云台数据
INSERT INTO tb_gimbal (id, gimbal_name, map_id, enabled, ip_address, port, username, password, rtsp_main_url, rtsp_sub_url, channel, x_coordinate, y_coordinate, p_coordinate, t_coordinate, z_coordinate, f_coordinate, preview_url, control_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440030', '云台001', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.110', 554, 'admin', 'admin123', 'rtsp://192.168.1.110:554/stream/main', 'rtsp://192.168.1.110:554/stream/sub', 1, 198.6700, 134.2800, 0.0000, 0.0000, 0.0000, 0.0000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440031', '云台002', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.111', 8554, 'operator', 'securePass!', 'rtsp://192.168.1.111:8554/live/main', 'rtsp://192.168.1.111:8554/live/sub', 2, 456.8300, 312.5700, 5.0000, 2.5000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440032', '云台003', '550e8400-e29b-41d4-a716-446655440011', TRUE, '10.0.0.50', 554, 'guest', 'guest123', 'rtsp://10.0.0.50:554/main', 'rtsp://10.0.0.50:554/sub', 1, 150.0000, 200.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'operator', 'operator', FALSE),
('550e8400-e29b-41d4-a716-446655440033', '云台004', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.112', 554, 'admin', 'admin456', 'rtsp://192.168.1.112:554/stream/main', 'rtsp://192.168.1.112:554/stream/sub', 1, 680.1500, 320.4800, 10.0000, 5.0000, 2.0000, 1.0000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440034', '云台005', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.113', 8554, 'operator', 'operator123', 'rtsp://192.168.1.113:8554/live/main', 'rtsp://192.168.1.113:8554/live/sub', 2, 450.2300, 580.7600, 15.0000, 8.0000, 3.0000, 1.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440035', '云台006', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.114', 554, 'admin', 'admin789', 'rtsp://192.168.1.114:554/stream/main', 'rtsp://192.168.1.114:554/stream/sub', 1, 720.8900, 450.1200, 20.0000, 10.0000, 4.0000, 2.0000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440036', '云台007', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.115', 554, 'admin', 'admin000', 'rtsp://192.168.1.115:554/stream/main', 'rtsp://192.168.1.115:554/stream/sub', 1, 320.5600, 680.3400, 25.0000, 12.0000, 5.0000, 2.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440037', '云台008', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.116', 554, 'admin', 'admin001', 'rtsp://192.168.1.116:554/stream/main', 'rtsp://192.168.1.116:554/stream/sub', 1, 100.0000, 100.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440038', '云台009', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.117', 554, 'admin', 'admin002', 'rtsp://192.168.1.117:554/stream/main', 'rtsp://192.168.1.117:554/stream/sub', 1, 150.0000, 150.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440039', '云台010', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.118', 554, 'admin', 'admin003', 'rtsp://192.168.1.118:554/stream/main', 'rtsp://192.168.1.118:554/stream/sub', 1, 200.0000, 200.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544003a', '云台011', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.119', 554, 'admin', 'admin004', 'rtsp://192.168.1.119:554/stream/main', 'rtsp://192.168.1.119:554/stream/sub', 1, 250.0000, 250.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544003b', '云台012', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.120', 554, 'admin', 'admin005', 'rtsp://192.168.1.120:554/stream/main', 'rtsp://192.168.1.120:554/stream/sub', 1, 300.0000, 300.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544003c', '云台013', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.121', 554, 'admin', 'admin006', 'rtsp://192.168.1.121:554/stream/main', 'rtsp://192.168.1.121:554/stream/sub', 1, 350.0000, 350.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544003d', '云台014', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.122', 554, 'admin', 'admin007', 'rtsp://192.168.1.122:554/stream/main', 'rtsp://192.168.1.122:554/stream/sub', 1, 400.0000, 400.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544003e', '云台015', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.123', 554, 'admin', 'admin008', 'rtsp://192.168.1.123:554/stream/main', 'rtsp://192.168.1.123:554/stream/sub', 1, 450.0000, 450.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544003f', '云台016', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.124', 554, 'admin', 'admin009', 'rtsp://192.168.1.124:554/stream/main', 'rtsp://192.168.1.124:554/stream/sub', 1, 500.0000, 500.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440040', '云台017', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.125', 554, 'admin', 'admin010', 'rtsp://192.168.1.125:554/stream/main', 'rtsp://192.168.1.125:554/stream/sub', 1, 550.0000, 550.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440041', '云台018', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.126', 554, 'admin', 'admin011', 'rtsp://192.168.1.126:554/stream/main', 'rtsp://192.168.1.126:554/stream/sub', 1, 600.0000, 600.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440042', '云台019', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.127', 554, 'admin', 'admin012', 'rtsp://192.168.1.127:554/stream/main', 'rtsp://192.168.1.127:554/stream/sub', 1, 650.0000, 650.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440043', '云台020', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.128', 554, 'admin', 'admin013', 'rtsp://192.168.1.128:554/stream/main', 'rtsp://192.168.1.128:554/stream/sub', 1, 700.0000, 700.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440044', '云台021', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.129', 554, 'admin', 'admin014', 'rtsp://192.168.1.129:554/stream/main', 'rtsp://192.168.1.129:554/stream/sub', 1, 750.0000, 750.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440045', '云台022', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.130', 554, 'admin', 'admin015', 'rtsp://192.168.1.130:554/stream/main', 'rtsp://192.168.1.130:554/stream/sub', 1, 800.0000, 800.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440046', '云台023', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.131', 554, 'admin', 'admin016', 'rtsp://192.168.1.131:554/stream/main', 'rtsp://192.168.1.131:554/stream/sub', 1, 850.0000, 850.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440047', '云台024', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.132', 554, 'admin', 'admin017', 'rtsp://192.168.1.132:554/stream/main', 'rtsp://192.168.1.132:554/stream/sub', 1, 900.0000, 900.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440048', '云台025', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.133', 554, 'admin', 'admin018', 'rtsp://192.168.1.133:554/stream/main', 'rtsp://192.168.1.133:554/stream/sub', 1, 950.0000, 950.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440049', '云台026', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.134', 554, 'admin', 'admin019', 'rtsp://192.168.1.134:554/stream/main', 'rtsp://192.168.1.134:554/stream/sub', 1, 100.0000, 200.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004a', '云台027', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.135', 554, 'admin', 'admin020', 'rtsp://192.168.1.135:554/stream/main', 'rtsp://192.168.1.135:554/stream/sub', 1, 150.0000, 250.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004b', '云台028', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.136', 554, 'admin', 'admin021', 'rtsp://192.168.1.136:554/stream/main', 'rtsp://192.168.1.136:554/stream/sub', 1, 200.0000, 300.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004c', '云台029', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.137', 554, 'admin', 'admin022', 'rtsp://192.168.1.137:554/stream/main', 'rtsp://192.168.1.137:554/stream/sub', 1, 250.0000, 350.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004d', '云台030', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.138', 554, 'admin', 'admin023', 'rtsp://192.168.1.138:554/stream/main', 'rtsp://192.168.1.138:554/stream/sub', 1, 300.0000, 400.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004e', '云台031', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.139', 554, 'admin', 'admin024', 'rtsp://192.168.1.139:554/stream/main', 'rtsp://192.168.1.139:554/stream/sub', 1, 350.0000, 450.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004f', '云台032', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.140', 554, 'admin', 'admin025', 'rtsp://192.168.1.140:554/stream/main', 'rtsp://192.168.1.140:554/stream/sub', 1, 400.0000, 500.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440050', '云台033', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.141', 554, 'admin', 'admin026', 'rtsp://192.168.1.141:554/stream/main', 'rtsp://192.168.1.141:554/stream/sub', 1, 450.0000, 550.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440051', '云台034', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.142', 554, 'admin', 'admin027', 'rtsp://192.168.1.142:554/stream/main', 'rtsp://192.168.1.142:554/stream/sub', 1, 500.0000, 600.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440052', '云台035', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.143', 554, 'admin', 'admin028', 'rtsp://192.168.1.143:554/stream/main', 'rtsp://192.168.1.143:554/stream/sub', 1, 550.0000, 650.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440053', '云台036', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.144', 554, 'admin', 'admin029', 'rtsp://192.168.1.144:554/stream/main', 'rtsp://192.168.1.144:554/stream/sub', 1, 600.0000, 700.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440054', '云台037', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.145', 554, 'admin', 'admin030', 'rtsp://192.168.1.145:554/stream/main', 'rtsp://192.168.1.145:554/stream/sub', 1, 650.0000, 750.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440055', '云台038', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.146', 554, 'admin', 'admin031', 'rtsp://192.168.1.146:554/stream/main', 'rtsp://192.168.1.146:554/stream/sub', 1, 700.0000, 800.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440056', '云台039', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.147', 554, 'admin', 'admin032', 'rtsp://192.168.1.147:554/stream/main', 'rtsp://192.168.1.147:554/stream/sub', 1, 750.0000, 850.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440057', '云台040', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.148', 554, 'admin', 'admin033', 'rtsp://192.168.1.148:554/stream/main', 'rtsp://192.168.1.148:554/stream/sub', 1, 800.0000, 900.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440058', '云台041', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.149', 554, 'admin', 'admin034', 'rtsp://192.168.1.149:554/stream/main', 'rtsp://192.168.1.149:554/stream/sub', 1, 850.0000, 950.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440059', '云台042', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.150', 554, 'admin', 'admin035', 'rtsp://192.168.1.150:554/stream/main', 'rtsp://192.168.1.150:554/stream/sub', 1, 50.0000, 150.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005a', '云台043', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.151', 554, 'admin', 'admin036', 'rtsp://192.168.1.151:554/stream/main', 'rtsp://192.168.1.151:554/stream/sub', 1, 100.0000, 250.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005b', '云台044', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.152', 554, 'admin', 'admin037', 'rtsp://192.168.1.152:554/stream/main', 'rtsp://192.168.1.152:554/stream/sub', 1, 150.0000, 350.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005c', '云台045', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.153', 554, 'admin', 'admin038', 'rtsp://192.168.1.153:554/stream/main', 'rtsp://192.168.1.153:554/stream/sub', 1, 200.0000, 450.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005d', '云台046', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.154', 554, 'admin', 'admin039', 'rtsp://192.168.1.154:554/stream/main', 'rtsp://192.168.1.154:554/stream/sub', 1, 250.0000, 550.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005e', '云台047', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.155', 554, 'admin', 'admin040', 'rtsp://192.168.1.155:554/stream/main', 'rtsp://192.168.1.155:554/stream/sub', 1, 300.0000, 650.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005f', '云台048', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.156', 554, 'admin', 'admin041', 'rtsp://192.168.1.156:554/stream/main', 'rtsp://192.168.1.156:554/stream/sub', 1, 350.0000, 750.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440060', '云台049', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.157', 554, 'admin', 'admin042', 'rtsp://192.168.1.157:554/stream/main', 'rtsp://192.168.1.157:554/stream/sub', 1, 400.0000, 850.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440061', '云台050', '550e8400-e29b-41d4-a716-446655440010', TRUE, '192.168.1.158', 554, 'admin', 'admin043', 'rtsp://192.168.1.158:554/stream/main', 'rtsp://192.168.1.158:554/stream/sub', 1, 450.0000, 950.0000, 0.0000, 0.0000, 1.0000, 0.5000, NULL, NULL, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台任务数据
INSERT INTO tb_gimbaltask (id, task_name, gimbal_id, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440040', '云台任务-A', '550e8400-e29b-41d4-a716-446655440030', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440041', '云台任务-B', '550e8400-e29b-41d4-a716-446655440031', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440042', '云台任务-C', '550e8400-e29b-41d4-a716-446655440032', NOW(), NOW(), 'operator', 'operator', FALSE),
('550e8400-e29b-41d4-a716-446655440043', '云台任务-D', '550e8400-e29b-41d4-a716-446655440033', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440044', '云台任务-E', '550e8400-e29b-41d4-a716-446655440034', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440045', '云台任务-F', '550e8400-e29b-41d4-a716-446655440035', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440046', '云台任务-G', '550e8400-e29b-41d4-a716-446655440036', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440047', '云台任务-H', '550e8400-e29b-41d4-a716-446655440037', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440048', '云台任务-I', '550e8400-e29b-41d4-a716-446655440038', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440049', '云台任务-J', '550e8400-e29b-41d4-a716-446655440039', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004a', '云台任务-K', '550e8400-e29b-41d4-a716-44665544003a', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004b', '云台任务-L', '550e8400-e29b-41d4-a716-44665544003b', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004c', '云台任务-M', '550e8400-e29b-41d4-a716-44665544003c', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004d', '云台任务-N', '550e8400-e29b-41d4-a716-44665544003d', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004e', '云台任务-O', '550e8400-e29b-41d4-a716-44665544003e', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544004f', '云台任务-P', '550e8400-e29b-41d4-a716-44665544003f', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440050', '云台任务-Q', '550e8400-e29b-41d4-a716-446655440040', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440051', '云台任务-R', '550e8400-e29b-41d4-a716-446655440041', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440052', '云台任务-S', '550e8400-e29b-41d4-a716-446655440042', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440053', '云台任务-T', '550e8400-e29b-41d4-a716-446655440043', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440054', '云台任务-U', '550e8400-e29b-41d4-a716-446655440044', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440055', '云台任务-V', '550e8400-e29b-41d4-a716-446655440045', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440056', '云台任务-W', '550e8400-e29b-41d4-a716-446655440046', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440057', '云台任务-X', '550e8400-e29b-41d4-a716-446655440047', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440058', '云台任务-Y', '550e8400-e29b-41d4-a716-446655440048', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440059', '云台任务-Z', '550e8400-e29b-41d4-a716-446655440049', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005a', '云台任务-AA', '550e8400-e29b-41d4-a716-44665544004a', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005b', '云台任务-AB', '550e8400-e29b-41d4-a716-44665544004b', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005c', '云台任务-AC', '550e8400-e29b-41d4-a716-44665544004c', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005d', '云台任务-AD', '550e8400-e29b-41d4-a716-44665544004d', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005e', '云台任务-AE', '550e8400-e29b-41d4-a716-44665544004e', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544005f', '云台任务-AF', '550e8400-e29b-41d4-a716-44665544004f', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440060', '云台任务-AG', '550e8400-e29b-41d4-a716-446655440050', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440061', '云台任务-AH', '550e8400-e29b-41d4-a716-446655440051', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440062', '云台任务-AI', '550e8400-e29b-41d4-a716-446655440052', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440063', '云台任务-AJ', '550e8400-e29b-41d4-a716-446655440053', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440064', '云台任务-AK', '550e8400-e29b-41d4-a716-446655440054', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440065', '云台任务-AL', '550e8400-e29b-41d4-a716-446655440055', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440066', '云台任务-AM', '550e8400-e29b-41d4-a716-446655440056', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440067', '云台任务-AN', '550e8400-e29b-41d4-a716-446655440057', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440068', '云台任务-AO', '550e8400-e29b-41d4-a716-446655440058', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440069', '云台任务-AP', '550e8400-e29b-41d4-a716-446655440059', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544006a', '云台任务-AQ', '550e8400-e29b-41d4-a716-44665544005a', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544006b', '云台任务-AR', '550e8400-e29b-41d4-a716-44665544005b', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544006c', '云台任务-AS', '550e8400-e29b-41d4-a716-44665544005c', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544006d', '云台任务-AT', '550e8400-e29b-41d4-a716-44665544005d', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544006e', '云台任务-AU', '550e8400-e29b-41d4-a716-44665544005e', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-44665544006f', '云台任务-AV', '550e8400-e29b-41d4-a716-44665544005f', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440070', '云台任务-AW', '550e8400-e29b-41d4-a716-446655440060', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440071', '云台任务-AX', '550e8400-e29b-41d4-a716-446655440061', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台预设点数据
-- 插入示例云台预设点数据（每个云台至少3个预设点，优化为单行格式）
INSERT INTO tb_gimbal_preset_point (id, preset_name, gimbal_id, p_coordinate, t_coordinate, z_coordinate, f_coordinate, aperture, shutter, backlight_compensation, wide_dynamic, strong_light_suppression, fill_light, image_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('750e8400-e29b-41d4-a716-446655440030', '预设点-全景', '550e8400-e29b-41d4-a716-446655440030', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal001_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440031', '预设点-监控', '550e8400-e29b-41d4-a716-446655440030', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal001_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440032', '预设点-定点', '550e8400-e29b-41d4-a716-446655440030', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal001_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440033', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440031', 0.0000, 0.0000, 4.0000, 0.8000, 35, 15, FALSE, TRUE, TRUE, TRUE, '/media/preset/gimbal002_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440034', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440031', -10.0000, 5.0000, 2.0000, 1.0000, 50, 50, TRUE, FALSE, TRUE, FALSE, '/media/preset/gimbal002_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440035', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440031', 15.0000, 8.0000, 3.0000, 1.5000, 60, 40, TRUE, TRUE, FALSE, TRUE, '/media/preset/gimbal002_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440036', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440032', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal003_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440037', '预设点-中心', '550e8400-e29b-41d4-a716-446655440032', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal003_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440038', '预设点-角落', '550e8400-e29b-41d4-a716-446655440032', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal003_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440039', '预设点-入口', '550e8400-e29b-41d4-a716-446655440033', 10.0000, 5.0000, 2.0000, 1.0000, 50, 50, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal004_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544003a', '预设点-出口', '550e8400-e29b-41d4-a716-446655440033', -10.0000, 5.0000, 2.0000, 1.0000, 50, 50, TRUE, FALSE, TRUE, FALSE, '/media/preset/gimbal004_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544003b', '预设点-全景', '550e8400-e29b-41d4-a716-446655440033', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal004_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544003c', '预设点-监控', '550e8400-e29b-41d4-a716-446655440034', 15.0000, 8.0000, 3.0000, 1.5000, 60, 40, TRUE, TRUE, TRUE, TRUE, '/media/preset/gimbal005_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544003d', '预设点-定点', '550e8400-e29b-41d4-a716-446655440034', -15.0000, 8.0000, 3.0000, 1.5000, 60, 40, FALSE, TRUE, FALSE, TRUE, '/media/preset/gimbal005_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544003e', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440034', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal005_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544003f', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440035', 20.0000, 10.0000, 4.0000, 2.0000, 70, 30, TRUE, TRUE, TRUE, TRUE, '/media/preset/gimbal006_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440040', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440035', 25.0000, 12.0000, 5.0000, 2.5000, 45, 25, FALSE, FALSE, TRUE, FALSE, '/media/preset/gimbal006_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440041', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440035', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal006_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440042', '预设点-中心', '550e8400-e29b-41d4-a716-446655440036', 25.0000, 12.0000, 5.0000, 2.5000, 55, 35, TRUE, TRUE, FALSE, TRUE, '/media/preset/gimbal007_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440043', '预设点-角落', '550e8400-e29b-41d4-a716-446655440036', -25.0000, 12.0000, 5.0000, 2.5000, 55, 35, TRUE, FALSE, TRUE, FALSE, '/media/preset/gimbal007_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440044', '预设点-入口', '550e8400-e29b-41d4-a716-446655440036', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal007_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440045', '预设点-全景', '550e8400-e29b-41d4-a716-446655440037', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal008_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440046', '预设点-监控', '550e8400-e29b-41d4-a716-446655440037', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal008_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440047', '预设点-定点', '550e8400-e29b-41d4-a716-446655440037', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal008_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440048', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440038', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal009_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440049', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440038', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal009_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544004a', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440038', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal009_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544004b', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440039', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal010_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544004c', '预设点-中心', '550e8400-e29b-41d4-a716-446655440039', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal010_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544004d', '预设点-角落', '550e8400-e29b-41d4-a716-446655440039', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal010_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544004e', '预设点-入口', '550e8400-e29b-41d4-a716-44665544003a', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal011_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544004f', '预设点-出口', '550e8400-e29b-41d4-a716-44665544003a', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal011_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440050', '预设点-全景', '550e8400-e29b-41d4-a716-44665544003a', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal011_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440051', '预设点-监控', '550e8400-e29b-41d4-a716-44665544003b', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal012_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440052', '预设点-定点', '550e8400-e29b-41d4-a716-44665544003b', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal012_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440053', '预设点-东侧', '550e8400-e29b-41d4-a716-44665544003b', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal012_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440054', '预设点-西侧', '550e8400-e29b-41d4-a716-44665544003c', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal013_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440055', '预设点-南侧', '550e8400-e29b-41d4-a716-44665544003c', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal013_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440056', '预设点-北侧', '550e8400-e29b-41d4-a716-44665544003c', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal013_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440057', '预设点-中心', '550e8400-e29b-41d4-a716-44665544003d', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal014_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440058', '预设点-角落', '550e8400-e29b-41d4-a716-44665544003d', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal014_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440059', '预设点-入口', '550e8400-e29b-41d4-a716-44665544003d', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal014_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544005a', '预设点-出口', '550e8400-e29b-41d4-a716-44665544003e', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal015_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544005b', '预设点-全景', '550e8400-e29b-41d4-a716-44665544003e', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal015_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544005c', '预设点-监控', '550e8400-e29b-41d4-a716-44665544003e', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal015_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544005d', '预设点-定点', '550e8400-e29b-41d4-a716-44665544003f', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal016_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544005e', '预设点-东侧', '550e8400-e29b-41d4-a716-44665544003f', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal016_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544005f', '预设点-西侧', '550e8400-e29b-41d4-a716-44665544003f', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal016_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440060', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440040', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal017_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440061', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440040', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal017_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440062', '预设点-中心', '550e8400-e29b-41d4-a716-446655440040', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal017_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440063', '预设点-角落', '550e8400-e29b-41d4-a716-446655440041', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal018_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440064', '预设点-入口', '550e8400-e29b-41d4-a716-446655440041', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal018_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440065', '预设点-出口', '550e8400-e29b-41d4-a716-446655440041', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal018_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440066', '预设点-全景', '550e8400-e29b-41d4-a716-446655440042', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal019_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440067', '预设点-监控', '550e8400-e29b-41d4-a716-446655440042', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal019_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440068', '预设点-定点', '550e8400-e29b-41d4-a716-446655440042', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal019_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440069', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440043', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal020_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544006a', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440043', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal020_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544006b', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440043', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal020_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544006c', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440044', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal021_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544006d', '预设点-中心', '550e8400-e29b-41d4-a716-446655440044', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal021_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544006e', '预设点-角落', '550e8400-e29b-41d4-a716-446655440044', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal021_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544006f', '预设点-入口', '550e8400-e29b-41d4-a716-446655440045', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal022_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440070', '预设点-出口', '550e8400-e29b-41d4-a716-446655440045', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal022_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440071', '预设点-全景', '550e8400-e29b-41d4-a716-446655440045', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal022_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440072', '预设点-监控', '550e8400-e29b-41d4-a716-446655440046', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal023_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440073', '预设点-定点', '550e8400-e29b-41d4-a716-446655440046', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal023_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440074', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440046', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal023_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440075', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440047', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal024_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440076', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440047', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal024_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440077', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440047', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal024_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440078', '预设点-中心', '550e8400-e29b-41d4-a716-446655440048', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal025_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440079', '预设点-角落', '550e8400-e29b-41d4-a716-446655440048', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal025_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544007a', '预设点-入口', '550e8400-e29b-41d4-a716-446655440048', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal025_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544007b', '预设点-出口', '550e8400-e29b-41d4-a716-446655440049', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal026_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544007c', '预设点-全景', '550e8400-e29b-41d4-a716-446655440049', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal026_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544007d', '预设点-监控', '550e8400-e29b-41d4-a716-446655440049', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal026_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544007e', '预设点-定点', '550e8400-e29b-41d4-a716-44665544004a', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal027_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544007f', '预设点-东侧', '550e8400-e29b-41d4-a716-44665544004a', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal027_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440080', '预设点-西侧', '550e8400-e29b-41d4-a716-44665544004a', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal027_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440081', '预设点-南侧', '550e8400-e29b-41d4-a716-44665544004b', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal028_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440082', '预设点-北侧', '550e8400-e29b-41d4-a716-44665544004b', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal028_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440083', '预设点-中心', '550e8400-e29b-41d4-a716-44665544004b', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal028_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440084', '预设点-角落', '550e8400-e29b-41d4-a716-44665544004c', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal029_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440085', '预设点-入口', '550e8400-e29b-41d4-a716-44665544004c', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal029_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440086', '预设点-出口', '550e8400-e29b-41d4-a716-44665544004c', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal029_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440087', '预设点-全景', '550e8400-e29b-41d4-a716-44665544004d', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal030_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440088', '预设点-监控', '550e8400-e29b-41d4-a716-44665544004d', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal030_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440089', '预设点-定点', '550e8400-e29b-41d4-a716-44665544004d', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal030_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544008a', '预设点-东侧', '550e8400-e29b-41d4-a716-44665544004e', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal031_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544008b', '预设点-西侧', '550e8400-e29b-41d4-a716-44665544004e', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal031_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544008c', '预设点-南侧', '550e8400-e29b-41d4-a716-44665544004e', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal031_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544008d', '预设点-北侧', '550e8400-e29b-41d4-a716-44665544004f', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal032_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544008e', '预设点-中心', '550e8400-e29b-41d4-a716-44665544004f', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal032_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544008f', '预设点-角落', '550e8400-e29b-41d4-a716-44665544004f', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal032_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440090', '预设点-入口', '550e8400-e29b-41d4-a716-446655440050', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal033_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440091', '预设点-出口', '550e8400-e29b-41d4-a716-446655440050', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal033_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440092', '预设点-全景', '550e8400-e29b-41d4-a716-446655440050', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal033_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440093', '预设点-监控', '550e8400-e29b-41d4-a716-446655440051', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal034_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440094', '预设点-定点', '550e8400-e29b-41d4-a716-446655440051', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal034_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440095', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440051', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal034_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440096', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440052', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal035_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440097', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440052', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal035_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440098', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440052', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal035_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440099', '预设点-中心', '550e8400-e29b-41d4-a716-446655440053', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal036_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544009a', '预设点-角落', '550e8400-e29b-41d4-a716-446655440053', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal036_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544009b', '预设点-入口', '550e8400-e29b-41d4-a716-446655440053', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal036_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544009c', '预设点-出口', '550e8400-e29b-41d4-a716-446655440054', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal037_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544009d', '预设点-全景', '550e8400-e29b-41d4-a716-446655440054', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal037_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544009e', '预设点-监控', '550e8400-e29b-41d4-a716-446655440054', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal037_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-44665544009f', '预设点-定点', '550e8400-e29b-41d4-a716-446655440055', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal038_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a0', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440055', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal038_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a1', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440055', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal038_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a2', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440056', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal039_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a3', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440056', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal039_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a4', '预设点-中心', '550e8400-e29b-41d4-a716-446655440056', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal039_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a5', '预设点-角落', '550e8400-e29b-41d4-a716-446655440057', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal040_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a6', '预设点-入口', '550e8400-e29b-41d4-a716-446655440057', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal040_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a7', '预设点-出口', '550e8400-e29b-41d4-a716-446655440057', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal040_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a8', '预设点-全景', '550e8400-e29b-41d4-a716-446655440058', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal041_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400a9', '预设点-监控', '550e8400-e29b-41d4-a716-446655440058', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal041_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400aa', '预设点-定点', '550e8400-e29b-41d4-a716-446655440058', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal041_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400ab', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440059', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal042_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400ac', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440059', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal042_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400ad', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440059', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal042_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400ae', '预设点-北侧', '550e8400-e29b-41d4-a716-44665544005a', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal043_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400af', '预设点-中心', '550e8400-e29b-41d4-a716-44665544005a', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal043_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b0', '预设点-角落', '550e8400-e29b-41d4-a716-44665544005a', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal043_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b1', '预设点-入口', '550e8400-e29b-41d4-a716-44665544005b', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal044_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b2', '预设点-出口', '550e8400-e29b-41d4-a716-44665544005b', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal044_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b3', '预设点-全景', '550e8400-e29b-41d4-a716-44665544005b', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal044_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b4', '预设点-监控', '550e8400-e29b-41d4-a716-44665544005c', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal045_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b5', '预设点-定点', '550e8400-e29b-41d4-a716-44665544005c', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal045_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b6', '预设点-东侧', '550e8400-e29b-41d4-a716-44665544005c', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal045_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b7', '预设点-西侧', '550e8400-e29b-41d4-a716-44665544005d', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal046_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b8', '预设点-南侧', '550e8400-e29b-41d4-a716-44665544005d', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal046_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400b9', '预设点-北侧', '550e8400-e29b-41d4-a716-44665544005d', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal046_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400ba', '预设点-中心', '550e8400-e29b-41d4-a716-44665544005e', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal047_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400bb', '预设点-角落', '550e8400-e29b-41d4-a716-44665544005e', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal047_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400bc', '预设点-入口', '550e8400-e29b-41d4-a716-44665544005e', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal047_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400bd', '预设点-出口', '550e8400-e29b-41d4-a716-44665544005f', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal048_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400be', '预设点-全景', '550e8400-e29b-41d4-a716-44665544005f', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal048_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400bf', '预设点-监控', '550e8400-e29b-41d4-a716-44665544005f', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal048_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400c0', '预设点-定点', '550e8400-e29b-41d4-a716-446655440060', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal049_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400c1', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440060', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal049_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400c2', '预设点-西侧', '550e8400-e29b-41d4-a716-446655440060', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal049_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400c3', '预设点-南侧', '550e8400-e29b-41d4-a716-446655440061', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal050_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400c4', '预设点-北侧', '550e8400-e29b-41d4-a716-446655440061', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal050_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-4466554400c5', '预设点-中心', '550e8400-e29b-41d4-a716-446655440061', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal050_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台巡检项目数据（优化为单行格式）
INSERT INTO tb_gimbal_inspection_project (id, task_name, gimbaltask_id, sort_order, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('650e8400-e29b-41d4-a716-446655440040', '全景拍摄项目', '550e8400-e29b-41d4-a716-446655440040', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440041', '监控录像项目', '550e8400-e29b-41d4-a716-446655440041', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440042', '定点观察项目', '550e8400-e29b-41d4-a716-446655440042', 0, NOW(), NOW(), 'operator', 'operator', FALSE),
('650e8400-e29b-41d4-a716-446655440043', '全方位监控项目', '550e8400-e29b-41d4-a716-446655440043', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440044', '区域巡检项目', '550e8400-e29b-41d4-a716-446655440044', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440045', '重点区域监控项目', '550e8400-e29b-41d4-a716-446655440045', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440046', '出入口监控项目', '550e8400-e29b-41d4-a716-446655440046', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440047', '夜间监控项目', '550e8400-e29b-41d4-a716-446655440040', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440048', '日间巡检项目', '550e8400-e29b-41d4-a716-446655440040', 2, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440049', '安全监控项目', '550e8400-e29b-41d4-a716-446655440041', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544004a', '环境监测项目', '550e8400-e29b-41d4-a716-446655440041', 2, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544004b', '设备巡检项目', '550e8400-e29b-41d4-a716-446655440042', 1, NOW(), NOW(), 'operator', 'operator', FALSE),
('650e8400-e29b-41d4-a716-44665544004c', '区域扫描项目', '550e8400-e29b-41d4-a716-446655440043', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544004d', '重点监控项目', '550e8400-e29b-41d4-a716-446655440043', 2, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544004e', '定时巡检项目', '550e8400-e29b-41d4-a716-446655440044', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544004f', '异常检测项目', '550e8400-e29b-41d4-a716-446655440045', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440050', '常规巡检项目', '550e8400-e29b-41d4-a716-446655440046', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440051', '特殊区域项目', '550e8400-e29b-41d4-a716-446655440047', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440052', '关键点位项目', '550e8400-e29b-41d4-a716-446655440047', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440053', '全面监控项目', '550e8400-e29b-41d4-a716-446655440048', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440054', '细节观察项目', '550e8400-e29b-41d4-a716-446655440048', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440055', '快速巡检项目', '550e8400-e29b-41d4-a716-446655440049', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440056', '深度巡检项目', '550e8400-e29b-41d4-a716-446655440049', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440057', '标准巡检项目', '550e8400-e29b-41d4-a716-44665544004a', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440058', '扩展巡检项目', '550e8400-e29b-41d4-a716-44665544004a', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440059', '基础监控项目', '550e8400-e29b-41d4-a716-44665544004b', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544005a', '常规巡检项目', '550e8400-e29b-41d4-a716-44665544004c', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544005b', '标准监控项目', '550e8400-e29b-41d4-a716-44665544004d', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544005c', '日常巡检项目', '550e8400-e29b-41d4-a716-44665544004e', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544005d', '定期检查项目', '550e8400-e29b-41d4-a716-44665544004f', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544005e', '系统监控项目', '550e8400-e29b-41d4-a716-446655440050', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544005f', '安全巡检项目', '550e8400-e29b-41d4-a716-446655440051', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440060', '设备检查项目', '550e8400-e29b-41d4-a716-446655440052', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440061', '环境监控项目', '550e8400-e29b-41d4-a716-446655440053', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440062', '区域检查项目', '550e8400-e29b-41d4-a716-446655440054', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440063', '重点监控项目', '550e8400-e29b-41d4-a716-446655440055', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440064', '全面检查项目', '550e8400-e29b-41d4-a716-446655440056', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440065', '细节监控项目', '550e8400-e29b-41d4-a716-446655440057', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440066', '快速检查项目', '550e8400-e29b-41d4-a716-446655440058', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440067', '深度监控项目', '550e8400-e29b-41d4-a716-446655440059', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440068', '扩展检查项目', '550e8400-e29b-41d4-a716-44665544005a', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440069', '综合巡检项目', '550e8400-e29b-41d4-a716-44665544005b', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544006a', '专项监控项目', '550e8400-e29b-41d4-a716-44665544005c', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544006b', '定期巡检项目', '550e8400-e29b-41d4-a716-44665544005d', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544006c', '系统检查项目', '550e8400-e29b-41d4-a716-44665544005e', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544006d', '安全检查项目', '550e8400-e29b-41d4-a716-44665544005f', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544006e', '设备监控项目', '550e8400-e29b-41d4-a716-446655440060', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-44665544006f', '环境检查项目', '550e8400-e29b-41d4-a716-446655440061', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440070', '区域监控项目', '550e8400-e29b-41d4-a716-446655440062', 0, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440071', '重点检查项目', '550e8400-e29b-41d4-a716-446655440063', 0, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台巡检项目-预设点关联数据（优化为单行格式）
INSERT INTO tb_gimbal_inspection_project_preset_point (id, inspection_project_id, preset_point_id, detection_type, video_duration, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('850e8400-e29b-41d4-a716-446655440040', '650e8400-e29b-41d4-a716-446655440040', '750e8400-e29b-41d4-a716-446655440030', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440041', '650e8400-e29b-41d4-a716-446655440040', '750e8400-e29b-41d4-a716-446655440031', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440042', '650e8400-e29b-41d4-a716-446655440041', '750e8400-e29b-41d4-a716-446655440033', '可见光视频', 60, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440043', '650e8400-e29b-41d4-a716-446655440042', '750e8400-e29b-41d4-a716-446655440036', '热成像图片', NULL, NOW(), NOW(), 'operator', 'operator', FALSE),
('850e8400-e29b-41d4-a716-446655440044', '650e8400-e29b-41d4-a716-446655440043', '750e8400-e29b-41d4-a716-446655440039', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440045', '650e8400-e29b-41d4-a716-446655440043', '750e8400-e29b-41d4-a716-44665544003a', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440046', '650e8400-e29b-41d4-a716-446655440044', '750e8400-e29b-41d4-a716-44665544003c', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440047', '650e8400-e29b-41d4-a716-446655440044', '750e8400-e29b-41d4-a716-44665544003d', '可见光视频', 45, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440048', '650e8400-e29b-41d4-a716-446655440045', '750e8400-e29b-41d4-a716-44665544003f', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440049', '650e8400-e29b-41d4-a716-446655440045', '750e8400-e29b-41d4-a716-446655440040', '热成像视频', 60, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440050', '650e8400-e29b-41d4-a716-446655440046', '750e8400-e29b-41d4-a716-446655440042', '可见光视频', 45, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440051', '650e8400-e29b-41d4-a716-446655440046', '750e8400-e29b-41d4-a716-446655440043', '热成像视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440052', '650e8400-e29b-41d4-a716-446655440047', '750e8400-e29b-41d4-a716-446655440032', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440053', '650e8400-e29b-41d4-a716-446655440047', '750e8400-e29b-41d4-a716-446655440034', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440054', '650e8400-e29b-41d4-a716-446655440047', '750e8400-e29b-41d4-a716-446655440035', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440055', '650e8400-e29b-41d4-a716-446655440048', '750e8400-e29b-41d4-a716-446655440036', '可见光视频', 60, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440056', '650e8400-e29b-41d4-a716-446655440049', '750e8400-e29b-41d4-a716-446655440038', '可见光视频', 45, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440057', '650e8400-e29b-41d4-a716-44665544004a', '750e8400-e29b-41d4-a716-44665544003b', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440058', '650e8400-e29b-41d4-a716-44665544004b', '750e8400-e29b-41d4-a716-44665544003d', '热成像图片', NULL, NOW(), NOW(), 'operator', 'operator', FALSE),
('850e8400-e29b-41d4-a716-446655440059', '650e8400-e29b-41d4-a716-44665544004c', '750e8400-e29b-41d4-a716-44665544003f', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544005a', '650e8400-e29b-41d4-a716-44665544004d', '750e8400-e29b-41d4-a716-446655440041', '热成像视频', 45, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544005b', '650e8400-e29b-41d4-a716-44665544004e', '750e8400-e29b-41d4-a716-446655440043', '可见光视频', 60, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544005c', '650e8400-e29b-41d4-a716-44665544004f', '750e8400-e29b-41d4-a716-446655440045', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544005d', '650e8400-e29b-41d4-a716-446655440050', '750e8400-e29b-41d4-a716-446655440047', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544005e', '650e8400-e29b-41d4-a716-446655440051', '750e8400-e29b-41d4-a716-446655440049', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544005f', '650e8400-e29b-41d4-a716-446655440052', '750e8400-e29b-41d4-a716-44665544004b', '热成像视频', 60, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440060', '650e8400-e29b-41d4-a716-446655440053', '750e8400-e29b-41d4-a716-44665544004d', '可见光视频', 45, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440061', '650e8400-e29b-41d4-a716-446655440054', '750e8400-e29b-41d4-a716-44665544004f', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440062', '650e8400-e29b-41d4-a716-446655440055', '750e8400-e29b-41d4-a716-446655440051', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440063', '650e8400-e29b-41d4-a716-446655440056', '750e8400-e29b-41d4-a716-446655440053', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440064', '650e8400-e29b-41d4-a716-446655440057', '750e8400-e29b-41d4-a716-446655440055', '热成像视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440065', '650e8400-e29b-41d4-a716-446655440058', '750e8400-e29b-41d4-a716-446655440057', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440066', '650e8400-e29b-41d4-a716-446655440059', '750e8400-e29b-41d4-a716-446655440051', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440067', '650e8400-e29b-41d4-a716-44665544005a', '750e8400-e29b-41d4-a716-446655440054', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440068', '650e8400-e29b-41d4-a716-44665544005b', '750e8400-e29b-41d4-a716-446655440057', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440069', '650e8400-e29b-41d4-a716-44665544005c', '750e8400-e29b-41d4-a716-44665544005a', '可见光视频', 60, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544006a', '650e8400-e29b-41d4-a716-44665544005d', '750e8400-e29b-41d4-a716-44665544005c', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544006b', '650e8400-e29b-41d4-a716-44665544005e', '750e8400-e29b-41d4-a716-44665544005e', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544006c', '650e8400-e29b-41d4-a716-44665544005f', '750e8400-e29b-41d4-a716-446655440030', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544006d', '650e8400-e29b-41d4-a716-446655440060', '750e8400-e29b-41d4-a716-446655440032', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544006e', '650e8400-e29b-41d4-a716-446655440061', '750e8400-e29b-41d4-a716-446655440034', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544006f', '650e8400-e29b-41d4-a716-446655440062', '750e8400-e29b-41d4-a716-446655440036', '可见光视频', 45, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440070', '650e8400-e29b-41d4-a716-446655440063', '750e8400-e29b-41d4-a716-446655440038', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440071', '650e8400-e29b-41d4-a716-446655440064', '750e8400-e29b-41d4-a716-44665544003a', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440072', '650e8400-e29b-41d4-a716-446655440065', '750e8400-e29b-41d4-a716-44665544003c', '可见光视频', 45, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440073', '650e8400-e29b-41d4-a716-446655440066', '750e8400-e29b-41d4-a716-44665544003e', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440074', '650e8400-e29b-41d4-a716-446655440067', '750e8400-e29b-41d4-a716-446655440040', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440075', '650e8400-e29b-41d4-a716-446655440068', '750e8400-e29b-41d4-a716-446655440042', '可见光视频', 60, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440076', '650e8400-e29b-41d4-a716-446655440069', '750e8400-e29b-41d4-a716-446655440044', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440077', '650e8400-e29b-41d4-a716-44665544006a', '750e8400-e29b-41d4-a716-446655440046', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440078', '650e8400-e29b-41d4-a716-44665544006b', '750e8400-e29b-41d4-a716-446655440048', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440079', '650e8400-e29b-41d4-a716-44665544006c', '750e8400-e29b-41d4-a716-44665544004a', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544007a', '650e8400-e29b-41d4-a716-44665544006d', '750e8400-e29b-41d4-a716-44665544004c', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544007b', '650e8400-e29b-41d4-a716-44665544006e', '750e8400-e29b-41d4-a716-44665544004e', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544007c', '650e8400-e29b-41d4-a716-44665544006f', '750e8400-e29b-41d4-a716-446655440050', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544007d', '650e8400-e29b-41d4-a716-446655440070', '750e8400-e29b-41d4-a716-446655440052', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-44665544007e', '650e8400-e29b-41d4-a716-446655440071', '750e8400-e29b-41d4-a716-446655440054', '可见光视频', 45, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台日程数据
INSERT INTO tb_gimbalschedule (id, gimbaltask_id, schedule_name, start_date, end_date, enabled, cycle_type, cycle_config, time_mode, time_config, time_display_start, time_display_end, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440040', '云台1每天巡检', '2025-01-01', '2025-12-31', TRUE, 'daily', NULL, 'custom', '{"customTimes": ["08:00", "12:00", "18:00"]}', '08:00:00', '18:00:00', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440051', '550e8400-e29b-41d4-a716-446655440041', '云台2间隔巡检', '2025-01-01', '2025-12-31', TRUE, 'daily', NULL, 'interval', '{"intervalTimeRange": ["08:00", "18:00"], "intervalMinutes": 30}', '08:00:00', '18:00:00', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440052', '550e8400-e29b-41d4-a716-446655440042', '云台3每周巡检', '2025-01-01', '2025-12-31', TRUE, 'weekly', '{"selectedWeeks": [1, 3, 5]}', 'custom', '{"customTimes": ["09:00", "15:00"]}', '09:00:00', '15:00:00', NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例云台记录数据
INSERT INTO tb_gimbalhistory (id, project_preset_point_id, record_data, media_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440060', '850e8400-e29b-41d4-a716-446655440040', '{"angle": {"pan": 0, "tilt": 0, "zoom": 1}, "status": "completed", "quality": "high"}', '/media/gimbal/2024/01/panorama_001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440061', '850e8400-e29b-41d4-a716-446655440042', '{"angle": {"pan": 45, "tilt": -30, "zoom": 2}, "status": "completed", "duration": 30}', '/media/gimbal/2024/01/monitor_001.mp4', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440062', '850e8400-e29b-41d4-a716-446655440043', '{"angle": {"pan": 90, "tilt": 0, "zoom": 5}, "status": "completed", "quality": "medium"}', '/media/gimbal/2024/01/observation_001.jpg', NOW(), NOW(), 'operator', 'operator', FALSE),
('550e8400-e29b-41d4-a716-446655440063', '850e8400-e29b-41d4-a716-446655440041', '{"angle": {"pan": 180, "tilt": 10, "zoom": 1}, "status": "completed", "quality": "high"}', '/media/gimbal/2024/01/panorama_002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例巡检点数据（必须在tb_device之前插入，因为tb_device引用tb_point）
INSERT INTO tb_point (id, point_name, map_id, enabled, x_coordinate, y_coordinate, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('60000000-0000-0000-0000-000000000001', '巡检点001', '550e8400-e29b-41d4-a716-446655440010', TRUE, 127.3500, 89.6200, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000002', '巡检点002', '550e8400-e29b-41d4-a716-446655440010', TRUE, 342.7800, 256.4300, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000003', '巡检点003', '550e8400-e29b-41d4-a716-446655440010', TRUE, 518.9200, 187.6500, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000004', '巡检点004', '550e8400-e29b-41d4-a716-446655440010', TRUE, 680.1500, 320.4800, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000005', '巡检点005', '550e8400-e29b-41d4-a716-446655440010', TRUE, 450.2300, 580.7600, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000006', '巡检点006', '550e8400-e29b-41d4-a716-446655440010', TRUE, 720.8900, 450.1200, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000007', '巡检点007', '550e8400-e29b-41d4-a716-446655440010', TRUE, 320.5600, 680.3400, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000008', '巡检点008', '550e8400-e29b-41d4-a716-446655440010', TRUE, 580.6700, 250.8900, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000009', '巡检点009', '550e8400-e29b-41d4-a716-446655440010', TRUE, 750.3400, 620.1500, NOW(), NOW(), 'admin', 'admin', FALSE),
('60000000-0000-0000-0000-000000000010', '巡检点010', '550e8400-e29b-41d4-a716-446655440010', TRUE, 280.1200, 420.7800, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例设备数据（关联到巡检点）
-- 为巡检点001创建设备
INSERT INTO tb_device (id, device_name, device_params, point_id, enabled, x_coordinate, y_coordinate, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440070', '温湿度传感器001', '{"type": "temperature_humidity", "model": "DHT22", "range": {"temp": "-40~80", "humidity": "0~100"}, "accuracy": {"temp": "±0.5", "humidity": "±2%"}}', '60000000-0000-0000-0000-000000000001', TRUE, 129.1800, 91.4500, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440071', '气体检测仪001', '{"type": "gas_detector", "model": "MQ-135", "detect_gas": ["CO", "NH3", "NOx", "smoke"], "voltage": "5V"}', '60000000-0000-0000-0000-000000000001', TRUE, 125.6700, 87.9200, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440072', '红外热像仪001', '{"type": "thermal_camera", "model": "FLIR-E8", "resolution": "320x240", "temp_range": "-20~250", "accuracy": "±2°C"}', '60000000-0000-0000-0000-000000000002', TRUE, 345.2400, 258.7600, NOW(), NOW(), 'operator', 'operator', FALSE),
('550e8400-e29b-41d4-a716-446655440073', '可见光相机001', '{"type": "visible_camera", "model": "Hikvision-DS-2CD", "resolution": "1920x1080", "format": "JPEG"}', '60000000-0000-0000-0000-000000000001', TRUE, 131.4200, 93.1800, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440074', '振动传感器001', '{"type": "vibration", "model": "ADXL345", "range": "0~100mm/s", "accuracy": "±0.1mm/s"}', '60000000-0000-0000-0000-000000000003', TRUE, 521.3600, 189.2800, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440075', '温湿度传感器002', '{"type": "temperature_humidity", "model": "DHT22", "range": {"temp": "-40~80", "humidity": "0~100"}, "accuracy": {"temp": "±0.5", "humidity": "±2%"}}', '60000000-0000-0000-0000-000000000004', TRUE, 682.1800, 322.4500, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440076', '压力传感器001', '{"type": "pressure", "model": "MPX5700", "range": "0~700kPa", "accuracy": "±1.5%"}', '60000000-0000-0000-0000-000000000004', TRUE, 678.6700, 318.9200, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440077', '可见光相机002', '{"type": "visible_camera", "model": "Hikvision-DS-2CD", "resolution": "1920x1080", "format": "JPEG"}', '60000000-0000-0000-0000-000000000005', TRUE, 452.2400, 582.7600, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440078', '红外热像仪002', '{"type": "thermal_camera", "model": "FLIR-E8", "resolution": "320x240", "temp_range": "-20~250", "accuracy": "±2°C"}', '60000000-0000-0000-0000-000000000005', TRUE, 448.4200, 578.1800, NOW(), NOW(), 'operator', 'operator', FALSE),
('550e8400-e29b-41d4-a716-446655440079', '气体检测仪002', '{"type": "gas_detector", "model": "MQ-135", "detect_gas": ["CO", "NH3", "NOx", "smoke"], "voltage": "5V"}', '60000000-0000-0000-0000-000000000006', TRUE, 722.8900, 452.1200, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440080', '振动传感器002', '{"type": "vibration", "model": "ADXL345", "range": "0~100mm/s", "accuracy": "±0.1mm/s"}', '60000000-0000-0000-0000-000000000006', TRUE, 718.6700, 448.9200, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440081', '温湿度传感器003', '{"type": "temperature_humidity", "model": "DHT22", "range": {"temp": "-40~80", "humidity": "0~100"}, "accuracy": {"temp": "±0.5", "humidity": "±2%"}}', '60000000-0000-0000-0000-000000000007', TRUE, 322.5600, 682.3400, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440082', '可见光相机003', '{"type": "visible_camera", "model": "Hikvision-DS-2CD", "resolution": "1920x1080", "format": "JPEG"}', '60000000-0000-0000-0000-000000000007', TRUE, 318.4200, 678.1800, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440083', '压力传感器002', '{"type": "pressure", "model": "MPX5700", "range": "0~700kPa", "accuracy": "±1.5%"}', '60000000-0000-0000-0000-000000000008', TRUE, 582.6700, 252.8900, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440084', '红外热像仪003', '{"type": "thermal_camera", "model": "FLIR-E8", "resolution": "320x240", "temp_range": "-20~250", "accuracy": "±2°C"}', '60000000-0000-0000-0000-000000000008', TRUE, 578.2400, 248.7600, NOW(), NOW(), 'operator', 'operator', FALSE),
('550e8400-e29b-41d4-a716-446655440085', '气体检测仪003', '{"type": "gas_detector", "model": "MQ-135", "detect_gas": ["CO", "NH3", "NOx", "smoke"], "voltage": "5V"}', '60000000-0000-0000-0000-000000000009', TRUE, 752.3400, 622.1500, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440086', '振动传感器003', '{"type": "vibration", "model": "ADXL345", "range": "0~100mm/s", "accuracy": "±0.1mm/s"}', '60000000-0000-0000-0000-000000000009', TRUE, 748.6700, 618.9200, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440087', '温湿度传感器004', '{"type": "temperature_humidity", "model": "DHT22", "range": {"temp": "-40~80", "humidity": "0~100"}, "accuracy": {"temp": "±0.5", "humidity": "±2%"}}', '60000000-0000-0000-0000-000000000010', TRUE, 282.1200, 422.7800, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440088', '可见光相机004', '{"type": "visible_camera", "model": "Hikvision-DS-2CD", "resolution": "1920x1080", "format": "JPEG"}', '60000000-0000-0000-0000-000000000010', TRUE, 278.4200, 418.1800, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例巡检项目数据（必须在tb_device之后插入，因为tb_item引用tb_device）
-- 插入示例检测类型数据
INSERT INTO tb_detection_type (id, type_name, type_code, description, sort_order, enabled, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('80000000-0000-0000-0000-000000000001', '温度检测', 'temperature', '温度检测类型', 1, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('80000000-0000-0000-0000-000000000002', '湿度检测', 'humidity', '湿度检测类型', 2, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('80000000-0000-0000-0000-000000000003', '气体检测', 'gas', '气体浓度检测类型', 3, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('80000000-0000-0000-0000-000000000004', '图像检测', 'image', '图像识别检测类型', 4, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('80000000-0000-0000-0000-000000000005', '声音检测', 'audio', '声音识别检测类型', 5, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('80000000-0000-0000-0000-000000000006', '振动检测', 'vibration', '振动检测类型', 6, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('80000000-0000-0000-0000-000000000007', '压力检测', 'pressure', '压力检测类型', 7, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('80000000-0000-0000-0000-000000000008', '流量检测', 'flow', '流量检测类型', 8, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例巡检项目数据
INSERT INTO tb_item (id, item_name, item_info, device_id, robot_id, detection_type_id, enabled, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('70000000-0000-0000-0000-000000000001', '温度检测', '{"type": "temperature", "unit": "℃", "threshold": {"min": -10, "max": 50}}', '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000001', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000002', '湿度检测', '{"type": "humidity", "unit": "%RH", "threshold": {"min": 30, "max": 80}}', '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000002', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000003', '气体浓度检测', '{"type": "gas_concentration", "unit": "ppm", "threshold": {"co": 50, "nh3": 25}}', '550e8400-e29b-41d4-a716-446655440071', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000003', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000005', '热成像检测', '{"type": "thermal_imaging", "format": "image", "resolution": "320x240"}', '550e8400-e29b-41d4-a716-446655440072', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'operator', 'operator', FALSE),
('70000000-0000-0000-0000-000000000006', '可见光拍照', '{"type": "photo", "format": "JPEG", "resolution": "1920x1080"}', '550e8400-e29b-41d4-a716-446655440073', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000007', '振动检测', '{"type": "vibration", "unit": "mm/s", "threshold": {"max": 50}}', '550e8400-e29b-41d4-a716-446655440074', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000006', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000010', '设备状态检查', '{"type": "equipment_status", "check_items": ["power", "connection", "function"]}', '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000013', '清洁度检查', '{"type": "cleanliness", "check_items": ["surface", "dust", "debris"]}', '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000014', '照明检查', '{"type": "lighting", "check_items": ["brightness", "function", "status"]}', '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000015', '温度检测002', '{"type": "temperature", "unit": "℃", "threshold": {"min": -10, "max": 50}}', '550e8400-e29b-41d4-a716-446655440075', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000001', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000016', '湿度检测002', '{"type": "humidity", "unit": "%RH", "threshold": {"min": 30, "max": 80}}', '550e8400-e29b-41d4-a716-446655440075', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000002', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000017', '压力检测', '{"type": "pressure", "unit": "kPa", "threshold": {"min": 0, "max": 700}}', '550e8400-e29b-41d4-a716-446655440076', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000007', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000018', '可见光拍照002', '{"type": "photo", "format": "JPEG", "resolution": "1920x1080"}', '550e8400-e29b-41d4-a716-446655440077', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000019', '设备外观检查', '{"type": "equipment_appearance", "check_items": ["surface", "damage", "cleanliness"]}', '550e8400-e29b-41d4-a716-446655440077', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000020', '热成像检测002', '{"type": "thermal_imaging", "format": "image", "resolution": "320x240"}', '550e8400-e29b-41d4-a716-446655440078', '550e8400-e29b-41d4-a716-446655440021', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'operator', 'operator', FALSE),
('70000000-0000-0000-0000-000000000021', '气体浓度检测002', '{"type": "gas_concentration", "unit": "ppm", "threshold": {"co": 50, "nh3": 25}}', '550e8400-e29b-41d4-a716-446655440079', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000003', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000022', '振动检测002', '{"type": "vibration", "unit": "mm/s", "threshold": {"max": 50}}', '550e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000006', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000023', '温度检测003', '{"type": "temperature", "unit": "℃", "threshold": {"min": -10, "max": 50}}', '550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440022', '80000000-0000-0000-0000-000000000001', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000024', '湿度检测003', '{"type": "humidity", "unit": "%RH", "threshold": {"min": 30, "max": 80}}', '550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000002', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000025', '可见光拍照003', '{"type": "photo", "format": "JPEG", "resolution": "1920x1080"}', '550e8400-e29b-41d4-a716-446655440082', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000026', '压力检测002', '{"type": "pressure", "unit": "kPa", "threshold": {"min": 0, "max": 700}}', '550e8400-e29b-41d4-a716-446655440083', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000007', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000027', '热成像检测003', '{"type": "thermal_imaging", "format": "image", "resolution": "320x240"}', '550e8400-e29b-41d4-a716-446655440084', '550e8400-e29b-41d4-a716-446655440023', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'operator', 'operator', FALSE),
('70000000-0000-0000-0000-000000000028', '气体浓度检测003', '{"type": "gas_concentration", "unit": "ppm", "threshold": {"co": 50, "nh3": 25}}', '550e8400-e29b-41d4-a716-446655440085', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000003', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000029', '振动检测003', '{"type": "vibration", "unit": "mm/s", "threshold": {"max": 50}}', '550e8400-e29b-41d4-a716-446655440086', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000006', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000030', '温度检测004', '{"type": "temperature", "unit": "℃", "threshold": {"min": -10, "max": 50}}', '550e8400-e29b-41d4-a716-446655440087', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000001', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000031', '可见光拍照004', '{"type": "photo", "format": "JPEG", "resolution": "1920x1080"}', '550e8400-e29b-41d4-a716-446655440088', '550e8400-e29b-41d4-a716-446655440023', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例车体控制器配置数据
INSERT INTO cfg_vehicle_controller (id, vehicle_model, wheel_diameter, reduction_ratio, wheelbase, track_width, max_linear_velocity, max_angular_velocity, serial_configs, ethernet_configs, controller_version, remote_upgrade_enabled, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440090', '四轮差速', 430.00, 50, 780.00, 1000.00, 0.800, 0.100, '[{"module_index": 1, "station_number": 1, "baud_rate": 115200, "function_code": 1, "enabled": true}, {"module_index": 2, "station_number": 2, "baud_rate": 115200, "function_code": 2, "enabled": true}, {"module_index": 3, "station_number": 3, "baud_rate": 115200, "function_code": 3, "enabled": false}, {"module_index": 4, "station_number": 4, "baud_rate": 115200, "function_code": 4, "enabled": false}]', '[{"module_index": 1, "ip_address": "192.168.1.100", "subnet_mask": "255.255.255.0", "gateway": "192.168.1.1", "port": 8080, "baud_rate": 115200, "communication_mode": "server", "enabled": true}, {"module_index": 2, "ip_address": "192.168.1.101", "subnet_mask": "255.255.255.0", "gateway": "192.168.1.1", "port": 8081, "baud_rate": 115200, "communication_mode": "client", "enabled": true}]', '1.232', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440091', '双轮差速', 350.00, 30, 600.00, 800.00, 1.200, 0.150, '[{"module_index": 1, "station_number": 1, "baud_rate": 9600, "function_code": 1, "enabled": true}, {"module_index": 2, "station_number": 2, "baud_rate": 9600, "function_code": 2, "enabled": false}, {"module_index": 3, "station_number": 3, "baud_rate": 9600, "function_code": 3, "enabled": false}, {"module_index": 4, "station_number": 4, "baud_rate": 9600, "function_code": 4, "enabled": false}]', '[{"module_index": 1, "ip_address": "192.168.2.100", "subnet_mask": "255.255.255.0", "gateway": "192.168.2.1", "port": 9000, "baud_rate": 9600, "communication_mode": "server", "enabled": true}, {"module_index": 2, "ip_address": "192.168.2.101", "subnet_mask": "255.255.255.0", "gateway": "192.168.2.1", "port": 9001, "baud_rate": 9600, "communication_mode": "client", "enabled": false}]', '1.200', FALSE, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例环境传感器配置数据
INSERT INTO cfg_environment_sensor (id, station_number, baud_rate, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440100', 1, 115200, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440101', 2, 9600, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440102', 3, 19200, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例双光云台配置数据
INSERT INTO cfg_dual_ptz (id, ptz_ip, subnet_mask, gateway, operating_speed, fill_light_enabled, wiper_enabled, auto_focus_enabled, backlight_compensation_enabled, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440110', '192.168.1.100', '255.255.255.0', '192.168.1.1', 100, TRUE, FALSE, TRUE, FALSE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440111', '192.168.1.101', '255.255.255.0', '192.168.1.1', 150, FALSE, TRUE, TRUE, TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440112', '192.168.1.102', '255.255.255.0', '192.168.1.1', 80, TRUE, TRUE, FALSE, FALSE, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例电机状态配置数据
INSERT INTO cfg_motor_status (id, motor_id, baud_rate, tpdo_config, rpdo_config, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440120', 1, 115200, '{"enabled": true, "transmission_type": "synchronous", "inhibit_time": 0, "event_timer": 0, "sync_start_value": 0}', '{"enabled": true, "transmission_type": "synchronous", "inhibit_time": 0, "event_timer": 0, "sync_start_value": 0}', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440121', 2, 9600, '{"enabled": true, "transmission_type": "asynchronous", "inhibit_time": 100, "event_timer": 1000, "sync_start_value": 1}', '{"enabled": true, "transmission_type": "asynchronous", "inhibit_time": 100, "event_timer": 1000, "sync_start_value": 1}', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440122', 3, 19200, '{"enabled": false, "transmission_type": "synchronous", "inhibit_time": 50, "event_timer": 500, "sync_start_value": 0}', '{"enabled": true, "transmission_type": "synchronous", "inhibit_time": 50, "event_timer": 500, "sync_start_value": 0}', NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例激光雷达配置数据
INSERT INTO cfg_lidar (id, lidar_ip, subnet_mask, gateway, lidar_port, scan_frequency_rpm, x_coordinate, y_coordinate, z_coordinate, scan_range_min, scan_range_max, scan_distance_min, scan_distance_max, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440130', '192.168.1.100', '255.255.255.0', '192.168.1.1', 8080, 2000, 49.10, 23.20, 34.90, 0.00, 360.00, 0.00, 100.00, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440131', '192.168.1.101', '255.255.255.0', '192.168.1.1', 8081, 1500, 50.00, 25.00, 35.00, 0.00, 180.00, 0.00, 50.00, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440132', '192.168.1.102', '255.255.255.0', '192.168.1.1', 8082, 3000, 48.50, 22.80, 33.50, 90.00, 270.00, 10.00, 80.00, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例机械臂状态配置数据
INSERT INTO cfg_robot_arm (id, robot_arm_ip, subnet_mask, gateway, robot_arm_port, operating_speed, origin_coordinates, plane_coordinates, load_size, end_coordinates, tool_io, collision_detection_level, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440140', '192.168.1.100', '255.255.255.0', '192.168.1.1', 8080, 50, '[10, 20, 0, 5, -3, -180]', '[10, 20, 0, 5, -3, -180]', 0.50, '[10, 20, 0, 5, -3, -180]', 0, '中', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440141', '192.168.1.101', '255.255.255.0', '192.168.1.1', 8081, 75, '[15, 25, 5, 10, -5, -90]', '[15, 25, 5, 10, -5, -90]', 1.20, '[15, 25, 5, 10, -5, -90]', 128, '高', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440142', '192.168.1.102', '255.255.255.0', '192.168.1.1', 8082, 25, '[5, 15, -5, 0, 0, 0]', '[5, 15, -5, 0, 0, 0]', 0.30, '[5, 15, -5, 0, 0, 0]', 255, '低', NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例超声波状态配置数据
INSERT INTO cfg_ultrasonic (id, ultrasonic_id, obstacle_avoidance_distance, deceleration_distance, baud_rate, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440150', 1, 800.00, 1500.00, 9600, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440151', 2, 1000.00, 2000.00, 19200, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440152', 3, 600.00, 1200.00, 115200, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例深度相机配置数据
INSERT INTO cfg_depth_camera (id, camera_type, resolution_width, resolution_height, frame_rate, depth_range_min, depth_range_max, depth_accuracy, camera_ip, camera_port, protocol, exposure_time, gain, white_balance, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440160', 'RGB-D', 640, 480, 30, 0.10, 10.00, 0.0010, NULL, NULL, 'USB', 8500, 1.50, 'Auto', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440161', 'ToF', 1024, 1024, 30, 0.25, 5.46, 0.0005, '192.168.1.200', 8080, 'Ethernet', 10000, 2.00, 'Daylight', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440162', 'Stereo', 1920, 1080, 60, 0.30, 20.00, 0.0020, '192.168.1.201', 8081, 'WiFi', 12000, 1.80, 'Manual', NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例导航控制器配置数据
INSERT INTO cfg_navigation_controller (id, module_group, ethernet_ip, subnet_mask, gateway, ethernet_port, baud_rate, deceleration_distance, stop_distance, max_linear_velocity, max_angular_velocity, acceleration, deceleration, expansion_coefficient, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440170', 1, '192.168.1.100', '255.255.255.0', '192.168.1.1', 8080, 9600, 800.00, 1500.00, 0.800, 0.100, 0.800, 0.800, 0.00, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440171', 2, '192.168.1.101', '255.255.255.0', '192.168.1.1', 8081, 19200, 1000.00, 2000.00, 1.000, 0.150, 1.000, 1.000, 0.50, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440172', 1, '192.168.1.102', '255.255.255.0', '192.168.1.1', 8082, 115200, 600.00, 1200.00, 0.500, 0.080, 0.500, 0.500, 1.00, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例智能传感器数据
INSERT INTO tb_sensor (id, device_id, sensor_name, sensor_params, enabled, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440070', '温度传感器', '{"unit": "℃", "range": "-40~80", "accuracy": "±0.5", "sampling_rate": "1Hz"}', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440070', '湿度传感器', '{"unit": "%RH", "range": "0~100", "accuracy": "±2%", "sampling_rate": "1Hz"}', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440082', '550e8400-e29b-41d4-a716-446655440071', 'CO浓度传感器', '{"unit": "ppm", "range": "0~1000", "alarm_threshold": 50, "response_time": "30s"}', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440083', '550e8400-e29b-41d4-a716-446655440072', '热成像传感器', '{"resolution": "320x240", "frame_rate": "9Hz", "temp_range": "-20~250", "accuracy": "±2°C"}', TRUE, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例传感器记录数据
INSERT INTO tb_sensorhistory (id, sensor_id, record_data, file_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440100', '550e8400-e29b-41d4-a716-446655440080', '{"temperature": 25.5, "unit": "℃", "status": "normal", "timestamp": 1704067200}', '/data/sensor/2024/01/temp_001.csv', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440081', '{"humidity": 65.2, "unit": "%RH", "status": "normal", "timestamp": 1704067200}', '/data/sensor/2024/01/humidity_001.csv', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440082', '{"co_concentration": 35, "unit": "ppm", "status": "normal", "alarm": false, "timestamp": 1704067260}', '/data/sensor/2024/01/co_001.json', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440103', '550e8400-e29b-41d4-a716-446655440083', '{"max_temp": 45.8, "min_temp": 18.2, "avg_temp": 28.5, "unit": "℃", "status": "completed"}', '/data/sensor/2024/01/thermal_001.jpg', NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例任务数据
-- 插入示例任务数据（厂区一-机器人一的两个任务）
INSERT INTO tb_task (id, task_name, robot_id, task_items, task_order, task_res_prior, task_int_prior, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440021', '任务一：环境监测', '550e8400-e29b-41d4-a716-446655440020', '["70000000-0000-0000-0000-000000000001", "70000000-0000-0000-0000-000000000002", "70000000-0000-0000-0000-000000000003"]', 1, 5, 3, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440022', '任务二：设备巡检', '550e8400-e29b-41d4-a716-446655440020', '["70000000-0000-0000-0000-000000000005", "70000000-0000-0000-0000-000000000006", "70000000-0000-0000-0000-000000000007"]', 2, 5, 3, NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例任务日程数据
INSERT INTO tb_taskschedule (id, task_id, schedule_name, start_date, end_date, enabled, item_count, cycle_type, cycle_config, time_mode, time_config, time_display_start, time_display_end, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440601', '550e8400-e29b-41d4-a716-446655440021', '每日巡检任务', '2024-01-01', '2024-12-31', 1, 5, 'daily', NULL, 'custom', '{"customTimes": ["08:00", "14:00", "18:00"]}', '08:00:00', '18:00:00', NOW(), NOW(), 'superadmin', 'superadmin', 0),
('550e8400-e29b-41d4-a716-446655440602', '550e8400-e29b-41d4-a716-446655440021', '每周一巡检任务', '2024-01-01', '2024-12-31', 1, 4, 'weekly', '{"selectedWeeks": [1]}', 'custom', '{"customTimes": ["14:00"]}', '14:00:00', '14:00:00', NOW(), NOW(), 'admin', 'admin', 0),
('550e8400-e29b-41d4-a716-446655440603', '550e8400-e29b-41d4-a716-446655440021', '每月固定日期间隔巡检', '2025-01-01', '2025-12-31', 1, 3, 'monthly_days', '{"selectedDays": [5, 10, 15, 20]}', 'interval', '{"intervalTimeRange": ["08:00", "20:00"], "intervalMinutes": 120}', '08:00:00', '20:00:00', NOW(), NOW(), 'admin', 'admin', 0),
('550e8400-e29b-41d4-a716-446655440604', '550e8400-e29b-41d4-a716-446655440022', '任务二每日巡检', '2025-01-01', '2025-12-31', 1, 3, 'daily', NULL, 'custom', '{"customTimes": ["09:00", "15:00", "21:00"]}', '09:00:00', '21:00:00', NOW(), NOW(), 'superadmin', 'superadmin', 0),
('550e8400-e29b-41d4-a716-446655440605', '550e8400-e29b-41d4-a716-446655440022', '任务二每周工作日巡检', '2025-01-01', '2025-12-31', 1, 3, 'weekly', '{"selectedWeeks": [1, 2, 3, 4, 5]}', 'interval', '{"intervalTimeRange": ["08:00", "18:00"], "intervalMinutes": 180}', '08:00:00', '18:00:00', NOW(), NOW(), 'superadmin', 'superadmin', 0),
('550e8400-e29b-41d4-a716-446655440606', '550e8400-e29b-41d4-a716-446655440022', '任务二每月初巡检', '2025-01-01', '2025-12-31', 1, 3, 'monthly_days', '{"selectedDays": [1]}', 'custom', '{"customTimes": ["10:00"]}', '10:00:00', '10:00:00', NOW(), NOW(), 'admin', 'admin', 0);

-- 插入示例任务记录数据
INSERT INTO tb_taskhistory (id, task_id, record_start_time, record_end_time, record_status, record_batch, current_point_id, current_item_id, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440801', '550e8400-e29b-41d4-a716-446655440021', '2024-01-15T08:00:00', '2024-01-15T08:30:00', 'completed', 1, NULL, NULL, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440802', '550e8400-e29b-41d4-a716-446655440021', '2024-01-15T14:00:00', '2024-01-15T14:28:00', 'completed', 2, NULL, NULL, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440803', '550e8400-e29b-41d4-a716-446655440021', '2024-01-16T09:00:00', NULL, 'running', 3, '60000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例任务结果数据
INSERT INTO tb_taskresult (id, taskhistory_id, record_batch, result_status, process_status, result_point_id, result_item_id, result_file_url, result_collect_time, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440901', '550e8400-e29b-41d4-a716-446655440801', 1, 'success', 'processed', '60000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000010', '/uploads/results/task_001_batch_001.json', '2024-01-15T08:30:00', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440902', '550e8400-e29b-41d4-a716-446655440802', 2, 'partial', 'processing', '60000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000010', '/uploads/results/task_001_batch_002.json', '2024-01-15T14:28:00', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例巡检记录数据
INSERT INTO tb_itemhistory (id, taskhistory_id, item_id, item_result, process_status, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655441001', '550e8400-e29b-41d4-a716-446655440801', '70000000-0000-0000-0000-000000000001', '{"status": "success", "photos": ["/data/photo1.jpg", "/data/photo2.jpg"]}', 'processed', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655441002', '550e8400-e29b-41d4-a716-446655440801', '70000000-0000-0000-0000-000000000002', '{"status": "success", "check_result": "正常"}', 'processed', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655441003', '550e8400-e29b-41d4-a716-446655440801', '70000000-0000-0000-0000-000000000010', '{"status": "success", "equipment_status": "正常"}', 'processing', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655441004', '550e8400-e29b-41d4-a716-446655440802', '70000000-0000-0000-0000-000000000013', '{"status": "success", "cleanliness": "良好"}', 'processed', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655441005', '550e8400-e29b-41d4-a716-446655440802', '70000000-0000-0000-0000-000000000014', '{"status": "success", "lighting": "正常"}', 'pending', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例报警规则数据（新表结构，暂时为空，等报警功能完全实现后再添加示例数据）
-- INSERT INTO tb_alarm_rule (id, rule_name, alarm_category, alarm_level, rule_type, rule_config, enabled, description, is_global, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
-- ('550e8400-e29b-41d4-a716-446655441101', '温度异常报警', 'inspection', 5, 'value_range', '{"data_source": "itemhistory.item_result.temperature", "ranges": [{"min": 0, "max": 20, "alarm": true}]}', TRUE, '温度超出正常范围', FALSE, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例报警信息数据（新表结构，暂时为空，等报警功能完全实现后再添加示例数据）
-- INSERT INTO tb_alarm_info (id, alarm_rule_id, alarm_category, alarm_level, alarm_status, source_type, source_ids, relation_type, relation_ids, trigger_item_ids, trigger_data, alarm_message, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
-- ('550e8400-e29b-41d4-a716-446655441201', '550e8400-e29b-41d4-a716-446655441101', 'inspection', 5, 'unviewed', 'itemhistory', '["itemhistory-001"]', 'item', '["item-001"]', '["item-001"]', '{"temperature": 15}', '温度异常', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入手动操作记录测试数据
INSERT INTO tb_manual_operation (id, user_id, username, operation_time, operation_content, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440000', 'superadmin', '2024-01-15 09:30:00', '{"action": "manual_start", "target": "robot_001", "description": "手动启动机器人"}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440010', 'admin', '2024-01-15 10:15:00', '{"action": "manual_stop", "target": "robot_002", "description": "手动停止机器人"}', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440082', '550e8400-e29b-41d4-a716-446655440002', 'operator', '2024-01-15 11:00:00', '{"action": "manual_reset", "target": "gimbal_001", "description": "手动重置云台"}', NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入操作记录测试数据
INSERT INTO tb_operation_record (id, user_id, username, operation_time, operation_content, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440090', '550e8400-e29b-41d4-a716-446655440000', 'superadmin', '2024-01-15 08:00:00', '{"action": "login", "ip": "192.168.1.100", "description": "用户登录"}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440091', '550e8400-e29b-41d4-a716-446655440010', 'admin', '2024-01-15 08:30:00', '{"action": "create_task", "target": "task_001", "description": "创建新任务"}', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440092', '550e8400-e29b-41d4-a716-446655440002', 'operator', '2024-01-15 09:00:00', '{"action": "update_config", "target": "robot_config", "description": "更新机器人配置"}', NOW(), NOW(), 'operator', 'operator', FALSE),
('550e8400-e29b-41d4-a716-446655440093', '550e8400-e29b-41d4-a716-446655440000', 'superadmin', '2024-01-15 12:00:00', '{"action": "logout", "ip": "192.168.1.100", "description": "用户登出"}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

SELECT '========== 操作记录模块 ==========' as divider1;
SELECT '手动操作记录表: tb_manual_operation' as table1;
SELECT '操作记录表: tb_operation_record' as table2;
SELECT '========== 示例数据统计 ==========' as divider2;
SELECT '3个用户, 2个厂区, 3个地图, 6个机器人, 19个设备, 4个智能传感器, 3个传感器日程, 4个传感器记录, 50个云台, 50个云台任务, 11个预设点, 7个巡检项目, 12个关联关系, 3个云台日程, 4个云台记录, 2个车体控制器配置, 3个环境传感器配置, 3个双光云台配置, 3个电机状态配置, 3个激光雷达配置, 3个机械臂状态配置, 3个超声波状态配置, 3个深度相机配置, 3个导航控制器配置, 1个任务' as summary1;
SELECT '3条地图路网, 10个巡检点, 26个巡检项目' as summary2;
SELECT '2条任务日程, 3条任务记录, 3条任务结果, 5条巡检记录' as summary3;
SELECT '2条报警规则, 1条报警信息' as summary4;
SELECT '3条手动操作记录, 4条操作记录' as summary5;
