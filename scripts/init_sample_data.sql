-- 博实智能巡检平台 - 示例数据初始化SQL
USE boshirobot;

-- 清空所有示例数据（如果存在）
-- 注意：使用 SET FOREIGN_KEY_CHECKS = 0 来禁用外键检查，以便可以按任意顺序删除数据
SET FOREIGN_KEY_CHECKS = 0;

-- 按外键依赖顺序删除数据（从子表到父表）
DELETE FROM tb_alarminfo;
DELETE FROM tb_alarmrule;
DELETE FROM tb_taskresult;
DELETE FROM tb_itemhistory;
DELETE FROM tb_item;
DELETE FROM tb_taskhistory;
DELETE FROM tb_taskschedule;
DELETE FROM tb_task;
DELETE FROM tb_point;
DELETE FROM tb_mapnet;
DELETE FROM tb_robot_map;
DELETE FROM tb_robot;
DELETE FROM tb_gimbalhistory;
DELETE FROM tb_gimbalschedule;
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
INSERT INTO tb_users (
    id, 
    username, 
    password_hash, 
    role, 
    created_at, 
    updated_at,
    created_by
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'superadmin',
    '$2b$12$kRjLRFxYlP1B/cSdwWiyMuUyBhVO3JoKrnl2k9kQfwPvqbqxgG8mu',
    'super_admin',
    NOW(),
    NOW(),
    'system'
), (
    '550e8400-e29b-41d4-a716-446655440101',
    'admin',
    '$2b$12$aO5ac829bmhgt8.3Bszrq.ByPvri0qLi1fN9gGgmpShzSF3yGiqle',
    'admin',
    NOW(),
    NOW(),
    'system'
), (
    '550e8400-e29b-41d4-a716-446655440102',
    'operator',
    '$2b$12$iaUv0/mZ1YaPJIl3e9G48uac9xTPzUzuM7miyvP5MS7z4Kflmttvy',
    'operator',
    NOW(),
    NOW(),
    'system'
);

-- 插入示例厂区数据
INSERT INTO tb_factory (
    id,
    factory_name,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    '厂区一',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440001',
    '厂区二',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入示例地图数据
INSERT INTO tb_map (
    id,
    map_name,
    map_image_url,
    map_scale,
    map_center_x,
    map_center_y,
    factory_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440010',
    '厂区一地图',
    '/uploads/maps/factory1_map.png',
    1.0,
    100.0,
    100.0,
    '550e8400-e29b-41d4-a716-446655440000',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440011',
    '厂区二地图一',
    '/uploads/maps/factory2_map1.png',
    1.0,
    100.0,
    100.0,
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440012',
    '厂区二地图二',
    '/uploads/maps/factory2_map2.png',
    1.0,
    100.0,
    100.0,
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入示例地图路网数据
-- 厂区一地图路网
INSERT INTO tb_mapnet (
    id,
    map_id,
    map_net_type,
    map_net_properties,
    map_net_geometry,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440501',
    '550e8400-e29b-41d4-a716-446655440010',
    'point',
    '{"name": "导航点A", "type": "navigation"}',
    '{"x": 50.0, "y": 50.0}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440502',
    '550e8400-e29b-41d4-a716-446655440010',
    'line',
    '{"name": "巡检路径1", "width": 2, "color": "blue"}',
    '{"start": {"x": 50.0, "y": 50.0}, "end": {"x": 150.0, "y": 50.0}}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440503',
    '550e8400-e29b-41d4-a716-446655440010',
    'rect',
    '{"name": "禁区范围", "type": "restricted"}',
    '{"x": 80.0, "y": 80.0, "width": 40.0, "height": 30.0}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);

-- 插入示例机器人数据
INSERT INTO tb_robot (
    id,
    robot_name,
    robot_info,
    factory_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440020',
    '厂区一机器人001',
    '{"model": "BOSHI-RB-01", "battery": 100, "status": "idle"}',
    '550e8400-e29b-41d4-a716-446655440000',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440021',
    '厂区一机器人002',
    '{"model": "BOSHI-RB-02", "battery": 85, "status": "working"}',
    '550e8400-e29b-41d4-a716-446655440000',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440022',
    '厂区一机器人003',
    '{"model": "BOSHI-RB-03", "battery": 95, "status": "idle"}',
    '550e8400-e29b-41d4-a716-446655440000',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440023',
    '厂区一机器人004',
    '{"model": "BOSHI-RB-04", "battery": 90, "status": "idle"}',
    '550e8400-e29b-41d4-a716-446655440000',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440024',
    '厂区二机器人001',
    '{"model": "BOSHI-RB-05", "battery": 100, "status": "idle"}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440025',
    '厂区二机器人002',
    '{"model": "BOSHI-RB-06", "battery": 88, "status": "working"}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入机器人-地图关联数据
-- 厂区一：4个机器人都关联到1个地图
INSERT INTO tb_robot_map (
    id,
    robot_id,
    map_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440501',
    '550e8400-e29b-41d4-a716-446655440020',
    '550e8400-e29b-41d4-a716-446655440010',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440502',
    '550e8400-e29b-41d4-a716-446655440021',
    '550e8400-e29b-41d4-a716-446655440010',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440503',
    '550e8400-e29b-41d4-a716-446655440022',
    '550e8400-e29b-41d4-a716-446655440010',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440504',
    '550e8400-e29b-41d4-a716-446655440023',
    '550e8400-e29b-41d4-a716-446655440010',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440505',
    '550e8400-e29b-41d4-a716-446655440024',
    '550e8400-e29b-41d4-a716-446655440011',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440506',
    '550e8400-e29b-41d4-a716-446655440025',
    '550e8400-e29b-41d4-a716-446655440012',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入示例云台数据
INSERT INTO tb_gimbal (
    id,
    gimbal_name,
    map_id,
    enabled,
    ip_address,
    port,
    username,
    password,
    rtsp_main_url,
    rtsp_sub_url,
    channel,
    x_coordinate,
    y_coordinate,
    p_coordinate,
    t_coordinate,
    z_coordinate,
    f_coordinate,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440030',
    '云台001',
    '550e8400-e29b-41d4-a716-446655440010',
    TRUE,
    '192.168.1.110',
    554,
    'admin',
    'admin123',
    'rtsp://192.168.1.110:554/stream/main',
    'rtsp://192.168.1.110:554/stream/sub',
    1,
    15.0000,
    12.5000,
    0.0000,
    0.0000,
    0.0000,
    0.0000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440031',
    '云台002',
    '550e8400-e29b-41d4-a716-446655440010',
    TRUE,
    '192.168.1.111',
    8554,
    'operator',
    'securePass!',
    'rtsp://192.168.1.111:8554/live/main',
    'rtsp://192.168.1.111:8554/live/sub',
    2,
    35.0000,
    18.7500,
    5.0000,
    2.5000,
    1.0000,
    0.5000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440032',
    '云台003',
    NULL,
    TRUE,
    '10.0.0.50',
    554,
    'guest',
    'guest123',
    'rtsp://10.0.0.50:554/main',
    NULL,
    1,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例云台任务数据
INSERT INTO tb_gimbaltask (
    id,
    task_name,
    gimbal_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440040',
    '云台任务-A',
    '550e8400-e29b-41d4-a716-446655440030',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440041',
    '云台任务-B',
    '550e8400-e29b-41d4-a716-446655440031',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440042',
    '云台任务-C',
    '550e8400-e29b-41d4-a716-446655440032',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例云台巡检项目数据
INSERT INTO tb_gimbal_inspection_project (
    id,
    task_name,
    gimbaltask_id,
    sort_order,
    x_coordinate,
    y_coordinate,
    zoom_level,
    focus,
    aperture,
    shutter,
    backlight_compensation,
    wide_dynamic,
    strong_light_suppression,
    fill_light,
    detection_type,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '650e8400-e29b-41d4-a716-446655440040',
    '全景拍摄项目',
    '550e8400-e29b-41d4-a716-446655440040',
    0,
    0.0000,
    0.0000,
    1.0000,
    0.5000,
    40,
    60,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    '可见光图片',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '650e8400-e29b-41d4-a716-446655440041',
    '监控录像项目',
    '550e8400-e29b-41d4-a716-446655440041',
    0,
    0.0000,
    0.0000,
    2.5000,
    1.2000,
    55,
    30,
    TRUE,
    FALSE,
    TRUE,
    TRUE,
    '可见光视频',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '650e8400-e29b-41d4-a716-446655440042',
    '定点观察项目',
    '550e8400-e29b-41d4-a716-446655440042',
    0,
    0.0000,
    0.0000,
    4.0000,
    0.8000,
    35,
    15,
    FALSE,
    TRUE,
    TRUE,
    TRUE,
    '热成像图片',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例云台日程数据
INSERT INTO tb_gimbalschedule (
    id,
    gimbaltask_id,
    schedule_name,
    start_date,
    end_date,
    enabled,
    cycle_type,
    cycle_config,
    time_mode,
    time_config,
    frequency_display,
    time_display_start,
    time_display_end,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440050',
    '550e8400-e29b-41d4-a716-446655440040',
    '云台1每天巡检',
    '2025-01-01',
    '2025-12-31',
    TRUE,
    'daily',
    NULL,
    'custom',
    '{"customTimes": ["08:00", "12:00", "18:00"]}',
    '每天',
    '08:00:00',
    '18:00:00',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440051',
    '550e8400-e29b-41d4-a716-446655440041',
    '云台2间隔巡检',
    '2025-01-01',
    '2025-12-31',
    TRUE,
    'daily',
    NULL,
    'interval',
    '{"intervalTimeRange": ["08:00", "18:00"], "intervalMinutes": 30}',
    '每天',
    '08:00:00',
    '18:00:00',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440052',
    '550e8400-e29b-41d4-a716-446655440042',
    '云台3每周巡检',
    '2025-01-01',
    '2025-12-31',
    TRUE,
    'weekly',
    '{"selectedWeeks": [1, 3, 5]}',
    'custom',
    '{"customTimes": ["09:00", "15:00"]}',
    '每周一/三/五',
    '09:00:00',
    '15:00:00',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例云台记录数据
INSERT INTO tb_gimbalhistory (
    id,
    inspection_project_id,
    record_data,
    media_url,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440060',
    '650e8400-e29b-41d4-a716-446655440040',
    '{"angle": {"pan": 0, "tilt": 0, "zoom": 1}, "status": "completed", "quality": "high"}',
    '/media/gimbal/2024/01/panorama_001.jpg',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440061',
    '650e8400-e29b-41d4-a716-446655440041',
    '{"angle": {"pan": 45, "tilt": -30, "zoom": 2}, "status": "completed", "duration": 30}',
    '/media/gimbal/2024/01/monitor_001.mp4',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440062',
    '650e8400-e29b-41d4-a716-446655440042',
    '{"angle": {"pan": 90, "tilt": 0, "zoom": 5}, "status": "completed", "quality": "medium"}',
    '/media/gimbal/2024/01/observation_001.jpg',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440063',
    '650e8400-e29b-41d4-a716-446655440040',
    '{"angle": {"pan": 180, "tilt": 10, "zoom": 1}, "status": "completed", "quality": "high"}',
    '/media/gimbal/2024/01/panorama_002.jpg',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);

-- 插入示例巡检点数据（必须在tb_device之前插入，因为tb_device引用tb_point）
INSERT INTO tb_point (
    id,
    point_name,
    map_id,
    enabled,
    x_coordinate,
    y_coordinate,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '60000000-0000-0000-0000-000000000001',
    '巡检点001',
    '550e8400-e29b-41d4-a716-446655440010',
    TRUE,
    10.0000,
    10.0000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '60000000-0000-0000-0000-000000000002',
    '巡检点002',
    '550e8400-e29b-41d4-a716-446655440010',
    TRUE,
    20.0000,
    20.0000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '60000000-0000-0000-0000-000000000003',
    '巡检点003',
    '550e8400-e29b-41d4-a716-446655440010',
    TRUE,
    30.0000,
    30.0000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);

-- 插入示例设备数据（关联到巡检点）
-- 为巡检点001创建设备
INSERT INTO tb_device (
    id,
    device_name,
    device_params,
    point_id,
    enabled,
    x_coordinate,
    y_coordinate,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440070',
    '温湿度传感器001',
    '{"type": "temperature_humidity", "model": "DHT22", "range": {"temp": "-40~80", "humidity": "0~100"}, "accuracy": {"temp": "±0.5", "humidity": "±2%"}}',
    '60000000-0000-0000-0000-000000000001',
    TRUE,
    12.0000,
    8.0000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440071',
    '气体检测仪001',
    '{"type": "gas_detector", "model": "MQ-135", "detect_gas": ["CO", "NH3", "NOx", "smoke"], "voltage": "5V"}',
    '60000000-0000-0000-0000-000000000001',
    TRUE,
    28.5000,
    14.3000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440072',
    '红外热像仪001',
    '{"type": "thermal_camera", "model": "FLIR-E8", "resolution": "320x240", "temp_range": "-20~250", "accuracy": "±2°C"}',
    '60000000-0000-0000-0000-000000000002',
    TRUE,
    45.7500,
    21.9000,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440073',
    '可见光相机001',
    '{"type": "visible_camera", "model": "Hikvision-DS-2CD", "resolution": "1920x1080", "format": "JPEG"}',
    '60000000-0000-0000-0000-000000000001',
    TRUE,
    15.0000,
    10.0000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440074',
    '振动传感器001',
    '{"type": "vibration", "model": "ADXL345", "range": "0~100mm/s", "accuracy": "±0.1mm/s"}',
    '60000000-0000-0000-0000-000000000003',
    TRUE,
    30.0000,
    10.0000,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);

-- 插入示例巡检项目数据（必须在tb_device之后插入，因为tb_item引用tb_device）
INSERT INTO tb_item (
    id,
    item_name,
    item_info,
    device_id,
    enabled,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '70000000-0000-0000-0000-000000000001',
    '温度检测',
    '{"type": "temperature", "unit": "℃", "threshold": {"min": -10, "max": 50}}',
    '550e8400-e29b-41d4-a716-446655440070',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '70000000-0000-0000-0000-000000000002',
    '湿度检测',
    '{"type": "humidity", "unit": "%RH", "threshold": {"min": 30, "max": 80}}',
    '550e8400-e29b-41d4-a716-446655440070',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '70000000-0000-0000-0000-000000000003',
    '气体浓度检测',
    '{"type": "gas_concentration", "unit": "ppm", "threshold": {"co": 50, "nh3": 25}}',
    '550e8400-e29b-41d4-a716-446655440071',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '70000000-0000-0000-0000-000000000005',
    '热成像检测',
    '{"type": "thermal_imaging", "format": "image", "resolution": "320x240"}',
    '550e8400-e29b-41d4-a716-446655440072',
    TRUE,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
), (
    '70000000-0000-0000-0000-000000000006',
    '可见光拍照',
    '{"type": "photo", "format": "JPEG", "resolution": "1920x1080"}',
    '550e8400-e29b-41d4-a716-446655440073',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '70000000-0000-0000-0000-000000000007',
    '振动检测',
    '{"type": "vibration", "unit": "mm/s", "threshold": {"max": 50}}',
    '550e8400-e29b-41d4-a716-446655440074',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '70000000-0000-0000-0000-000000000010',
    '设备状态检查',
    '{"type": "equipment_status", "check_items": ["power", "connection", "function"]}',
    '550e8400-e29b-41d4-a716-446655440070',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '70000000-0000-0000-0000-000000000013',
    '清洁度检查',
    '{"type": "cleanliness", "check_items": ["surface", "dust", "debris"]}',
    '550e8400-e29b-41d4-a716-446655440070',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '70000000-0000-0000-0000-000000000014',
    '照明检查',
    '{"type": "lighting", "check_items": ["brightness", "function", "status"]}',
    '550e8400-e29b-41d4-a716-446655440070',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);

-- 插入示例车体控制器配置数据
INSERT INTO cfg_vehicle_controller (
    id,
    vehicle_model,
    wheel_diameter,
    reduction_ratio,
    wheelbase,
    track_width,
    max_linear_velocity,
    max_angular_velocity,
    serial_configs,
    ethernet_configs,
    controller_version,
    remote_upgrade_enabled,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440090',
    '四轮差速',
    430.00,
    50,
    780.00,
    1000.00,
    0.800,
    0.100,
    '[
        {
            "module_index": 1,
            "station_number": 1,
            "baud_rate": 115200,
            "function_code": 1,
            "enabled": true
        },
        {
            "module_index": 2,
            "station_number": 2,
            "baud_rate": 115200,
            "function_code": 2,
            "enabled": true
        },
        {
            "module_index": 3,
            "station_number": 3,
            "baud_rate": 115200,
            "function_code": 3,
            "enabled": false
        },
        {
            "module_index": 4,
            "station_number": 4,
            "baud_rate": 115200,
            "function_code": 4,
            "enabled": false
        }
    ]',
    '[
        {
            "module_index": 1,
            "ip_address": "192.168.1.100",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.1.1",
            "port": 8080,
            "baud_rate": 115200,
            "communication_mode": "server",
            "enabled": true
        },
        {
            "module_index": 2,
            "ip_address": "192.168.1.101",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.1.1",
            "port": 8081,
            "baud_rate": 115200,
            "communication_mode": "client",
            "enabled": true
        }
    ]',
    '1.232',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440091',
    '双轮差速',
    350.00,
    30,
    600.00,
    800.00,
    1.200,
    0.150,
    '[
        {
            "module_index": 1,
            "station_number": 1,
            "baud_rate": 9600,
            "function_code": 1,
            "enabled": true
        },
        {
            "module_index": 2,
            "station_number": 2,
            "baud_rate": 9600,
            "function_code": 2,
            "enabled": false
        },
        {
            "module_index": 3,
            "station_number": 3,
            "baud_rate": 9600,
            "function_code": 3,
            "enabled": false
        },
        {
            "module_index": 4,
            "station_number": 4,
            "baud_rate": 9600,
            "function_code": 4,
            "enabled": false
        }
    ]',
    '[
        {
            "module_index": 1,
            "ip_address": "192.168.2.100",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.2.1",
            "port": 9000,
            "baud_rate": 9600,
            "communication_mode": "server",
            "enabled": true
        },
        {
            "module_index": 2,
            "ip_address": "192.168.2.101",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.2.1",
            "port": 9001,
            "baud_rate": 9600,
            "communication_mode": "client",
            "enabled": false
        }
    ]',
    '1.200',
    FALSE,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例环境传感器配置数据
INSERT INTO cfg_environment_sensor (
    id,
    station_number,
    baud_rate,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440100',
    1,
    115200,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440101',
    2,
    9600,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440102',
    3,
    19200,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例双光云台配置数据
INSERT INTO cfg_dual_ptz (
    id,
    ptz_ip,
    subnet_mask,
    gateway,
    operating_speed,
    fill_light_enabled,
    wiper_enabled,
    auto_focus_enabled,
    backlight_compensation_enabled,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440110',
    '192.168.1.100',
    '255.255.255.0',
    '192.168.1.1',
    100,
    TRUE,
    FALSE,
    TRUE,
    FALSE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440111',
    '192.168.1.101',
    '255.255.255.0',
    '192.168.1.1',
    150,
    FALSE,
    TRUE,
    TRUE,
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440112',
    '192.168.1.102',
    '255.255.255.0',
    '192.168.1.1',
    80,
    TRUE,
    TRUE,
    FALSE,
    FALSE,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例电机状态配置数据
INSERT INTO cfg_motor_status (
    id,
    motor_id,
    baud_rate,
    tpdo_config,
    rpdo_config,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440120',
    1,
    115200,
    '{
        "enabled": true,
        "transmission_type": "synchronous",
        "inhibit_time": 0,
        "event_timer": 0,
        "sync_start_value": 0
    }',
    '{
        "enabled": true,
        "transmission_type": "synchronous",
        "inhibit_time": 0,
        "event_timer": 0,
        "sync_start_value": 0
    }',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440121',
    2,
    9600,
    '{
        "enabled": true,
        "transmission_type": "asynchronous",
        "inhibit_time": 100,
        "event_timer": 1000,
        "sync_start_value": 1
    }',
    '{
        "enabled": true,
        "transmission_type": "asynchronous",
        "inhibit_time": 100,
        "event_timer": 1000,
        "sync_start_value": 1
    }',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440122',
    3,
    19200,
    '{
        "enabled": false,
        "transmission_type": "synchronous",
        "inhibit_time": 50,
        "event_timer": 500,
        "sync_start_value": 0
    }',
    '{
        "enabled": true,
        "transmission_type": "synchronous",
        "inhibit_time": 50,
        "event_timer": 500,
        "sync_start_value": 0
    }',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例激光雷达配置数据
INSERT INTO cfg_lidar (
    id,
    lidar_ip,
    subnet_mask,
    gateway,
    lidar_port,
    scan_frequency_rpm,
    x_coordinate,
    y_coordinate,
    z_coordinate,
    scan_range_min,
    scan_range_max,
    scan_distance_min,
    scan_distance_max,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440130',
    '192.168.1.100',
    '255.255.255.0',
    '192.168.1.1',
    8080,
    2000,
    49.10,
    23.20,
    34.90,
    0.00,
    360.00,
    0.00,
    100.00,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440131',
    '192.168.1.101',
    '255.255.255.0',
    '192.168.1.1',
    8081,
    1500,
    50.00,
    25.00,
    35.00,
    0.00,
    180.00,
    0.00,
    50.00,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440132',
    '192.168.1.102',
    '255.255.255.0',
    '192.168.1.1',
    8082,
    3000,
    48.50,
    22.80,
    33.50,
    90.00,
    270.00,
    10.00,
    80.00,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例机械臂状态配置数据
INSERT INTO cfg_robot_arm (
    id,
    robot_arm_ip,
    subnet_mask,
    gateway,
    robot_arm_port,
    operating_speed,
    origin_coordinates,
    plane_coordinates,
    load_size,
    end_coordinates,
    tool_io,
    collision_detection_level,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440140',
    '192.168.1.100',
    '255.255.255.0',
    '192.168.1.1',
    8080,
    50,
    '[10, 20, 0, 5, -3, -180]',
    '[10, 20, 0, 5, -3, -180]',
    0.50,
    '[10, 20, 0, 5, -3, -180]',
    0,
    '中',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440141',
    '192.168.1.101',
    '255.255.255.0',
    '192.168.1.1',
    8081,
    75,
    '[15, 25, 5, 10, -5, -90]',
    '[15, 25, 5, 10, -5, -90]',
    1.20,
    '[15, 25, 5, 10, -5, -90]',
    128,
    '高',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440142',
    '192.168.1.102',
    '255.255.255.0',
    '192.168.1.1',
    8082,
    25,
    '[5, 15, -5, 0, 0, 0]',
    '[5, 15, -5, 0, 0, 0]',
    0.30,
    '[5, 15, -5, 0, 0, 0]',
    255,
    '低',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例超声波状态配置数据
INSERT INTO cfg_ultrasonic (
    id,
    ultrasonic_id,
    obstacle_avoidance_distance,
    deceleration_distance,
    baud_rate,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440150',
    1,
    800.00,
    1500.00,
    9600,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440151',
    2,
    1000.00,
    2000.00,
    19200,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440152',
    3,
    600.00,
    1200.00,
    115200,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例深度相机配置数据
INSERT INTO cfg_depth_camera (
    id,
    camera_type,
    resolution_width,
    resolution_height,
    frame_rate,
    depth_range_min,
    depth_range_max,
    depth_accuracy,
    camera_ip,
    camera_port,
    protocol,
    exposure_time,
    gain,
    white_balance,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440160',
    'RGB-D',
    640,
    480,
    30,
    0.10,
    10.00,
    0.0010,
    NULL,
    NULL,
    'USB',
    8500,
    1.50,
    'Auto',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440161',
    'ToF',
    1024,
    1024,
    30,
    0.25,
    5.46,
    0.0005,
    '192.168.1.200',
    8080,
    'Ethernet',
    10000,
    2.00,
    'Daylight',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440162',
    'Stereo',
    1920,
    1080,
    60,
    0.30,
    20.00,
    0.0020,
    '192.168.1.201',
    8081,
    'WiFi',
    12000,
    1.80,
    'Manual',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例导航控制器配置数据
INSERT INTO cfg_navigation_controller (
    id,
    module_group,
    ethernet_ip,
    subnet_mask,
    gateway,
    ethernet_port,
    baud_rate,
    deceleration_distance,
    stop_distance,
    max_linear_velocity,
    max_angular_velocity,
    acceleration,
    deceleration,
    expansion_coefficient,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440170',
    1,
    '192.168.1.100',
    '255.255.255.0',
    '192.168.1.1',
    8080,
    9600,
    800.00,
    1500.00,
    0.800,
    0.100,
    0.800,
    0.800,
    0.00,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440171',
    2,
    '192.168.1.101',
    '255.255.255.0',
    '192.168.1.1',
    8081,
    19200,
    1000.00,
    2000.00,
    1.000,
    0.150,
    1.000,
    1.000,
    0.50,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440172',
    1,
    '192.168.1.102',
    '255.255.255.0',
    '192.168.1.1',
    8082,
    115200,
    600.00,
    1200.00,
    0.500,
    0.080,
    0.500,
    0.500,
    1.00,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例智能传感器数据
INSERT INTO tb_sensor (
    id,
    device_id,
    sensor_name,
    sensor_params,
    enabled,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440080',
    '550e8400-e29b-41d4-a716-446655440070',
    '温度传感器',
    '{"unit": "℃", "range": "-40~80", "accuracy": "±0.5", "sampling_rate": "1Hz"}',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440081',
    '550e8400-e29b-41d4-a716-446655440070',
    '湿度传感器',
    '{"unit": "%RH", "range": "0~100", "accuracy": "±2%", "sampling_rate": "1Hz"}',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440082',
    '550e8400-e29b-41d4-a716-446655440071',
    'CO浓度传感器',
    '{"unit": "ppm", "range": "0~1000", "alarm_threshold": 50, "response_time": "30s"}',
    TRUE,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440083',
    '550e8400-e29b-41d4-a716-446655440072',
    '热成像传感器',
    '{"resolution": "320x240", "frame_rate": "9Hz", "temp_range": "-20~250", "accuracy": "±2°C"}',
    TRUE,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例传感器记录数据
INSERT INTO tb_sensorhistory (
    id,
    sensor_id,
    record_data,
    file_url,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440100',
    '550e8400-e29b-41d4-a716-446655440080',
    '{"temperature": 25.5, "unit": "℃", "status": "normal", "timestamp": 1704067200}',
    '/data/sensor/2024/01/temp_001.csv',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440101',
    '550e8400-e29b-41d4-a716-446655440081',
    '{"humidity": 65.2, "unit": "%RH", "status": "normal", "timestamp": 1704067200}',
    '/data/sensor/2024/01/humidity_001.csv',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440102',
    '550e8400-e29b-41d4-a716-446655440082',
    '{"co_concentration": 35, "unit": "ppm", "status": "normal", "alarm": false, "timestamp": 1704067260}',
    '/data/sensor/2024/01/co_001.json',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440103',
    '550e8400-e29b-41d4-a716-446655440083',
    '{"max_temp": 45.8, "min_temp": 18.2, "avg_temp": 28.5, "unit": "℃", "status": "completed"}',
    '/data/sensor/2024/01/thermal_001.jpg',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例任务数据
-- 插入示例任务数据（厂区一-机器人一的两个任务）
INSERT INTO tb_task (
    id,
    task_name,
    robot_id,
    task_items,
    task_order,
    task_res_prior,
    task_int_prior,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440021',
    '任务一：环境监测',
    '550e8400-e29b-41d4-a716-446655440020',
    '["70000000-0000-0000-0000-000000000001", "70000000-0000-0000-0000-000000000002", "70000000-0000-0000-0000-000000000003"]',
    1,
    5,
    3,
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440022',
    '任务二：设备巡检',
    '550e8400-e29b-41d4-a716-446655440020',
    '["70000000-0000-0000-0000-000000000005", "70000000-0000-0000-0000-000000000006", "70000000-0000-0000-0000-000000000007"]',
    2,
    5,
    3,
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入示例任务日程数据
INSERT INTO tb_taskschedule (
    id,
    task_id,
    schedule_name,
    start_date,
    end_date,
    enabled,
    item_count,
    cycle_type,
    cycle_config,
    time_mode,
    time_config,
    frequency_display,
    time_display_start,
    time_display_end,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440601',
    '550e8400-e29b-41d4-a716-446655440021',
    '每日巡检任务',
    '2024-01-01',
    '2024-12-31',
    1,
    5,
    'daily',
    NULL,
    'custom',
    '{"customTimes": ["08:00", "14:00", "18:00"]}',
    '每天',
    '08:00:00',
    '18:00:00',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    0
), (
    '550e8400-e29b-41d4-a716-446655440602',
    '550e8400-e29b-41d4-a716-446655440021',
    '每周一巡检任务',
    '2024-01-01',
    '2024-12-31',
    1,
    4,
    'weekly',
    '{"selectedWeeks": [1]}',
    'custom',
    '{"customTimes": ["14:00"]}',
    '每周一',
    '14:00:00',
    '14:00:00',
    NOW(),
    NOW(),
    'admin',
    'admin',
    0
);

-- 插入示例任务记录数据
INSERT INTO tb_taskhistory (
    id,
    task_id,
    record_start_time,
    record_end_time,
    record_status,
    record_batch,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440801',
    '550e8400-e29b-41d4-a716-446655440021',
    '2024-01-15T08:00:00',
    '2024-01-15T08:30:00',
    'completed',
    1,
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440802',
    '550e8400-e29b-41d4-a716-446655440021',
    '2024-01-15T14:00:00',
    '2024-01-15T14:28:00',
    'completed',
    2,
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440803',
    '550e8400-e29b-41d4-a716-446655440021',
    '2024-01-16T09:00:00',
    NULL,
    'running',
    3,
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例任务结果数据
INSERT INTO tb_taskresult (
    id,
    taskhistory_id,
    record_batch,
    result_point_id,
    result_item_id,
    result_file_url,
    result_collect_time,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440901',
    '550e8400-e29b-41d4-a716-446655440801',
    1,
    '60000000-0000-0000-0000-000000000003',
    '70000000-0000-0000-0000-000000000010',
    '/uploads/results/task_001_batch_001.json',
    '2024-01-15T08:30:00',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440902',
    '550e8400-e29b-41d4-a716-446655440802',
    2,
    '60000000-0000-0000-0000-000000000003',
    '70000000-0000-0000-0000-000000000010',
    '/uploads/results/task_001_batch_002.json',
    '2024-01-15T14:28:00',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入示例巡检记录数据
INSERT INTO tb_itemhistory (
    id,
    taskhistory_id,
    item_id,
    item_result,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655441001',
    '550e8400-e29b-41d4-a716-446655440801',
    '70000000-0000-0000-0000-000000000001',
    '{"status": "success", "photos": ["/data/photo1.jpg", "/data/photo2.jpg"]}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441002',
    '550e8400-e29b-41d4-a716-446655440801',
    '70000000-0000-0000-0000-000000000002',
    '{"status": "success", "check_result": "正常"}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441003',
    '550e8400-e29b-41d4-a716-446655440801',
    '70000000-0000-0000-0000-000000000010',
    '{"status": "success", "equipment_status": "正常"}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441004',
    '550e8400-e29b-41d4-a716-446655440802',
    '70000000-0000-0000-0000-000000000013',
    '{"status": "success", "cleanliness": "良好"}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441005',
    '550e8400-e29b-41d4-a716-446655440802',
    '70000000-0000-0000-0000-000000000014',
    '{"status": "success", "lighting": "正常"}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入示例报警规则数据
INSERT INTO tb_alarmrule (
    id,
    rule_name,
    business_type,
    business_id,
    alarm_param,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655441101',
    '温度异常报警',
    'inspection_item',
    '550e8400-e29b-41d4-a716-446655440012',
    '{"threshold": 40, "operator": "gt", "level": "warning"}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441102',
    '设备故障报警',
    'inspection_item',
    '70000000-0000-0000-0000-000000000010',
    '{"check_field": "equipment_status", "expected": "正常", "level": "critical"}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441201',
    '云台角度异常报警',
    'gimbal_task',
    '550e8400-e29b-41d4-a716-446655440010',
    '{"angle_threshold": 180, "operator": "gt", "level": "warning"}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441202',
    '云台任务超时报警',
    'gimbal_task',
    '550e8400-e29b-41d4-a716-446655440010',
    '{"timeout_threshold": 300, "unit": "seconds", "level": "critical"}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441301',
    '传感器数据异常报警',
    'sensor',
    '550e8400-e29b-41d4-a716-446655440010',
    '{"data_range": {"min": 0, "max": 100}, "level": "warning"}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441302',
    '传感器离线报警',
    'sensor',
    '550e8400-e29b-41d4-a716-446655440010',
    '{"offline_threshold": 60, "unit": "seconds", "level": "critical"}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);

-- 插入示例报警信息数据
INSERT INTO tb_alarminfo (
    id,
    alarmrule_id,
    record_type,
    record_id,
    alarm_data,
    alarm_info,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655441201',
    '550e8400-e29b-41d4-a716-446655441102',
    'itemhistory',
    '550e8400-e29b-41d4-a716-446655441003',
    '{"actual_value": "正常", "expected_value": "正常", "match": true}',
    '设备状态正常，符合预期',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441401',
    '550e8400-e29b-41d4-a716-446655441201',
    'gimbalhistory',
    '550e8400-e29b-41d4-a716-446655440010',
    '{"actual_angle": 185, "threshold": 180, "exceeded": true}',
    '云台角度超出正常范围，当前角度185度',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441501',
    '550e8400-e29b-41d4-a716-446655441301',
    'sensorhistory',
    '550e8400-e29b-41d4-a716-446655440010',
    '{"actual_value": 105, "range": {"min": 0, "max": 100}, "exceeded": true}',
    '传感器数据超出正常范围，当前值105',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入手动操作记录测试数据
INSERT INTO tb_manual_operation (id, user_id, username, operation_time, operation_content, created_at, updated_at, created_by, updated_by, is_deleted) VALUES (
    '550e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440000', 'superadmin', '2024-01-15 09:30:00', '{"action": "manual_start", "target": "robot_001", "description": "手动启动机器人"}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE
), (
    '550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440010', 'admin', '2024-01-15 10:15:00', '{"action": "manual_stop", "target": "robot_002", "description": "手动停止机器人"}', NOW(), NOW(), 'admin', 'admin', FALSE
), (
    '550e8400-e29b-41d4-a716-446655440082', '550e8400-e29b-41d4-a716-446655440002', 'operator', '2024-01-15 11:00:00', '{"action": "manual_reset", "target": "gimbal_001", "description": "手动重置云台"}', NOW(), NOW(), 'operator', 'operator', FALSE
);

-- 插入操作记录测试数据
INSERT INTO tb_operation_record (id, user_id, username, operation_time, operation_content, created_at, updated_at, created_by, updated_by, is_deleted) VALUES (
    '550e8400-e29b-41d4-a716-446655440090', '550e8400-e29b-41d4-a716-446655440000', 'superadmin', '2024-01-15 08:00:00', '{"action": "login", "ip": "192.168.1.100", "description": "用户登录"}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE
), (
    '550e8400-e29b-41d4-a716-446655440091', '550e8400-e29b-41d4-a716-446655440010', 'admin', '2024-01-15 08:30:00', '{"action": "create_task", "target": "task_001", "description": "创建新任务"}', NOW(), NOW(), 'admin', 'admin', FALSE
), (
    '550e8400-e29b-41d4-a716-446655440092', '550e8400-e29b-41d4-a716-446655440002', 'operator', '2024-01-15 09:00:00', '{"action": "update_config", "target": "robot_config", "description": "更新机器人配置"}', NOW(), NOW(), 'operator', 'operator', FALSE
), (
    '550e8400-e29b-41d4-a716-446655440093', '550e8400-e29b-41d4-a716-446655440000', 'superadmin', '2024-01-15 12:00:00', '{"action": "logout", "ip": "192.168.1.100", "description": "用户登出"}', NOW(), NOW(), 'superadmin', 'superadmin', FALSE
);

SELECT '========== 操作记录模块 ==========' as divider1;
SELECT '手动操作记录表: tb_manual_operation' as table1;
SELECT '操作记录表: tb_operation_record' as table2;
SELECT '========== 示例数据统计 ==========' as divider2;
SELECT '3个用户, 2个厂区, 3个地图, 6个机器人, 3个设备, 4个智能传感器, 3个传感器日程, 4个传感器记录, 3个云台, 3个云台任务, 3个云台日程, 4个云台记录, 2个车体控制器配置, 3个环境传感器配置, 3个双光云台配置, 3个电机状态配置, 3个激光雷达配置, 3个机械臂状态配置, 3个超声波状态配置, 3个深度相机配置, 3个导航控制器配置, 1个任务' as summary1;
SELECT '3条地图路网, 4个巡检点, 7个巡检项目' as summary2;
SELECT '2条任务日程, 3条任务记录, 3条任务结果, 5条巡检记录' as summary3;
SELECT '2条报警规则, 1条报警信息' as summary4;
SELECT '3条手动操作记录, 4条操作记录' as summary5;
