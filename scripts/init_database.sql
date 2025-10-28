-- 博实智能巡检平台 - 数据库初始化SQL
-- 创建数据库
CREATE DATABASE IF NOT EXISTS boshirobot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE boshirobot;

-- 删除现有表（如果存在）- 按外键依赖顺序删除
DROP TABLE IF EXISTS tb_alarminfo;
DROP TABLE IF EXISTS tb_alarmrule;
DROP TABLE IF EXISTS tb_taskresult;
DROP TABLE IF EXISTS tb_itemhistory;
DROP TABLE IF EXISTS tb_point_item;  -- 旧的中间表，需要先删除
DROP TABLE IF EXISTS tb_item;
DROP TABLE IF EXISTS tb_taskhistory;
DROP TABLE IF EXISTS tb_taskschedule;
DROP TABLE IF EXISTS tb_task;
DROP TABLE IF EXISTS tb_point;
DROP TABLE IF EXISTS tb_mapnet;
DROP TABLE IF EXISTS tb_robot;
DROP TABLE IF EXISTS tb_gimbalhistory;
DROP TABLE IF EXISTS tb_gimbalschedule;
DROP TABLE IF EXISTS tb_gimbaltask;
DROP TABLE IF EXISTS tb_gimbal;
DROP TABLE IF EXISTS tb_sensorhistory;
DROP TABLE IF EXISTS tb_sensorschedule;
DROP TABLE IF EXISTS tb_sensor;
DROP TABLE IF EXISTS tb_device;
DROP TABLE IF EXISTS cfg_vehicle_controller;
DROP TABLE IF EXISTS cfg_environment_sensor;
DROP TABLE IF EXISTS cfg_dual_ptz;
DROP TABLE IF EXISTS cfg_motor_status;
DROP TABLE IF EXISTS cfg_lidar;
DROP TABLE IF EXISTS cfg_robot_arm;
DROP TABLE IF EXISTS cfg_ultrasonic;
DROP TABLE IF EXISTS cfg_depth_camera;
DROP TABLE IF EXISTS cfg_navigation_controller;
DROP TABLE IF EXISTS tb_map;
DROP TABLE IF EXISTS tb_factory;
DROP TABLE IF EXISTS tb_sessions;
DROP TABLE IF EXISTS tb_users;

-- 创建用户表
CREATE TABLE tb_users (
    id VARCHAR(36) PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    mobile VARCHAR(20) NULL COMMENT '手机号',
    email VARCHAR(100) NULL COMMENT '邮箱',
    role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色: super_admin/admin/operator/viewer/user',
    last_login_at DATETIME NULL COMMENT '最后登录时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_is_deleted (is_deleted),
    INDEX idx_mobile (mobile),
    INDEX idx_email (email)
    -- 注意：不设置唯一约束，唯一性检查由应用层处理（只检查is_deleted=false的记录）
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 创建会话表
CREATE TABLE tb_sessions (
    id VARCHAR(36) PRIMARY KEY COMMENT '会话ID',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    token VARCHAR(500) NOT NULL UNIQUE COMMENT '会话令牌',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (user_id) REFERENCES tb_users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表';

-- 创建厂区表
CREATE TABLE tb_factory (
    id VARCHAR(36) PRIMARY KEY COMMENT '厂区ID',
    factory_name VARCHAR(100) NOT NULL COMMENT '厂区名称',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_factory_name (factory_name),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='厂区表';

-- 创建地图表
CREATE TABLE tb_map (
    id VARCHAR(36) PRIMARY KEY COMMENT '地图ID',
    map_name VARCHAR(100) NOT NULL COMMENT '地图名称',
    map_image_url VARCHAR(500) NULL COMMENT '图片地址',
    map_scale DECIMAL(10,6) NULL COMMENT '比例尺',
    map_center_x DECIMAL(15,6) NULL COMMENT '中心点横坐标',
    map_center_y DECIMAL(15,6) NULL COMMENT '中心点纵坐标',
    factory_id VARCHAR(36) NULL COMMENT '厂区ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_map_name (map_name),
    INDEX idx_factory_id (factory_id),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_map_name_active (map_name, is_deleted),
    FOREIGN KEY (factory_id) REFERENCES tb_factory(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='地图表';

-- 创建地图路网表
CREATE TABLE tb_mapnet (
    id VARCHAR(36) PRIMARY KEY COMMENT '路网元素ID',
    map_id VARCHAR(36) NOT NULL COMMENT '所属地图ID',
    map_net_type VARCHAR(50) NOT NULL COMMENT '元素类型',
    map_net_properties JSON NULL COMMENT '路网元素属性',
    map_net_geometry JSON NULL COMMENT '路网元素地理信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE CASCADE,
    INDEX idx_map_id (map_id),
    INDEX idx_map_net_type (map_net_type),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='地图路网表';

-- 创建机器人表
CREATE TABLE tb_robot (
    id VARCHAR(36) PRIMARY KEY COMMENT '机器人ID',
    robot_name VARCHAR(100) NOT NULL COMMENT '机器人名称',
    robot_info JSON NULL COMMENT '机器人信息',
    map_id VARCHAR(36) NOT NULL COMMENT '地图ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_robot_name (robot_name),
    INDEX idx_map_id (map_id),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_robot_name_active (robot_name, is_deleted),
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='机器人表';

-- 创建云台表
CREATE TABLE tb_gimbal (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台ID',
    gimbal_name VARCHAR(100) NOT NULL COMMENT '云台名称',
    gimbal_params JSON NULL COMMENT '云台参数',
    map_id VARCHAR(36) NULL COMMENT '地图ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_gimbal_name (gimbal_name),
    INDEX idx_map_id (map_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_gimbal_name_active (gimbal_name, is_deleted),
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台表';

-- 创建云台任务表
CREATE TABLE tb_gimbaltask (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台任务ID',
    task_name VARCHAR(100) NOT NULL COMMENT '云台任务名称',
    angle_params JSON NULL COMMENT '角度参数',
    task_type VARCHAR(20) NOT NULL COMMENT '任务类别：image/video',
    gimbal_id VARCHAR(36) NOT NULL COMMENT '所属云台ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_task_name (task_name),
    INDEX idx_task_type (task_type),
    INDEX idx_gimbal_id (gimbal_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_task_name_active (task_name, is_deleted),
    FOREIGN KEY (gimbal_id) REFERENCES tb_gimbal(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台任务表';

-- 创建云台日程表
CREATE TABLE tb_gimbalschedule (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台日程ID',
    schedule_type VARCHAR(50) NOT NULL COMMENT '云台日程类型',
    schedule_is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '云台日程是否激活',
    gimbaltask_id VARCHAR(36) NOT NULL COMMENT '关联云台任务ID',
    schedule_param JSON NULL COMMENT '日程参数',
    set_time INT NOT NULL COMMENT '设置时间（Unix时间戳）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_schedule_type (schedule_type),
    INDEX idx_schedule_is_active (schedule_is_active),
    INDEX idx_gimbaltask_id (gimbaltask_id),
    INDEX idx_set_time (set_time),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (gimbaltask_id) REFERENCES tb_gimbaltask(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台日程表';

-- 创建云台记录表
CREATE TABLE tb_gimbalhistory (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台记录ID',
    gimbaltask_id VARCHAR(36) NOT NULL COMMENT '关联云台任务ID',
    record_data JSON NULL COMMENT '记录数据',
    media_url VARCHAR(500) NULL COMMENT '图像/视频链接',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_gimbaltask_id (gimbaltask_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (gimbaltask_id) REFERENCES tb_gimbaltask(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台记录表';

-- 创建设备表
CREATE TABLE tb_device (
    id VARCHAR(36) PRIMARY KEY COMMENT '设备ID',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_params JSON NULL COMMENT '设备参数',
    map_id VARCHAR(36) NULL COMMENT '地图ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_device_name (device_name),
    INDEX idx_map_id (map_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_device_name_active (device_name, is_deleted),
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备表';

-- 创建车体控制器配置表
CREATE TABLE cfg_vehicle_controller (
    id VARCHAR(36) PRIMARY KEY COMMENT '车体控制器ID',
    
    -- 车体基础参数
    vehicle_model VARCHAR(50) NOT NULL COMMENT '车体模型：双轮差速/四轮差速/四驱四转/单舵轮/双舵轮',
    wheel_diameter DECIMAL(8,2) NOT NULL COMMENT '车轮直径(mm)',
    reduction_ratio INT NOT NULL COMMENT '车体减速比',
    wheelbase DECIMAL(8,2) NOT NULL COMMENT '车体轴距(mm)',
    track_width DECIMAL(8,2) NOT NULL COMMENT '车体轮距(mm)',
    max_linear_velocity DECIMAL(8,3) NOT NULL COMMENT '车体最大线速度(m/s)',
    max_angular_velocity DECIMAL(8,3) NOT NULL COMMENT '车体最大角速度(rad/s)',
    
    -- 串口通讯配置（JSON数组，支持4组）
    serial_configs JSON NOT NULL COMMENT '串口通讯配置数组',
    
    -- 以太网通讯配置（JSON数组，支持2组）
    ethernet_configs JSON NOT NULL COMMENT '以太网通讯配置数组',
    
    -- 控制器管理
    controller_version VARCHAR(20) NOT NULL COMMENT '控制器版本',
    remote_upgrade_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '远程升级是否开启',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_vehicle_model (vehicle_model),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车体控制器配置表';

-- 创建环境传感器配置表
CREATE TABLE cfg_environment_sensor (
    id VARCHAR(36) PRIMARY KEY COMMENT '环境传感器ID',
    
    -- 环境传感器参数
    station_number INT NOT NULL COMMENT '站号(1-255)',
    baud_rate INT NOT NULL COMMENT '波特率(9600-115200)',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_station_number (station_number),
    INDEX idx_baud_rate (baud_rate),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='环境传感器配置表';

-- 创建双光云台配置表
CREATE TABLE cfg_dual_ptz (
    id VARCHAR(36) PRIMARY KEY COMMENT '双光云台配置ID',
    
    -- 网络配置
    ptz_ip VARCHAR(15) NOT NULL COMMENT '云台IP地址',
    subnet_mask VARCHAR(15) NOT NULL DEFAULT '255.255.255.0' COMMENT '子网掩码',
    gateway VARCHAR(15) NOT NULL DEFAULT '192.168.1.1' COMMENT '网关地址',
    
    -- 运行参数
    operating_speed INT NOT NULL DEFAULT 100 COMMENT '运行速度(1-255)',
    fill_light_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '补光灯开启状态',
    wiper_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '雨刷开启状态',
    auto_focus_enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '自动对焦开启状态',
    backlight_compensation_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '逆光补偿开启状态',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_ptz_ip (ptz_ip),
    INDEX idx_operating_speed (operating_speed),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='双光云台配置表';

-- 创建电机状态配置表
CREATE TABLE cfg_motor_status (
    id VARCHAR(36) PRIMARY KEY COMMENT '电机状态配置ID',
    
    -- 电机参数
    motor_id INT NOT NULL COMMENT '电机ID(0-255)',
    baud_rate INT NOT NULL COMMENT '波特率(9600-115200)',
    tpdo_config JSON NULL COMMENT 'TPDO配置参数',
    rpdo_config JSON NULL COMMENT 'RPDO配置参数',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_motor_id (motor_id),
    INDEX idx_baud_rate (baud_rate),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电机状态配置表';

-- 创建激光雷达配置表
CREATE TABLE cfg_lidar (
    id VARCHAR(36) PRIMARY KEY COMMENT '激光雷达配置ID',
    
    -- 网络配置
    lidar_ip VARCHAR(15) NOT NULL COMMENT '激光雷达IP地址',
    subnet_mask VARCHAR(15) NOT NULL DEFAULT '255.255.255.0' COMMENT '子网掩码',
    gateway VARCHAR(15) NOT NULL DEFAULT '192.168.1.1' COMMENT '网关地址',
    lidar_port INT NOT NULL COMMENT '激光雷达端口(1-65535)',
    
    -- 雷达参数
    scan_frequency_rpm INT NOT NULL DEFAULT 2000 COMMENT '雷达扫描频率/转速Rpm',
    x_coordinate DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'X坐标',
    y_coordinate DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Y坐标',
    z_coordinate DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Z坐标',
    scan_range_min DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '扫描范围最小值(度)',
    scan_range_max DECIMAL(5,2) NOT NULL DEFAULT 360.00 COMMENT '扫描范围最大值(度)',
    scan_distance_min DECIMAL(8,2) NOT NULL DEFAULT 0.00 COMMENT '扫描距离最小值(米)',
    scan_distance_max DECIMAL(8,2) NOT NULL DEFAULT 100.00 COMMENT '扫描距离最大值(米)',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_lidar_ip (lidar_ip),
    INDEX idx_lidar_port (lidar_port),
    INDEX idx_scan_frequency (scan_frequency_rpm),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='激光雷达配置表';

-- 创建机械臂状态配置表
CREATE TABLE cfg_robot_arm (
    id VARCHAR(36) PRIMARY KEY COMMENT '机械臂状态配置ID',
    
    -- 网络配置
    robot_arm_ip VARCHAR(15) NOT NULL COMMENT '机械臂IP地址',
    subnet_mask VARCHAR(15) NOT NULL DEFAULT '255.255.255.0' COMMENT '子网掩码',
    gateway VARCHAR(15) NOT NULL DEFAULT '192.168.1.1' COMMENT '网关地址',
    robot_arm_port INT NOT NULL COMMENT '机械臂端口号(1-65535)',
    
    -- 机械臂参数
    operating_speed INT NOT NULL DEFAULT 50 COMMENT '机械臂运行速度(0-100%)',
    origin_coordinates JSON NOT NULL COMMENT '机械臂原点坐标',
    plane_coordinates JSON NOT NULL COMMENT '机械臂平面坐标',
    load_size DECIMAL(5,2) NOT NULL DEFAULT 0.50 COMMENT '机械臂负载大小(kg)',
    end_coordinates JSON NOT NULL COMMENT '机械臂末端坐标',
    tool_io INT NOT NULL DEFAULT 0 COMMENT '机械臂工具IO(0-255)',
    collision_detection_level ENUM('低', '中', '高') NOT NULL DEFAULT '中' COMMENT '机械臂碰撞检测级别',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_robot_arm_ip (robot_arm_ip),
    INDEX idx_robot_arm_port (robot_arm_port),
    INDEX idx_operating_speed (operating_speed),
    INDEX idx_collision_level (collision_detection_level),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='机械臂状态配置表';

-- 创建超声波状态配置表
CREATE TABLE cfg_ultrasonic (
    id VARCHAR(36) PRIMARY KEY COMMENT '超声波状态配置ID',
    
    -- 超声波参数
    ultrasonic_id INT NOT NULL COMMENT '超声波ID(0-255)',
    obstacle_avoidance_distance DECIMAL(8,2) NOT NULL DEFAULT 800.00 COMMENT '超声波避障距离(mm)',
    deceleration_distance DECIMAL(8,2) NOT NULL DEFAULT 1500.00 COMMENT '超声波减速距离(mm)',
    baud_rate INT NOT NULL DEFAULT 9600 COMMENT '超声波波特率(9600-115200)',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_ultrasonic_id (ultrasonic_id),
    INDEX idx_baud_rate (baud_rate),
    INDEX idx_obstacle_distance (obstacle_avoidance_distance),
    INDEX idx_deceleration_distance (deceleration_distance),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='超声波状态配置表';

-- 创建深度相机配置表
CREATE TABLE cfg_depth_camera (
    id VARCHAR(36) PRIMARY KEY COMMENT '深度相机配置ID',
    
    -- 相机基本信息
    camera_type ENUM('RGB-D', 'ToF', 'Stereo', 'Structured_Light') NOT NULL DEFAULT 'RGB-D' COMMENT '深度相机类型',
    resolution_width INT NOT NULL DEFAULT 640 COMMENT '分辨率宽度',
    resolution_height INT NOT NULL DEFAULT 480 COMMENT '分辨率高度',
    frame_rate INT NOT NULL DEFAULT 30 COMMENT '帧率(fps)',
    
    -- 深度参数
    depth_range_min DECIMAL(8,2) NOT NULL DEFAULT 0.10 COMMENT '最小深度范围(m)',
    depth_range_max DECIMAL(8,2) NOT NULL DEFAULT 10.00 COMMENT '最大深度范围(m)',
    depth_accuracy DECIMAL(8,4) NOT NULL DEFAULT 0.0010 COMMENT '深度精度(m)',
    
    -- 网络配置
    camera_ip VARCHAR(15) NULL COMMENT '相机IP地址',
    camera_port INT NULL COMMENT '相机端口号',
    protocol ENUM('USB', 'Ethernet', 'WiFi', 'Serial') NOT NULL DEFAULT 'USB' COMMENT '连接协议',
    
    -- 相机参数
    exposure_time INT NULL COMMENT '曝光时间(μs)',
    gain DECIMAL(5,2) NULL COMMENT '增益值',
    white_balance ENUM('Auto', 'Manual', 'Daylight', 'Fluorescent', 'Tungsten') NOT NULL DEFAULT 'Auto' COMMENT '白平衡模式',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_camera_type (camera_type),
    INDEX idx_camera_ip (camera_ip),
    INDEX idx_protocol (protocol),
    INDEX idx_frame_rate (frame_rate),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='深度相机配置表';

-- 创建导航控制器配置表
CREATE TABLE cfg_navigation_controller (
    id VARCHAR(36) PRIMARY KEY COMMENT '导航控制器配置ID',
    
    -- 控制器基本信息
    module_group INT NOT NULL DEFAULT 1 COMMENT '模块组编号(支持多组配置)',
    
    -- 网络配置
    ethernet_ip VARCHAR(15) NOT NULL COMMENT '以太网通讯IP地址',
    subnet_mask VARCHAR(15) NOT NULL DEFAULT '255.255.255.0' COMMENT '子网掩码',
    gateway VARCHAR(15) NOT NULL DEFAULT '192.168.1.1' COMMENT '网关地址',
    ethernet_port INT NOT NULL COMMENT '以太网通讯端口号(1-65535)',
    baud_rate INT NOT NULL DEFAULT 9600 COMMENT '波特率(9600-115200)',
    
    -- 导航参数
    deceleration_distance DECIMAL(8,2) NOT NULL DEFAULT 800.00 COMMENT '减速距离(mm)',
    stop_distance DECIMAL(8,2) NOT NULL DEFAULT 1500.00 COMMENT '停止距离(mm)',
    max_linear_velocity DECIMAL(8,3) NOT NULL DEFAULT 0.800 COMMENT '路径最大线速度(m/s)',
    max_angular_velocity DECIMAL(8,3) NOT NULL DEFAULT 0.100 COMMENT '路径最大角速度(rad/s)',
    acceleration DECIMAL(8,3) NOT NULL DEFAULT 0.800 COMMENT '加速度(m/s²)',
    deceleration DECIMAL(8,3) NOT NULL DEFAULT 0.800 COMMENT '减速度(m/s²)',
    expansion_coefficient DECIMAL(8,2) NOT NULL DEFAULT 0.00 COMMENT '膨胀系数(0-2.0)',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 索引
    INDEX idx_module_group (module_group),
    INDEX idx_ethernet_ip (ethernet_ip),
    INDEX idx_ethernet_port (ethernet_port),
    INDEX idx_baud_rate (baud_rate),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导航控制器配置表';

-- 创建智能传感器表
CREATE TABLE tb_sensor (
    id VARCHAR(36) PRIMARY KEY COMMENT '传感器ID',
    device_id VARCHAR(36) NOT NULL COMMENT '关联设备ID',
    sensor_name VARCHAR(100) NOT NULL COMMENT '传感器名称',
    sensor_params JSON NULL COMMENT '传感器参数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_device_id (device_id),
    INDEX idx_sensor_name (sensor_name),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (device_id) REFERENCES tb_device(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='智能传感器表';

-- 创建传感器日程表
CREATE TABLE tb_sensorschedule (
    id VARCHAR(36) PRIMARY KEY COMMENT '传感器日程ID',
    schedule_type VARCHAR(50) NOT NULL COMMENT '传感器日程类型',
    schedule_is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '传感器日程是否激活',
    sensor_id VARCHAR(36) NOT NULL COMMENT '关联传感器ID',
    schedule_param JSON NULL COMMENT '日程参数',
    set_time INT NOT NULL COMMENT '设置时间（Unix时间戳）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_schedule_type (schedule_type),
    INDEX idx_schedule_is_active (schedule_is_active),
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_set_time (set_time),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (sensor_id) REFERENCES tb_sensor(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='传感器日程表';

-- 创建传感器记录表
CREATE TABLE tb_sensorhistory (
    id VARCHAR(36) PRIMARY KEY COMMENT '传感器记录ID',
    sensor_id VARCHAR(36) NOT NULL COMMENT '关联传感器ID',
    record_data JSON NULL COMMENT '记录数据',
    file_url VARCHAR(500) NULL COMMENT '相关文件链接',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (sensor_id) REFERENCES tb_sensor(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='传感器记录表';

-- 创建巡检点表
CREATE TABLE tb_point (
    id VARCHAR(36) PRIMARY KEY COMMENT '巡检点ID',
    point_name VARCHAR(100) NOT NULL COMMENT '巡检点名称',
    map_id VARCHAR(36) NOT NULL COMMENT '所属地图ID',
    point_actions JSON NULL COMMENT '巡检点动作',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE CASCADE,
    INDEX idx_point_name (point_name),
    INDEX idx_map_id (map_id),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='巡检点表';

-- 创建任务表
CREATE TABLE tb_task (
    id VARCHAR(36) PRIMARY KEY COMMENT '任务ID',
    task_name VARCHAR(100) NOT NULL COMMENT '任务名称',
    map_id VARCHAR(36) NOT NULL COMMENT '所属地图ID',
    robot_id VARCHAR(36) NOT NULL COMMENT '执行机器人ID',
    task_items JSON NULL COMMENT '任务巡检项目ID列表',
    task_order INT NOT NULL DEFAULT 0 COMMENT '任务执行顺序',
    task_res_prior INT NOT NULL DEFAULT 1 COMMENT '响应优先级',
    task_int_prior INT NOT NULL DEFAULT 1 COMMENT '打断优先级',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE CASCADE,
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    INDEX idx_task_name (task_name),
    INDEX idx_map_id (map_id),
    INDEX idx_robot_id (robot_id),
    INDEX idx_task_order (task_order),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务表';

-- 创建任务日程表
CREATE TABLE tb_taskschedule (
    id VARCHAR(36) PRIMARY KEY COMMENT '任务日程ID',
    schedule_type VARCHAR(50) NOT NULL COMMENT '任务日程类型',
    schedule_is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '任务日程是否激活',
    task_id VARCHAR(36) NOT NULL COMMENT '关联任务ID',
    schedule_param JSON NULL COMMENT '日程参数',
    set_time INT NOT NULL COMMENT '设置时间（Unix时间戳）',
    cnt INT NOT NULL DEFAULT 1 COMMENT '需要执行的次数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (task_id) REFERENCES tb_task(id) ON DELETE CASCADE,
    INDEX idx_schedule_type (schedule_type),
    INDEX idx_task_id (task_id),
    INDEX idx_set_time (set_time),
    INDEX idx_schedule_is_active (schedule_is_active),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务日程表';

-- 创建任务记录表
CREATE TABLE tb_taskhistory (
    id VARCHAR(36) PRIMARY KEY COMMENT '任务记录ID',
    task_id VARCHAR(36) NOT NULL COMMENT '关联任务ID',
    record_start_time DATETIME NOT NULL COMMENT '任务开始时间',
    record_end_time DATETIME NULL COMMENT '任务结束时间',
    record_status VARCHAR(20) NOT NULL COMMENT '任务状态',
    record_batch INT NOT NULL COMMENT '任务批次号',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (task_id) REFERENCES tb_task(id) ON DELETE CASCADE,
    INDEX idx_task_id (task_id),
    INDEX idx_record_status (record_status),
    INDEX idx_record_batch (record_batch),
    INDEX idx_record_start_time (record_start_time),
    INDEX idx_record_end_time (record_end_time),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务记录表';

-- 创建巡检项目表
CREATE TABLE tb_item (
    id VARCHAR(36) PRIMARY KEY COMMENT '巡检项目ID',
    item_name VARCHAR(100) NOT NULL COMMENT '巡检项目名称',
    item_info JSON NOT NULL COMMENT '巡检参数信息',
    point_id VARCHAR(36) NOT NULL COMMENT '所属巡检点ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_item_name (item_name),
    INDEX idx_point_id (point_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_item_name_active (item_name, is_deleted),
    FOREIGN KEY (point_id) REFERENCES tb_point(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='巡检项目表';

-- 创建巡检记录表
CREATE TABLE tb_itemhistory (
    id VARCHAR(36) PRIMARY KEY COMMENT '巡检记录ID',
    taskhistory_id VARCHAR(36) NOT NULL COMMENT '任务记录ID',
    item_id VARCHAR(36) NOT NULL COMMENT '巡检项目ID',
    item_result JSON NULL COMMENT '巡检结果',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_taskhistory_id (taskhistory_id),
    INDEX idx_item_id (item_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_taskhistory_item_active (taskhistory_id, item_id, is_deleted),
    FOREIGN KEY (taskhistory_id) REFERENCES tb_taskhistory(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES tb_item(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='巡检记录表';

-- 创建任务结果表
CREATE TABLE tb_taskresult (
    id VARCHAR(36) PRIMARY KEY COMMENT '任务结果ID',
    taskhistory_id VARCHAR(36) NOT NULL UNIQUE COMMENT '任务记录ID',
    record_batch INT NOT NULL COMMENT '任务批次',
    result_point_id VARCHAR(36) NULL COMMENT '任务结束点ID',
    result_item_id VARCHAR(36) NULL COMMENT '任务结束巡检项目ID',
    result_file_url VARCHAR(500) NULL COMMENT '任务结果文件地址',
    result_collect_time DATETIME NULL COMMENT '结果采集时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_record_batch (record_batch),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (taskhistory_id) REFERENCES tb_taskhistory(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务结果表';

-- 创建报警规则表
CREATE TABLE tb_alarmrule (
    id VARCHAR(36) PRIMARY KEY COMMENT '报警规则ID',
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    business_type ENUM('inspection_item', 'gimbal_task', 'sensor') NOT NULL DEFAULT 'inspection_item' COMMENT '业务类型',
    business_id VARCHAR(36) NOT NULL COMMENT '业务对象ID',
    alarm_param JSON NULL COMMENT '报警参数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_rule_name (rule_name),
    INDEX idx_business_type (business_type),
    INDEX idx_business_id (business_id),
    INDEX idx_business_type_id (business_type, business_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_rule_name_active (rule_name, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报警规则表';

-- 创建报警信息表
CREATE TABLE tb_alarminfo (
    id VARCHAR(36) PRIMARY KEY COMMENT '报警信息ID',
    alarmrule_id VARCHAR(36) NOT NULL COMMENT '报警规则ID',
    record_type ENUM('itemhistory', 'gimbalhistory', 'sensorhistory') NOT NULL DEFAULT 'itemhistory' COMMENT '记录类型',
    record_id VARCHAR(36) NOT NULL COMMENT '记录ID',
    alarm_data JSON NULL COMMENT '触发数据',
    alarm_info TEXT NULL COMMENT '报警信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_alarmrule_id (alarmrule_id),
    INDEX idx_record_type (record_type),
    INDEX idx_record_id (record_id),
    INDEX idx_record_type_id (record_type, record_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (alarmrule_id) REFERENCES tb_alarmrule(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报警信息表';

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
    '主厂区',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440001',
    '分厂区A',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440002',
    '分厂区B',
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
    '550e8400-e29b-41d4-a716-446655440001',
    '一楼巡检地图',
    '/uploads/maps/floor1_map.png',
    1.0,
    100.0,
    100.0,
    '550e8400-e29b-41d4-a716-446655440000',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入示例地图路网数据
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
    '550e8400-e29b-41d4-a716-446655440001',
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
    '550e8400-e29b-41d4-a716-446655440001',
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
    '550e8400-e29b-41d4-a716-446655440001',
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
    map_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440002',
    '巡检机器人001',
    '{"model": "BOSHI-RB-01", "battery": 100, "status": "idle"}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440003',
    '巡检机器人002',
    '{"model": "BOSHI-RB-02", "battery": 85, "status": "working"}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440004',
    '巡检机器人003',
    '{"model": "BOSHI-RB-03", "battery": 95, "status": "idle"}',
    '550e8400-e29b-41d4-a716-446655440001',
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
    gimbal_params,
    map_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440030',
    '云台001',
    '{"type": "PTZ", "pan_range": 360, "tilt_range": 90, "zoom": "10x"}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440031',
    '云台002',
    '{"type": "Fixed", "angle": 45, "height": 3.5, "resolution": "4K"}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440032',
    '云台003',
    '{"type": "PTZ", "pan_range": 180, "tilt_range": 60, "zoom": "20x", "night_vision": true}',
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
    angle_params,
    task_type,
    gimbal_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440040',
    '全景拍摄任务',
    '{"pan": 0, "tilt": 0, "zoom": 1, "duration": 5}',
    'image',
    '550e8400-e29b-41d4-a716-446655440030',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440041',
    '监控录像任务',
    '{"pan": 45, "tilt": -30, "zoom": 2, "duration": 30}',
    'video',
    '550e8400-e29b-41d4-a716-446655440031',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440042',
    '定点观察任务',
    '{"pan": 90, "tilt": 0, "zoom": 5, "duration": 10}',
    'image',
    '550e8400-e29b-41d4-a716-446655440032',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例云台日程数据
INSERT INTO tb_gimbalschedule (
    id,
    schedule_type,
    schedule_is_active,
    gimbaltask_id,
    schedule_param,
    set_time,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440050',
    'daily',
    TRUE,
    '550e8400-e29b-41d4-a716-446655440040',
    '{"hour": 8, "minute": 0, "repeat": true}',
    UNIX_TIMESTAMP(NOW()),
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440051',
    'interval',
    TRUE,
    '550e8400-e29b-41d4-a716-446655440041',
    '{"interval_minutes": 30, "repeat": true}',
    UNIX_TIMESTAMP(NOW()),
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440052',
    'once',
    FALSE,
    '550e8400-e29b-41d4-a716-446655440042',
    '{"execute_time": "2024-12-31 10:00:00"}',
    UNIX_TIMESTAMP('2024-12-31 10:00:00'),
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例云台记录数据
INSERT INTO tb_gimbalhistory (
    id,
    gimbaltask_id,
    record_data,
    media_url,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440060',
    '550e8400-e29b-41d4-a716-446655440040',
    '{"angle": {"pan": 0, "tilt": 0, "zoom": 1}, "status": "completed", "quality": "high"}',
    '/media/gimbal/2024/01/panorama_001.jpg',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440061',
    '550e8400-e29b-41d4-a716-446655440041',
    '{"angle": {"pan": 45, "tilt": -30, "zoom": 2}, "status": "completed", "duration": 30}',
    '/media/gimbal/2024/01/monitor_001.mp4',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440062',
    '550e8400-e29b-41d4-a716-446655440042',
    '{"angle": {"pan": 90, "tilt": 0, "zoom": 5}, "status": "completed", "quality": "medium"}',
    '/media/gimbal/2024/01/observation_001.jpg',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440063',
    '550e8400-e29b-41d4-a716-446655440040',
    '{"angle": {"pan": 180, "tilt": 10, "zoom": 1}, "status": "completed", "quality": "high"}',
    '/media/gimbal/2024/01/panorama_002.jpg',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);

-- 插入示例设备数据
INSERT INTO tb_device (
    id,
    device_name,
    device_params,
    map_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440070',
    '温湿度传感器001',
    '{"type": "temperature_humidity", "model": "DHT22", "range": {"temp": "-40~80", "humidity": "0~100"}, "accuracy": {"temp": "±0.5", "humidity": "±2%"}}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440071',
    '气体检测仪001',
    '{"type": "gas_detector", "model": "MQ-135", "detect_gas": ["CO", "NH3", "NOx", "smoke"], "voltage": "5V"}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440072',
    '红外热像仪001',
    '{"type": "thermal_camera", "model": "FLIR-E8", "resolution": "320x240", "temp_range": "-20~250", "accuracy": "±2°C"}',
    '550e8400-e29b-41d4-a716-446655440001',
    NOW(),
    NOW(),
    'operator',
    'operator',
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
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例传感器日程数据
INSERT INTO tb_sensorschedule (
    id,
    schedule_type,
    schedule_is_active,
    sensor_id,
    schedule_param,
    set_time,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440090',
    'interval',
    TRUE,
    '550e8400-e29b-41d4-a716-446655440080',
    '{"interval_seconds": 60, "repeat": true}',
    UNIX_TIMESTAMP(NOW()),
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440091',
    'interval',
    TRUE,
    '550e8400-e29b-41d4-a716-446655440082',
    '{"interval_seconds": 30, "repeat": true, "threshold_check": true}',
    UNIX_TIMESTAMP(NOW()),
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440092',
    'daily',
    FALSE,
    '550e8400-e29b-41d4-a716-446655440083',
    '{"hour": 9, "minute": 0, "repeat": true}',
    UNIX_TIMESTAMP(NOW()),
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
INSERT INTO tb_task (
    id,
    task_name,
    map_id,
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
    '550e8400-e29b-41d4-a716-446655440003',
    '一楼日常巡检',
    '550e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440002',
    '["550e8400-e29b-41d4-a716-446655440009", "550e8400-e29b-41d4-a716-446655440010", "550e8400-e29b-41d4-a716-446655440011"]',
    1,
    5,
    3,
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 插入示例巡检点数据
INSERT INTO tb_point (
    id,
    point_name,
    map_id,
    point_actions,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440005',
    '一楼入口检查点',
    '550e8400-e29b-41d4-a716-446655440001',
    '{"action": "stop_and_check", "duration": 30}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440006',
    '一楼设备间检查点',
    '550e8400-e29b-41d4-a716-446655440001',
    '{"action": "detailed_inspection", "duration": 60}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440007',
    '一楼走廊检查点',
    '550e8400-e29b-41d4-a716-446655440001',
    '{"action": "patrol", "duration": 15}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440008',
    '一楼出口检查点',
    '550e8400-e29b-41d4-a716-446655440001',
    '{"action": "final_check", "duration": 20}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);

-- 插入示例巡检项目数据
INSERT INTO tb_item (
    id,
    item_name,
    item_info,
    point_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    -- 一楼入口检查点 (550e8400-e29b-41d4-a716-446655440005) 的巡检项目
    '550e8400-e29b-41d4-a716-446655440009',
    '拍照记录',
    '{"type": "camera", "resolution": "1920x1080"}',
    '550e8400-e29b-41d4-a716-446655440005',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440010',
    '安全检查',
    '{"items": ["消防栓", "安全标识", "应急灯"]}',
    '550e8400-e29b-41d4-a716-446655440005',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    -- 设备间检查点 (550e8400-e29b-41d4-a716-446655440006) 的巡检项目
    '550e8400-e29b-41d4-a716-446655440011',
    '设备状态检查',
    '{"devices": ["空调", "配电柜", "UPS"]}',
    '550e8400-e29b-41d4-a716-446655440006',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440012',
    '环境监测',
    '{"sensors": ["温度", "湿度", "烟雾"]}',
    '550e8400-e29b-41d4-a716-446655440006',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    -- 走廊检查点 (550e8400-e29b-41d4-a716-446655440007) 的巡检项目
    '550e8400-e29b-41d4-a716-446655440013',
    '清洁检查',
    '{"areas": ["地面", "墙面", "天花板"]}',
    '550e8400-e29b-41d4-a716-446655440007',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440014',
    '照明检查',
    '{"lights": ["走廊灯", "应急灯", "指示灯"]}',
    '550e8400-e29b-41d4-a716-446655440007',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
), (
    -- 出口检查点 (550e8400-e29b-41d4-a716-446655440008) 的巡检项目
    '550e8400-e29b-41d4-a716-446655440025',
    '消防设施检查',
    '{"facilities": ["灭火器", "消防栓", "烟感器"]}',
    '550e8400-e29b-41d4-a716-446655440008',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
);


-- 插入示例任务日程数据
INSERT INTO tb_taskschedule (
    id,
    schedule_type,
    schedule_is_active,
    task_id,
    schedule_param,
    set_time,
    cnt,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440601',
    'daily',
    TRUE,
    '550e8400-e29b-41d4-a716-446655440003',
    '{"time": "08:00:00", "repeat": true}',
    1705392000,
    15,
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440602',
    'weekly',
    TRUE,
    '550e8400-e29b-41d4-a716-446655440003',
    '{"day": "monday", "time": "14:00:00"}',
    1705478400,
    4,
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
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
    '550e8400-e29b-41d4-a716-446655440003',
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
    '550e8400-e29b-41d4-a716-446655440003',
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
    '550e8400-e29b-41d4-a716-446655440003',
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
    '550e8400-e29b-41d4-a716-446655440006',
    '550e8400-e29b-41d4-a716-446655440011',
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
    '550e8400-e29b-41d4-a716-446655440006',
    '550e8400-e29b-41d4-a716-446655440011',
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
    '550e8400-e29b-41d4-a716-446655440009',
    '{"status": "success", "photos": ["/data/photo1.jpg", "/data/photo2.jpg"]}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441002',
    '550e8400-e29b-41d4-a716-446655440801',
    '550e8400-e29b-41d4-a716-446655440010',
    '{"status": "success", "check_result": "正常"}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441003',
    '550e8400-e29b-41d4-a716-446655440801',
    '550e8400-e29b-41d4-a716-446655440011',
    '{"status": "success", "equipment_status": "正常"}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441004',
    '550e8400-e29b-41d4-a716-446655440802',
    '550e8400-e29b-41d4-a716-446655440013',
    '{"status": "success", "cleanliness": "良好"}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441005',
    '550e8400-e29b-41d4-a716-446655440802',
    '550e8400-e29b-41d4-a716-446655440014',
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
    '550e8400-e29b-41d4-a716-446655440011',
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
    '550e8400-e29b-41d4-a716-446655440001',
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
    '550e8400-e29b-41d4-a716-446655440001',
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
    '550e8400-e29b-41d4-a716-446655440001',
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
    '550e8400-e29b-41d4-a716-446655440001',
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
    '550e8400-e29b-41d4-a716-446655440001',
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
    '550e8400-e29b-41d4-a716-446655440001',
    '{"actual_value": 105, "range": {"min": 0, "max": 100}, "exceeded": true}',
    '传感器数据超出正常范围，当前值105',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
);

-- 显示创建结果
SELECT 'Database initialization completed successfully!' as status;
SELECT '========== 用户账号信息 ==========' as divider;
SELECT 'superadmin / superadmin (超级管理员)' as user1;
SELECT 'admin / admin (管理员)' as user2;
SELECT 'operator / operator (操作员)' as user3;
SELECT '========== 示例数据统计 ==========' as divider2;
SELECT '3个用户, 3个厂区, 1个地图, 1个机器人, 3个设备, 4个智能传感器, 3个传感器日程, 4个传感器记录, 3个云台, 3个云台任务, 3个云台日程, 4个云台记录, 2个车体控制器配置, 3个环境传感器配置, 3个双光云台配置, 3个电机状态配置, 3个激光雷达配置, 3个机械臂状态配置, 3个超声波状态配置, 3个深度相机配置, 3个导航控制器配置, 1个任务' as summary1;
SELECT '3条地图路网, 4个巡检点, 7个巡检项目' as summary2;
SELECT '2条任务日程, 3条任务记录, 3条任务结果, 5条巡检记录' as summary3;
SELECT '2条报警规则, 1条报警信息' as summary4;
SELECT 'Token expiry: 30 days (2592000 seconds)' as token_info;
SELECT 'Roles: super_admin > admin > operator > viewer > user' as role_info;
