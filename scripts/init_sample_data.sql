-- 博实智能巡检平台 - 示例数据初始化SQL
USE boshirobot;

-- 注意：此脚本假设数据库表结构已经通过 init_database.sql 创建
-- 如果是旧版本数据库升级，请先执行 add_missing_columns.sql 添加缺失字段

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
DELETE FROM tb_group;
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

-- 插入示例厂区数据（只有一个厂区）
INSERT INTO tb_factory (id, factory_name, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440000', '默认厂区', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例地图数据（只有一个地图）
INSERT INTO tb_map (id, map_name, map_image_url, map_scale, map_center_x, map_center_y, factory_id, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440010', '默认地图', '/uploads/maps/default_map.png', 1.0, 100.0, 100.0, '550e8400-e29b-41d4-a716-446655440000', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例地图路网数据
-- 厂区一地图路网
INSERT INTO tb_mapnet (id, map_id, map_net_type, map_net_properties, map_net_geometry, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440501', '550e8400-e29b-41d4-a716-446655440010', 'point', '{"name": "导航点A", "type": "navigation"}', '{"x": 50.0, "y": 50.0}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440502', '550e8400-e29b-41d4-a716-446655440010', 'line', '{"name": "巡检路径1", "width": 2, "color": "blue"}', '{"start": {"x": 50.0, "y": 50.0}, "end": {"x": 150.0, "y": 50.0}}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440503', '550e8400-e29b-41d4-a716-446655440010', 'rect', '{"name": "禁区范围", "type": "restricted"}', '{"x": 80.0, "y": 80.0, "width": 40.0, "height": 30.0}', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例分组数据（只有一个组）
INSERT INTO tb_group (id, group_name, group_description, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440200', '第一组', '第一组设备分组', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例机器人数据（只有一个机器人）
INSERT INTO tb_robot (id, robot_name, robot_info, factory_id, group_id, preview_url, control_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440020', '默认机器人', '{"model": "BOSHI-RB-01", "battery": 100, "status": "idle"}', '550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440200', 'http://192.168.8.126:9266/robot-preview', 'http://192.168.8.126:9266/robot-control', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入机器人-地图关联数据（唯一机器人关联唯一地图）
INSERT INTO tb_robot_map (id, robot_id, map_id, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440501', '550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440010', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例云台数据（只有1个云台）
INSERT INTO tb_gimbal (id, gimbal_name, map_id, group_id, enabled, ip_address, port, username, password, rtsp_main_url, rtsp_sub_url, channel, x_coordinate, y_coordinate, p_coordinate, t_coordinate, z_coordinate, f_coordinate, preview_url, control_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440030', '云台001', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440200', TRUE, '192.168.1.110', 554, 'admin', 'admin123', 'rtsp://192.168.1.110:554/stream/main', 'rtsp://192.168.1.110:554/stream/sub', 1, 198.6700, 134.2800, 0.0000, 0.0000, 0.0000, 0.0000, 'http://192.168.8.126:9266/ptz-preview', 'http://192.168.8.126:9266/ptz-control', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台任务数据（只保留云台001的任务）
INSERT INTO tb_gimbaltask (id, task_name, gimbal_id, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('650e8400-e29b-41d4-a716-446655440040', '云台001-日常巡检任务', '550e8400-e29b-41d4-a716-446655440030', NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440041', '云台001-夜间监控任务', '550e8400-e29b-41d4-a716-446655440030', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台预设点数据（只保留云台001的预设点，4个预设点）
INSERT INTO tb_gimbal_preset_point (id, preset_name, gimbal_id, p_coordinate, t_coordinate, z_coordinate, f_coordinate, aperture, shutter, backlight_compensation, wide_dynamic, strong_light_suppression, fill_light, image_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('750e8400-e29b-41d4-a716-446655440030', '预设点-全景', '550e8400-e29b-41d4-a716-446655440030', 0.0000, 0.0000, 1.0000, 0.5000, 40, 60, TRUE, TRUE, FALSE, FALSE, '/media/preset/gimbal001_preset001.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440031', '预设点-监控', '550e8400-e29b-41d4-a716-446655440030', 5.0000, 2.5000, 2.5000, 1.2000, 55, 30, TRUE, FALSE, TRUE, TRUE, '/media/preset/gimbal001_preset002.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440032', '预设点-定点', '550e8400-e29b-41d4-a716-446655440030', 10.0000, 5.0000, 3.0000, 1.5000, 50, 40, FALSE, TRUE, TRUE, FALSE, '/media/preset/gimbal001_preset003.jpg', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440033', '预设点-东侧', '550e8400-e29b-41d4-a716-446655440030', 0.0000, 0.0000, 4.0000, 0.8000, 35, 15, FALSE, TRUE, TRUE, TRUE, '/media/preset/gimbal001_preset004.jpg', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台巡检项目数据（只保留云台001的任务的巡检项目）
INSERT INTO tb_gimbal_inspection_project (id, task_name, gimbaltask_id, sort_order, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('650e8400-e29b-41d4-a716-446655440050', '日常巡检项目1', '650e8400-e29b-41d4-a716-446655440040', 1, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440051', '日常巡检项目2', '650e8400-e29b-41d4-a716-446655440040', 2, NOW(), NOW(), 'admin', 'admin', FALSE),
('650e8400-e29b-41d4-a716-446655440052', '夜间监控项目', '650e8400-e29b-41d4-a716-446655440041', 1, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台巡检项目-预设点关联数据（只保留云台001的关联）
INSERT INTO tb_gimbal_inspection_project_preset_point (id, inspection_project_id, preset_point_id, detection_type, video_duration, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('850e8400-e29b-41d4-a716-446655440040', '650e8400-e29b-41d4-a716-446655440050', '750e8400-e29b-41d4-a716-446655440030', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440041', '650e8400-e29b-41d4-a716-446655440050', '750e8400-e29b-41d4-a716-446655440031', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440042', '650e8400-e29b-41d4-a716-446655440051', '750e8400-e29b-41d4-a716-446655440032', '可见光视频', 60, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440043', '650e8400-e29b-41d4-a716-446655440051', '750e8400-e29b-41d4-a716-446655440033', '热成像图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440044', '650e8400-e29b-41d4-a716-446655440052', '750e8400-e29b-41d4-a716-446655440030', '可见光图片', NULL, NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440045', '650e8400-e29b-41d4-a716-446655440052', '750e8400-e29b-41d4-a716-446655440031', '可见光视频', 30, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台日程数据（只保留云台001的任务的日程）
INSERT INTO tb_gimbalschedule (id, gimbaltask_id, schedule_name, start_date, end_date, enabled, cycle_type, cycle_config, time_mode, time_config, time_display_start, time_display_end, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('750e8400-e29b-41d4-a716-446655440040', '650e8400-e29b-41d4-a716-446655440040', '日常巡检日程', '2024-12-19', '2026-12-19', TRUE, 'daily', NULL, 'custom', '{"customTimes": ["08:00", "14:00", "18:00"]}', '08:00:00', '18:00:00', NOW(), NOW(), 'admin', 'admin', FALSE),
('750e8400-e29b-41d4-a716-446655440041', '650e8400-e29b-41d4-a716-446655440041', '夜间监控日程', '2024-12-19', '2026-12-19', TRUE, 'daily', NULL, 'custom', '{"customTimes": ["20:00", "22:00", "00:00"]}', '20:00:00', '00:00:00', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例云台记录数据
-- 插入示例云台记录数据
INSERT INTO tb_gimbalhistory (id, project_preset_point_id, record_data, media_url, view_status, inspection_result_status, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('850e8400-e29b-41d4-a716-446655440060', '850e8400-e29b-41d4-a716-446655440040', '{"status": 0, "angle": {"pan": 0, "tilt": 0, "zoom": 1}, "quality": "high", "temperature": 25.5}', '/media/gimbal/gimbal001_record001.jpg', 'pending', 'critical', NOW(), NOW(), 'admin', 'admin', FALSE),
('850e8400-e29b-41d4-a716-446655440061', '850e8400-e29b-41d4-a716-446655440041', '{"status": 1, "angle": {"pan": 5, "tilt": 2.5, "zoom": 1.2}, "quality": "high", "temperature": 24.8}', '/media/gimbal/gimbal001_record002.mp4', NULL, 'normal', NOW(), NOW(), 'admin', 'admin', FALSE);

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
('70000000-0000-0000-0000-000000000020', '热成像检测002', '{"type": "thermal_imaging", "format": "image", "resolution": "320x240"}', '550e8400-e29b-41d4-a716-446655440078', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'operator', 'operator', FALSE),
('70000000-0000-0000-0000-000000000021', '气体浓度检测002', '{"type": "gas_concentration", "unit": "ppm", "threshold": {"co": 50, "nh3": 25}}', '550e8400-e29b-41d4-a716-446655440079', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000003', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000022', '振动检测002', '{"type": "vibration", "unit": "mm/s", "threshold": {"max": 50}}', '550e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000006', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000023', '温度检测003', '{"type": "temperature", "unit": "℃", "threshold": {"min": -10, "max": 50}}', '550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000001', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000024', '湿度检测003', '{"type": "humidity", "unit": "%RH", "threshold": {"min": 30, "max": 80}}', '550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000002', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000025', '可见光拍照003', '{"type": "photo", "format": "JPEG", "resolution": "1920x1080"}', '550e8400-e29b-41d4-a716-446655440082', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000026', '压力检测002', '{"type": "pressure", "unit": "kPa", "threshold": {"min": 0, "max": 700}}', '550e8400-e29b-41d4-a716-446655440083', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000007', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000027', '热成像检测003', '{"type": "thermal_imaging", "format": "image", "resolution": "320x240"}', '550e8400-e29b-41d4-a716-446655440084', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'operator', 'operator', FALSE),
('70000000-0000-0000-0000-000000000028', '气体浓度检测003', '{"type": "gas_concentration", "unit": "ppm", "threshold": {"co": 50, "nh3": 25}}', '550e8400-e29b-41d4-a716-446655440085', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000003', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000029', '振动检测003', '{"type": "vibration", "unit": "mm/s", "threshold": {"max": 50}}', '550e8400-e29b-41d4-a716-446655440086', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000006', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000030', '温度检测004', '{"type": "temperature", "unit": "℃", "threshold": {"min": -10, "max": 50}}', '550e8400-e29b-41d4-a716-446655440087', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000001', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('70000000-0000-0000-0000-000000000031', '可见光拍照004', '{"type": "photo", "format": "JPEG", "resolution": "1920x1080"}', '550e8400-e29b-41d4-a716-446655440088', '550e8400-e29b-41d4-a716-446655440020', '80000000-0000-0000-0000-000000000004', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例车体控制器配置数据
INSERT INTO cfg_vehicle_controller (id, robot_id, vehicle_model, wheel_diameter, reduction_ratio, wheelbase, track_width, max_linear_velocity, max_angular_velocity, serial_1_station_number, serial_1_baud_rate, serial_1_function_code, serial_2_station_number, serial_2_baud_rate, serial_2_function_code, serial_3_station_number, serial_3_baud_rate, serial_3_function_code, serial_4_station_number, serial_4_baud_rate, serial_4_function_code, ethernet_1_ip_address, ethernet_1_subnet_mask, ethernet_1_gateway, ethernet_1_port, ethernet_1_baud_rate, ethernet_1_communication_mode, ethernet_2_ip_address, ethernet_2_subnet_mask, ethernet_2_gateway, ethernet_2_port, ethernet_2_baud_rate, ethernet_2_communication_mode, controller_version, remote_upgrade_enabled, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440090', '550e8400-e29b-41d4-a716-446655440020', '四轮差速', 430.00, 50, 780.00, 1000.00, 0.800, 0.100, 1, 115200, 1, 2, 115200, 2, 3, 115200, 3, 4, 115200, 4, '192.168.1.100', '255.255.255.0', '192.168.1.1', 8080, 115200, 'server', '192.168.1.101', '255.255.255.0', '192.168.1.1', 8081, 115200, 'client', '1.232', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例环境传感器配置数据
INSERT INTO cfg_environment_sensor (id, robot_id, station_number, baud_rate, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440200', '550e8400-e29b-41d4-a716-446655440020', 1, 115200, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例双光云台配置数据
INSERT INTO cfg_dual_ptz (id, robot_id, ptz_ip, subnet_mask, gateway, operating_speed, fill_light_enabled, wiper_enabled, auto_focus_enabled, backlight_compensation_enabled, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440210', '550e8400-e29b-41d4-a716-446655440020', '192.168.1.100', '255.255.255.0', '192.168.1.1', 100, TRUE, FALSE, TRUE, FALSE, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例电机状态配置数据
INSERT INTO cfg_motor_status (id, robot_id, motor_id, baud_rate, tpdo_config, rpdo_config, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440220', '550e8400-e29b-41d4-a716-446655440020', 1, 115200, '{"enabled": true, "transmission_type": "synchronous", "inhibit_time": 0, "event_timer": 0, "sync_start_value": 0}', '{"enabled": true, "transmission_type": "synchronous", "inhibit_time": 0, "event_timer": 0, "sync_start_value": 0}', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例激光雷达配置数据
INSERT INTO cfg_lidar (id, robot_id, lidar_ip, subnet_mask, gateway, lidar_port, scan_frequency_rpm, x_coordinate, y_coordinate, z_coordinate, scan_range_min, scan_range_max, scan_distance_min, scan_distance_max, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440130', '550e8400-e29b-41d4-a716-446655440020', '192.168.1.100', '255.255.255.0', '192.168.1.1', 8080, 2000, 49.10, 23.20, 34.90, 0.00, 360.00, 0.00, 100.00, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例机械臂状态配置数据
INSERT INTO cfg_robot_arm (id, robot_id, robot_arm_ip, subnet_mask, gateway, robot_arm_port, operating_speed, origin_coordinates, plane_coordinates, load_size, end_coordinates, tool_io, collision_detection_level, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440140', '550e8400-e29b-41d4-a716-446655440020', '192.168.1.100', '255.255.255.0', '192.168.1.1', 8080, 50, JSON_ARRAY(10, 20, 0, 5, -3, -180), JSON_ARRAY(10, 20, 0, 5, -3, -180), 0.50, JSON_ARRAY(10, 20, 0, 5, -3, -180), 0, '中', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例超声波状态配置数据
INSERT INTO cfg_ultrasonic (id, robot_id, ultrasonic_id, obstacle_avoidance_distance, deceleration_distance, baud_rate, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440150', '550e8400-e29b-41d4-a716-446655440020', 1, 800.00, 1500.00, 9600, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例深度相机配置数据
INSERT INTO cfg_depth_camera (id, robot_id, serial_port_id, camera_mode, image_flip, image_alignment, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440160', '550e8400-e29b-41d4-a716-446655440020', 1, '标准模式', '上下翻转', '自动对齐', NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例导航控制器配置数据
INSERT INTO cfg_navigation_controller (id, robot_id, ethernet_1_ip, ethernet_1_subnet_mask, ethernet_1_gateway, ethernet_1_port, ethernet_1_baud_rate, ethernet_2_ip, ethernet_2_subnet_mask, ethernet_2_gateway, ethernet_2_port, ethernet_2_baud_rate, deceleration_distance, stop_distance, max_linear_velocity, max_angular_velocity, acceleration, deceleration, expansion_coefficient, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440170', '550e8400-e29b-41d4-a716-446655440020', '192.168.1.100', '255.255.255.0', '192.168.1.1', 8080, 9600, '192.168.1.101', '255.255.255.0', '192.168.1.1', 8081, 19200, 800.00, 1500.00, 0.800, 0.100, 0.800, 0.800, 0.00, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例智能传感器数据
INSERT INTO tb_sensor (id, device_id, sensor_name, sensor_params, group_id, enabled, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440070', '温度传感器', '{"unit": "℃", "range": "-40~80", "accuracy": "±0.5", "sampling_rate": "1Hz"}', '550e8400-e29b-41d4-a716-446655440200', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440070', '湿度传感器', '{"unit": "%RH", "range": "0~100", "accuracy": "±2%", "sampling_rate": "1Hz"}', '550e8400-e29b-41d4-a716-446655440201', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440082', '550e8400-e29b-41d4-a716-446655440071', 'CO浓度传感器', '{"unit": "ppm", "range": "0~1000", "alarm_threshold": 50, "response_time": "30s"}', '550e8400-e29b-41d4-a716-446655440202', TRUE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440083', '550e8400-e29b-41d4-a716-446655440072', '热成像传感器', '{"resolution": "320x240", "frame_rate": "9Hz", "temp_range": "-20~250", "accuracy": "±2°C"}', NULL, TRUE, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例传感器记录数据
INSERT INTO tb_sensorhistory (id, sensor_id, record_data, file_url, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440100', '550e8400-e29b-41d4-a716-446655440080', '{"temperature": 25.5, "unit": "℃", "status": "normal", "timestamp": 1704067200}', '/data/sensor/2024/01/temp_001.csv', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440081', '{"humidity": 65.2, "unit": "%RH", "status": "normal", "timestamp": 1704067200}', '/data/sensor/2024/01/humidity_001.csv', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440082', '{"co_concentration": 35, "unit": "ppm", "status": "normal", "alarm": false, "timestamp": 1704067260}', '/data/sensor/2024/01/co_001.json', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655440103', '550e8400-e29b-41d4-a716-446655440083', '{"max_temp": 45.8, "min_temp": 18.2, "avg_temp": 28.5, "unit": "℃", "status": "completed"}', '/data/sensor/2024/01/thermal_001.jpg', NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例任务数据
-- 插入示例任务数据（厂区一-机器人一的两个任务）
INSERT INTO tb_task (id, task_name, robot_id, task_items, task_order, task_res_prior, task_int_prior, total_duration, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440021', '任务一：环境监测', '550e8400-e29b-41d4-a716-446655440020', '["70000000-0000-0000-0000-000000000001", "70000000-0000-0000-0000-000000000002", "70000000-0000-0000-0000-000000000003"]', 1, 5, 3, 30, NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440022', '任务二：设备巡检', '550e8400-e29b-41d4-a716-446655440020', '["70000000-0000-0000-0000-000000000005", "70000000-0000-0000-0000-000000000006", "70000000-0000-0000-0000-000000000007"]', 2, 5, 3, 45, NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例任务日程数据
INSERT INTO tb_taskschedule (id, task_id, schedule_name, start_date, end_date, enabled, item_count, cycle_type, cycle_config, time_mode, time_config, time_display_start, time_display_end, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440601', '550e8400-e29b-41d4-a716-446655440021', '每日巡检任务', '2024-01-01', '2024-12-31', 1, 5, 'daily', NULL, 'custom', '{"customTimes": ["08:00", "14:00", "18:00"]}', '08:00:00', '18:00:00', NOW(), NOW(), 'superadmin', 'superadmin', 0),
('550e8400-e29b-41d4-a716-446655440602', '550e8400-e29b-41d4-a716-446655440021', '每周一巡检任务', '2024-01-01', '2024-12-31', 1, 4, 'weekly', '{"selectedWeeks": [1]}', 'custom', '{"customTimes": ["14:00"]}', '14:00:00', '14:00:00', NOW(), NOW(), 'admin', 'admin', 0),
('550e8400-e29b-41d4-a716-446655440603', '550e8400-e29b-41d4-a716-446655440021', '每月固定日期间隔巡检', '2025-01-01', '2025-12-31', 1, 3, 'monthly_days', '{"selectedDays": [5, 10, 15, 20]}', 'interval', '{"intervalTimeRange": ["08:00", "20:00"], "intervalMinutes": 120}', '08:00:00', '20:00:00', NOW(), NOW(), 'admin', 'admin', 0),
('550e8400-e29b-41d4-a716-446655440604', '550e8400-e29b-41d4-a716-446655440022', '任务二每日巡检', '2025-01-01', '2025-12-31', 1, 3, 'daily', NULL, 'custom', '{"customTimes": ["09:00", "15:00", "21:00"]}', '09:00:00', '21:00:00', NOW(), NOW(), 'superadmin', 'superadmin', 0),
('550e8400-e29b-41d4-a716-446655440605', '550e8400-e29b-41d4-a716-446655440022', '任务二每周工作日巡检', '2025-01-01', '2025-12-31', 1, 3, 'weekly', '{"selectedWeeks": [1, 2, 3, 4, 5]}', 'interval', '{"intervalTimeRange": ["08:00", "18:00"], "intervalMinutes": 180}', '08:00:00', '18:00:00', NOW(), NOW(), 'superadmin', 'superadmin', 0),
('550e8400-e29b-41d4-a716-446655440606', '550e8400-e29b-41d4-a716-446655440022', '任务二每月初巡检', '2025-01-01', '2025-12-31', 1, 3, 'monthly_days', '{"selectedDays": [1]}', 'custom', '{"customTimes": ["10:00"]}', '10:00:00', '10:00:00', NOW(), NOW(), 'admin', 'admin', 0);

-- 插入示例任务记录数据
INSERT INTO tb_taskhistory (id, task_id, record_start_time, record_end_time, record_status, record_batch, current_point_id, current_item_id, view_status, inspection_result_status, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440801', '550e8400-e29b-41d4-a716-446655440021', '2024-01-15T08:00:00', '2024-01-15T08:30:00', 'completed', 1, NULL, NULL, 'pending', 'critical', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440802', '550e8400-e29b-41d4-a716-446655440021', '2024-01-15T14:00:00', '2024-01-15T14:28:00', 'completed', 2, NULL, NULL, NULL, 'normal', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440803', '550e8400-e29b-41d4-a716-446655440021', '2024-01-16T09:00:00', NULL, 'running', 3, '60000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', NULL, NULL, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例任务结果数据
-- result_status: success-成功, failed-失败, partial-部分成功, warning-警告
-- process_status: pending-待处理, viewed-已查看, processed-已处理
INSERT INTO tb_taskresult (id, taskhistory_id, record_batch, result_status, process_status, result_point_id, result_item_id, result_file_url, result_collect_time, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655440901', '550e8400-e29b-41d4-a716-446655440801', 1, 'failed', 'pending', '60000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000010', '/uploads/results/task_001_batch_001.json', '2024-01-15T08:30:00', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440902', '550e8400-e29b-41d4-a716-446655440802', 2, 'warning', 'viewed', '60000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000010', '/uploads/results/task_001_batch_002.json', '2024-01-15T14:28:00', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655440903', '550e8400-e29b-41d4-a716-446655440803', 3, NULL, 'pending', '60000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', NULL, NULL, NOW(), NOW(), 'operator', 'operator', FALSE);

-- 插入示例巡检记录数据
-- process_status: pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）
-- inspection_result_status: normal-正常, warning-预警报警, critical-严重报警, emergency-危机报警
INSERT INTO tb_itemhistory (id, taskhistory_id, item_id, item_result, process_status, inspection_result_status, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655441001', '550e8400-e29b-41d4-a716-446655440801', '70000000-0000-0000-0000-000000000001', '{"status": "success", "photos": ["/data/photo1.jpg", "/data/photo2.jpg"]}', 'pending', 'critical', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655441002', '550e8400-e29b-41d4-a716-446655440801', '70000000-0000-0000-0000-000000000002', '{"status": "warning", "check_result": "温度异常", "temperature": 85}', 'pending', 'critical', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655441003', '550e8400-e29b-41d4-a716-446655440801', '70000000-0000-0000-0000-000000000010', '{"status": "success", "equipment_status": "正常"}', 'pending', 'emergency', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655441004', '550e8400-e29b-41d4-a716-446655440802', '70000000-0000-0000-0000-000000000013', '{"status": "success", "cleanliness": "良好"}', NULL, 'normal', NOW(), NOW(), 'superadmin', 'superadmin', FALSE),
('550e8400-e29b-41d4-a716-446655441005', '550e8400-e29b-41d4-a716-446655440802', '70000000-0000-0000-0000-000000000014', '{"status": "success", "lighting": "正常"}', NULL, 'normal', NOW(), NOW(), 'superadmin', 'superadmin', FALSE);

-- 插入示例报警规则数据
INSERT INTO tb_alarm_rule (id, rule_name, alarm_category, alarm_level, rule_type, rule_config, enabled, description, is_global, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655441101', '温度异常报警', 'inspection', 5, 'value_range', '{"data_source": "itemhistory.item_result.temperature", "ranges": [{"min": 0, "max": 20, "alarm": true}, {"min": 60, "max": 100, "alarm": true}]}', TRUE, '温度超出正常范围（0-20℃或60-100℃）', FALSE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441102', '湿度异常报警', 'inspection', 4, 'value_range', '{"data_source": "itemhistory.item_result.humidity", "ranges": [{"min": 0, "max": 30, "alarm": true}, {"min": 80, "max": 100, "alarm": true}]}', TRUE, '湿度超出正常范围（30-80%）', FALSE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441103', '云台监控异常报警', 'gimbal', 6, 'value_range', '{"data_source": "gimbalhistory.record_data.status", "ranges": [{"min": 0, "max": 0, "alarm": true}]}', TRUE, '云台监控状态异常', FALSE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441104', '设备状态异常报警', 'inspection', 7, 'value_range', '{"data_source": "itemhistory.item_result.equipment_status_code", "ranges": [{"min": 1, "max": 1, "alarm": true}]}', TRUE, '设备状态码为1时报警', FALSE, NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441105', '机器人车体异常报警', 'robot', 8, 'bool_value', '{"data_source": "robot_status.status", "alarm_value": "error"}', TRUE, '机器人车体状态异常', FALSE, NOW(), NOW(), 'admin', 'admin', FALSE);

-- 插入示例报警规则关联数据（绑定巡检项目和云台巡检项目）
INSERT INTO tb_alarm_rule_relation (id, alarm_rule_id, relation_type, relation_id, sort_order, created_at, updated_at, created_by, updated_by) VALUES
('550e8400-e29b-41d4-a716-446655441201', '550e8400-e29b-41d4-a716-446655441101', 'item', '70000000-0000-0000-0000-000000000001', 0, NOW(), NOW(), 'admin', 'admin'),
('550e8400-e29b-41d4-a716-446655441202', '550e8400-e29b-41d4-a716-446655441101', 'item', '70000000-0000-0000-0000-000000000002', 0, NOW(), NOW(), 'admin', 'admin'),
('550e8400-e29b-41d4-a716-446655441203', '550e8400-e29b-41d4-a716-446655441102', 'item', '70000000-0000-0000-0000-000000000003', 0, NOW(), NOW(), 'admin', 'admin'),
('550e8400-e29b-41d4-a716-446655441204', '550e8400-e29b-41d4-a716-446655441103', 'gimbal', '650e8400-e29b-41d4-a716-446655440050', 0, NOW(), NOW(), 'admin', 'admin'),
('550e8400-e29b-41d4-a716-446655441206', '550e8400-e29b-41d4-a716-446655441104', 'item', '70000000-0000-0000-0000-000000000010', 0, NOW(), NOW(), 'admin', 'admin'),
('550e8400-e29b-41d4-a716-446655441207', '550e8400-e29b-41d4-a716-446655441105', 'robot', '550e8400-e29b-41d4-a716-446655440020', 0, NOW(), NOW(), 'admin', 'admin');

-- 插入示例报警信息数据（绑定具体的巡检结果）
INSERT INTO tb_alarm_info (id, alarm_rule_id, alarm_category, alarm_level, alarm_status, source_type, source_ids, relation_type, relation_ids, trigger_item_ids, trigger_project_ids, trigger_data, calculated_value, alarm_message, created_at, updated_at, created_by, updated_by, is_deleted) VALUES
('550e8400-e29b-41d4-a716-446655441301', '550e8400-e29b-41d4-a716-446655441101', 'inspection', 5, 'unviewed', 'itemhistory', '["550e8400-e29b-41d4-a716-446655441001"]', 'item', '["70000000-0000-0000-0000-000000000001"]', '["70000000-0000-0000-0000-000000000001"]', NULL, '{"temperature": 15, "status": "success", "photos": ["/data/photo1.jpg", "/data/photo2.jpg"]}', '{"temperature": 15}', '温度异常：当前温度15℃，低于正常范围（20-60℃）', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441302', '550e8400-e29b-41d4-a716-446655441101', 'inspection', 5, 'unviewed', 'itemhistory', '["550e8400-e29b-41d4-a716-446655441002"]', 'item', '["70000000-0000-0000-0000-000000000002"]', '["70000000-0000-0000-0000-000000000002"]', NULL, '{"status": "warning", "check_result": "温度异常", "temperature": 85}', '{"temperature": 85}', '温度异常：当前温度85℃，高于正常范围（20-60℃），需要立即处理', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441303', '550e8400-e29b-41d4-a716-446655441102', 'inspection', 4, 'unviewed', 'itemhistory', '["550e8400-e29b-41d4-a716-446655441003"]', 'item', '["70000000-0000-0000-0000-000000000010"]', '["70000000-0000-0000-0000-000000000010"]', NULL, '{"humidity": 25, "status": "success", "equipment_status": "正常"}', '{"humidity": 25}', '湿度异常：当前湿度25%，低于正常范围（30-80%）', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441304', '550e8400-e29b-41d4-a716-446655441104', 'inspection', 7, 'unviewed', 'itemhistory', '["550e8400-e29b-41d4-a716-446655441003"]', 'item', '["70000000-0000-0000-0000-000000000010"]', '["70000000-0000-0000-0000-000000000010"]', NULL, '{"equipment_status_code": 1, "status": "success", "equipment_status": "正常"}', '{"equipment_status_code": 1}', '设备状态异常：设备状态码为1', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441305', '550e8400-e29b-41d4-a716-446655441103', 'gimbal', 6, 'unviewed', 'gimbalhistory', '["850e8400-e29b-41d4-a716-446655440060"]', 'gimbal', '["650e8400-e29b-41d4-a716-446655440050"]', NULL, '["650e8400-e29b-41d4-a716-446655440050"]', '{"status": 0, "angle": {"pan": 0, "tilt": 0, "zoom": 1}, "quality": "high"}', '{"status": 0}', '云台监控异常：云台状态为0（异常）', NOW(), NOW(), 'admin', 'admin', FALSE),
('550e8400-e29b-41d4-a716-446655441306', '550e8400-e29b-41d4-a716-446655441105', 'robot', 8, 'unviewed', 'robot_status', '["550e8400-e29b-41d4-a716-446655440020"]', 'robot', '["550e8400-e29b-41d4-a716-446655440020"]', NULL, NULL, '{"status": "error", "battery": 15, "location": {"x": 100.5, "y": 200.3}, "velocity": 0, "error_code": "E001", "error_message": "电机故障"}', '{"status": "error"}', '机器人车体异常：机器人状态为error（电机故障），需要立即处理', NOW(), NOW(), 'admin', 'admin', FALSE);

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
SELECT '3个用户, 1个厂区, 1个地图, 1个机器人, 19个设备, 4个智能传感器, 4个传感器记录, 1个云台, 2个云台任务, 4个预设点, 3个云台巡检项目, 6个关联关系, 2个云台日程, 2个云台记录, 1个车体控制器配置, 1个环境传感器配置, 1个双光云台配置, 1个电机状态配置, 1个激光雷达配置, 1个机械臂状态配置, 1个超声波状态配置, 1个深度相机配置, 1个导航控制器配置, 2个任务, 1个分组' as summary1;
SELECT '3条地图路网, 10个巡检点, 26个巡检项目' as summary2;
SELECT '6条任务日程, 3条任务记录, 3条任务结果, 5条巡检记录' as summary3;
SELECT '5条报警规则, 7条报警规则关联, 6条报警信息' as summary4;
SELECT '3条手动操作记录, 4条操作记录' as summary5;
