-- 博实智能巡检平台 - 数据库初始化SQL
-- 创建数据库
CREATE DATABASE IF NOT EXISTS boshirobot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE boshirobot;

-- 删除所有现有表（如果存在）- 按外键依赖顺序删除
-- 注意：使用 SET FOREIGN_KEY_CHECKS = 0 来禁用外键检查，以便可以按任意顺序删除表
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS tb_alarm_info;
DROP TABLE IF EXISTS tb_alarm_rule_relation;
DROP TABLE IF EXISTS tb_alarm_rule;
DROP TABLE IF EXISTS tb_alarminfo;
DROP TABLE IF EXISTS tb_alarmrule;
DROP TABLE IF EXISTS tb_taskresult;
DROP TABLE IF EXISTS tb_itemhistory;
DROP TABLE IF EXISTS tb_point_item;  -- 旧的中间表，需要先删除
DROP TABLE IF EXISTS tb_item;
DROP TABLE IF EXISTS tb_detection_type;
DROP TABLE IF EXISTS tb_taskhistory;
DROP TABLE IF EXISTS tb_taskschedule;
DROP TABLE IF EXISTS tb_task;
DROP TABLE IF EXISTS tb_point;
DROP TABLE IF EXISTS tb_mapnet;
DROP TABLE IF EXISTS tb_robot_map;
DROP TABLE IF EXISTS tb_robot;
DROP TABLE IF EXISTS tb_gimbalhistory;
DROP TABLE IF EXISTS tb_group;
DROP TABLE IF EXISTS tb_gimbalschedule;
DROP TABLE IF EXISTS tb_gimbal_inspection_project_preset_point;
DROP TABLE IF EXISTS tb_gimbal_preset_point;
DROP TABLE IF EXISTS tb_gimbal_inspection_project;
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
DROP TABLE IF EXISTS tb_operation_record;
DROP TABLE IF EXISTS tb_manual_operation;
DROP TABLE IF EXISTS tb_map;
DROP TABLE IF EXISTS tb_factory;
DROP TABLE IF EXISTS tb_sessions;
DROP TABLE IF EXISTS tb_users;
-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

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

-- 创建分组表
CREATE TABLE tb_group (
    id VARCHAR(36) PRIMARY KEY COMMENT '分组ID',
    group_name VARCHAR(100) NOT NULL COMMENT '分组名称',
    group_description VARCHAR(500) NULL COMMENT '分组描述',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_group_name (group_name),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分组表';

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
    factory_id VARCHAR(36) NULL COMMENT '厂区ID',
    group_id VARCHAR(36) NULL COMMENT '分组ID',
    preview_url VARCHAR(500) NULL COMMENT '预览地址',
    control_url VARCHAR(500) NULL COMMENT '控制地址',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_robot_name (robot_name),
    INDEX idx_factory_id (factory_id),
    INDEX idx_group_id (group_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_robot_name_active (robot_name, is_deleted),
    FOREIGN KEY (factory_id) REFERENCES tb_factory(id) ON DELETE SET NULL,
    FOREIGN KEY (group_id) REFERENCES tb_group(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='机器人表';

-- 创建机器人-地图关联表（多对多中间表）
CREATE TABLE tb_robot_map (
    id VARCHAR(36) PRIMARY KEY COMMENT '关联ID',
    robot_id VARCHAR(36) NOT NULL COMMENT '机器人ID',
    map_id VARCHAR(36) NOT NULL COMMENT '地图ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_robot_id (robot_id),
    INDEX idx_map_id (map_id),
    INDEX idx_created_at (created_at),
    UNIQUE KEY uk_robot_map (robot_id, map_id),
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='机器人-地图关联表';

-- 创建云台表
CREATE TABLE tb_gimbal (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台ID',
    gimbal_name VARCHAR(100) NOT NULL COMMENT '云台名称',
    map_id VARCHAR(36) NULL COMMENT '地图ID',
    group_id VARCHAR(36) NULL COMMENT '分组ID',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '启用状态：0-禁用，1-启用',
    ip_address VARCHAR(45) NOT NULL COMMENT '云台IP地址',
    port INT NOT NULL COMMENT '云台端口',
    username VARCHAR(100) NOT NULL COMMENT '登录用户名',
    password VARCHAR(255) NOT NULL COMMENT '登录密码',
    rtsp_main_url VARCHAR(255) NOT NULL COMMENT 'RTSP主码流地址',
    rtsp_sub_url VARCHAR(255) NULL COMMENT 'RTSP子码流地址',
    channel INT NOT NULL DEFAULT 1 COMMENT '通道号：1或2',
    x_coordinate DECIMAL(10,4) NULL COMMENT 'X坐标（地图横坐标）',
    y_coordinate DECIMAL(10,4) NULL COMMENT 'Y坐标（地图纵坐标）',
    p_coordinate DECIMAL(10,4) NULL COMMENT 'P坐标',
    t_coordinate DECIMAL(10,4) NULL COMMENT 'T坐标',
    z_coordinate DECIMAL(10,4) NULL COMMENT 'Z坐标',
    f_coordinate DECIMAL(10,4) NULL COMMENT 'F坐标',
    preview_url VARCHAR(500) NULL COMMENT '预览地址',
    control_url VARCHAR(500) NULL COMMENT '控制地址',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_gimbal_name (gimbal_name),
    INDEX idx_map_id (map_id),
    INDEX idx_group_id (group_id),
    INDEX idx_enabled (enabled),
    INDEX idx_gimbal_coordinates (map_id, x_coordinate, y_coordinate),
    INDEX idx_gimbal_channel (channel),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_gimbal_name_active (gimbal_name, is_deleted),
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE SET NULL,
    FOREIGN KEY (group_id) REFERENCES tb_group(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台表';

-- 创建云台任务表
CREATE TABLE tb_gimbaltask (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台任务ID',
    task_name VARCHAR(100) NOT NULL COMMENT '云台任务名称',
    gimbal_id VARCHAR(36) NOT NULL COMMENT '所属云台ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_task_name (task_name),
    INDEX idx_gimbal_id (gimbal_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_task_name_active (task_name, is_deleted),
    FOREIGN KEY (gimbal_id) REFERENCES tb_gimbal(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台任务表';

-- 创建云台预设点表（必须在tb_gimbal_inspection_project之前创建，因为中间表会引用）
CREATE TABLE tb_gimbal_preset_point (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台预设点ID',
    preset_name VARCHAR(100) NOT NULL COMMENT '预设点名称',
    gimbal_id VARCHAR(36) NOT NULL COMMENT '关联云台ID',
    p_coordinate DECIMAL(10,4) NULL COMMENT 'P坐标（水平旋转）',
    t_coordinate DECIMAL(10,4) NULL COMMENT 'T坐标（垂直旋转）',
    z_coordinate DECIMAL(10,4) NULL COMMENT 'Z坐标（变焦）',
    f_coordinate DECIMAL(10,4) NULL COMMENT 'F坐标（聚焦）',
    aperture INT NULL COMMENT '光圈（0-100）',
    shutter INT NULL COMMENT '快门分母',
    backlight_compensation BOOLEAN NOT NULL DEFAULT FALSE COMMENT '背光补偿',
    wide_dynamic BOOLEAN NOT NULL DEFAULT FALSE COMMENT '宽动态',
    strong_light_suppression BOOLEAN NOT NULL DEFAULT FALSE COMMENT '强光抑制',
    fill_light BOOLEAN NOT NULL DEFAULT FALSE COMMENT '补光',
    image_url VARCHAR(500) NULL COMMENT '图片链接',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_preset_name (preset_name),
    INDEX idx_gimbal_id (gimbal_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_preset_name_per_gimbal (gimbal_id, preset_name, is_deleted),
    FOREIGN KEY (gimbal_id) REFERENCES tb_gimbal(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台预设点表';

-- 创建云台巡检项目表
CREATE TABLE tb_gimbal_inspection_project (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台巡检项目ID',
    task_name VARCHAR(100) NOT NULL COMMENT '巡检项目名称',
    gimbaltask_id VARCHAR(36) NOT NULL COMMENT '关联云台任务ID',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序值，数字越小越靠前',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_project_name (task_name),
    INDEX idx_gimbaltask_id (gimbaltask_id),
    INDEX idx_gimbaltask_sort_order (gimbaltask_id, sort_order),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_project_name_per_task (gimbaltask_id, task_name, is_deleted),
    FOREIGN KEY (gimbaltask_id) REFERENCES tb_gimbaltask(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台巡检项目表';

-- 创建云台巡检项目-预设点关联表（多对多中间表）
CREATE TABLE tb_gimbal_inspection_project_preset_point (
    id VARCHAR(36) PRIMARY KEY COMMENT '关联ID',
    inspection_project_id VARCHAR(36) NOT NULL COMMENT '云台巡检项目ID',
    preset_point_id VARCHAR(36) NOT NULL COMMENT '云台预设点ID',
    detection_type VARCHAR(20) NOT NULL COMMENT '检测类型：可见光视频/可见光图片/热成像图片/热成像视频',
    video_duration INT NULL COMMENT '拍摄时长（秒），当detection_type为可见光视频或热成像视频时使用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_inspection_project_id (inspection_project_id),
    INDEX idx_preset_point_id (preset_point_id),
    INDEX idx_detection_type (detection_type),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_project_preset_detection_active (inspection_project_id, preset_point_id, detection_type, is_deleted),
    FOREIGN KEY (inspection_project_id) REFERENCES tb_gimbal_inspection_project(id) ON DELETE CASCADE,
    FOREIGN KEY (preset_point_id) REFERENCES tb_gimbal_preset_point(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台巡检项目-预设点关联表';

-- 创建云台日程表
CREATE TABLE tb_gimbalschedule (
    id VARCHAR(50) PRIMARY KEY COMMENT '日程ID',
    gimbaltask_id VARCHAR(50) NOT NULL COMMENT '关联的云台任务ID',
    schedule_name VARCHAR(200) NOT NULL COMMENT '日程名称',
    start_date DATE NOT NULL COMMENT '开始日期',
    end_date DATE NOT NULL COMMENT '结束日期',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '启用状态：0-禁用，1-启用',
    
    -- 执行周期配置
    cycle_type VARCHAR(20) NOT NULL COMMENT '周期类型：daily/monthly_days/weekly',
    cycle_config JSON NULL COMMENT '周期详细配置（JSON格式）',
    -- cycle_config 结构示例：
    -- {"selectedDays": [1,5,10]} 或 {"selectedWeeks": [1,3,5]}
    
    -- 执行时间配置
    time_mode VARCHAR(20) NOT NULL COMMENT '时间模式：custom/interval',
    time_config JSON NOT NULL COMMENT '时间详细配置（JSON格式）',
    -- time_config 结构示例：
    -- 自定义模式: {"customTimes": ["08:00","12:00","18:00"]}
    -- 间隔模式: {"intervalTimeRange": ["08:00","18:00"], "intervalMinutes": 60}
    
    -- 用于显示的简化字段（便于查询和展示）
    time_display_start TIME NULL COMMENT '开始时间（用于时间轴显示）',
    time_display_end TIME NULL COMMENT '结束时间（用于时间轴显示）',
    
    -- 审计字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    INDEX idx_gimbaltask_id (gimbaltask_id),
    INDEX idx_cycle_type (cycle_type),
    INDEX idx_enabled (enabled),
    INDEX idx_date_range (start_date, end_date),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (gimbaltask_id) REFERENCES tb_gimbaltask(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台任务日程表（格式与任务日程表统一）';

-- 创建云台巡检记录表
CREATE TABLE tb_gimbalhistory (
    id VARCHAR(36) PRIMARY KEY COMMENT '云台巡检记录ID',
    project_preset_point_id VARCHAR(36) NOT NULL COMMENT '关联云台巡检项目-预设点关联ID',
    record_data JSON NULL COMMENT '记录数据',
    media_url VARCHAR(500) NULL COMMENT '图像/视频链接',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_project_preset_point_id (project_preset_point_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (project_preset_point_id) REFERENCES tb_gimbal_inspection_project_preset_point(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='云台巡检记录表';

-- 创建车体控制器配置表
CREATE TABLE cfg_vehicle_controller (
    id VARCHAR(36) PRIMARY KEY COMMENT '车体控制器ID',
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
    -- 车体基础参数
    vehicle_model VARCHAR(50) NOT NULL COMMENT '车体模型：双轮差速/四轮差速/四驱四转/单舵轮/双舵轮',
    wheel_diameter DECIMAL(8,2) NOT NULL COMMENT '车轮直径(mm)',
    reduction_ratio INT NOT NULL COMMENT '车体减速比',
    wheelbase DECIMAL(8,2) NOT NULL COMMENT '车体轴距(mm)',
    track_width DECIMAL(8,2) NOT NULL COMMENT '车体轮距(mm)',
    max_linear_velocity DECIMAL(8,3) NOT NULL COMMENT '车体最大线速度(m/s)',
    max_angular_velocity DECIMAL(8,3) NOT NULL COMMENT '车体最大角速度(rad/s)',
    
    -- 串口通讯配置（4组，每组3个参数：站号、波特率、功能码）
    serial_1_station_number INT NULL COMMENT '串口1站号(1-255)',
    serial_1_baud_rate INT NULL COMMENT '串口1波特率(9600-115200)',
    serial_1_function_code INT NULL COMMENT '串口1功能码',
    serial_2_station_number INT NULL COMMENT '串口2站号(1-255)',
    serial_2_baud_rate INT NULL COMMENT '串口2波特率(9600-115200)',
    serial_2_function_code INT NULL COMMENT '串口2功能码',
    serial_3_station_number INT NULL COMMENT '串口3站号(1-255)',
    serial_3_baud_rate INT NULL COMMENT '串口3波特率(9600-115200)',
    serial_3_function_code INT NULL COMMENT '串口3功能码',
    serial_4_station_number INT NULL COMMENT '串口4站号(1-255)',
    serial_4_baud_rate INT NULL COMMENT '串口4波特率(9600-115200)',
    serial_4_function_code INT NULL COMMENT '串口4功能码',
    
    -- 以太网通讯配置（2组，用编号区分）
    ethernet_1_ip_address VARCHAR(15) NULL COMMENT '以太网1IP地址',
    ethernet_1_subnet_mask VARCHAR(15) NULL COMMENT '以太网1子网掩码',
    ethernet_1_gateway VARCHAR(15) NULL COMMENT '以太网1网关',
    ethernet_1_port INT NULL COMMENT '以太网1端口(1-65535)',
    ethernet_1_baud_rate INT NULL COMMENT '以太网1波特率(9600-115200)',
    ethernet_1_communication_mode VARCHAR(20) NULL COMMENT '以太网1通讯模式：server/client',
    ethernet_2_ip_address VARCHAR(15) NULL COMMENT '以太网2IP地址',
    ethernet_2_subnet_mask VARCHAR(15) NULL COMMENT '以太网2子网掩码',
    ethernet_2_gateway VARCHAR(15) NULL COMMENT '以太网2网关',
    ethernet_2_port INT NULL COMMENT '以太网2端口(1-65535)',
    ethernet_2_baud_rate INT NULL COMMENT '以太网2波特率(9600-115200)',
    ethernet_2_communication_mode VARCHAR(20) NULL COMMENT '以太网2通讯模式：server/client',
    
    -- 控制器管理
    controller_version VARCHAR(20) NOT NULL COMMENT '控制器版本',
    remote_upgrade_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '远程升级是否开启',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
    INDEX idx_vehicle_model (vehicle_model),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车体控制器配置表';

-- 创建环境传感器配置表
CREATE TABLE cfg_environment_sensor (
    id VARCHAR(36) PRIMARY KEY COMMENT '环境传感器ID',
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
    -- 环境传感器参数
    station_number INT NOT NULL COMMENT '站号(1-255)',
    baud_rate INT NOT NULL COMMENT '波特率(9600-115200)',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
    INDEX idx_station_number (station_number),
    INDEX idx_baud_rate (baud_rate),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='环境传感器配置表';

-- 创建双光云台配置表
CREATE TABLE cfg_dual_ptz (
    id VARCHAR(36) PRIMARY KEY COMMENT '双光云台配置ID',
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
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
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
    INDEX idx_ptz_ip (ptz_ip),
    INDEX idx_operating_speed (operating_speed),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='双光云台配置表';

-- 创建电机状态配置表
CREATE TABLE cfg_motor_status (
    id VARCHAR(36) PRIMARY KEY COMMENT '电机状态配置ID',
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
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
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
    INDEX idx_motor_id (motor_id),
    INDEX idx_baud_rate (baud_rate),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电机状态配置表';

-- 创建激光雷达配置表
CREATE TABLE cfg_lidar (
    id VARCHAR(36) PRIMARY KEY COMMENT '激光雷达配置ID',
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
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
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
    INDEX idx_lidar_ip (lidar_ip),
    INDEX idx_lidar_port (lidar_port),
    INDEX idx_scan_frequency (scan_frequency_rpm),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='激光雷达配置表';

-- 创建机械臂状态配置表
CREATE TABLE cfg_robot_arm (
    id VARCHAR(36) PRIMARY KEY COMMENT '机械臂状态配置ID',
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
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
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
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
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
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
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
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
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
    -- 深度相机配置参数
    serial_port_id INT NOT NULL DEFAULT 0 COMMENT '串口ID(0-255)',
    camera_mode VARCHAR(50) NULL COMMENT '相机模式',
    image_flip ENUM('上下翻转', '左右翻转', '中心翻转') NULL COMMENT '图像翻转',
    image_alignment VARCHAR(50) NULL COMMENT '图像对齐',
    
    -- 基础字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
    INDEX idx_serial_port_id (serial_port_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='深度相机配置表';

-- 创建导航控制器配置表
CREATE TABLE cfg_navigation_controller (
    id VARCHAR(36) PRIMARY KEY COMMENT '导航控制器配置ID',
    
    -- 关联机器人
    robot_id VARCHAR(36) NOT NULL COMMENT '关联机器人ID',
    
    -- 以太网通讯配置（2组，用编号区分）
    ethernet_1_ip VARCHAR(15) NULL COMMENT '以太网1IP地址',
    ethernet_1_subnet_mask VARCHAR(15) NULL COMMENT '以太网1子网掩码',
    ethernet_1_gateway VARCHAR(15) NULL COMMENT '以太网1网关',
    ethernet_1_port INT NULL COMMENT '以太网1端口号(1-65535)',
    ethernet_1_baud_rate INT NULL COMMENT '以太网1波特率(9600-115200)',
    ethernet_2_ip VARCHAR(15) NULL COMMENT '以太网2IP地址',
    ethernet_2_subnet_mask VARCHAR(15) NULL COMMENT '以太网2子网掩码',
    ethernet_2_gateway VARCHAR(15) NULL COMMENT '以太网2网关',
    ethernet_2_port INT NULL COMMENT '以太网2端口号(1-65535)',
    ethernet_2_baud_rate INT NULL COMMENT '以太网2波特率(9600-115200)',
    
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
    
    -- 外键
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_robot_id (robot_id),
    INDEX idx_ethernet_1_ip (ethernet_1_ip),
    INDEX idx_ethernet_1_port (ethernet_1_port),
    INDEX idx_ethernet_2_ip (ethernet_2_ip),
    INDEX idx_ethernet_2_port (ethernet_2_port),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导航控制器配置表';

-- 创建巡检点表
CREATE TABLE tb_point (
    id VARCHAR(36) PRIMARY KEY COMMENT '巡检点ID',
    point_name VARCHAR(100) NOT NULL COMMENT '巡检点名称',
    map_id VARCHAR(36) NOT NULL COMMENT '所属地图ID',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '启用状态：0-禁用，1-启用',
    x_coordinate DECIMAL(10,4) NULL COMMENT 'X坐标（地图横坐标）',
    y_coordinate DECIMAL(10,4) NULL COMMENT 'Y坐标（地图纵坐标）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (map_id) REFERENCES tb_map(id) ON DELETE CASCADE,
    INDEX idx_point_name (point_name),
    INDEX idx_map_id (map_id),
    INDEX idx_enabled (enabled),
    INDEX idx_point_coordinates (map_id, x_coordinate, y_coordinate),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='巡检点表';

-- 创建设备表（必须在tb_point之后创建，因为tb_device引用tb_point，且必须在tb_sensor之前，因为tb_sensor引用tb_device）
CREATE TABLE tb_device (
    id VARCHAR(36) PRIMARY KEY COMMENT '设备ID',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_params JSON NULL COMMENT '设备参数',
    point_id VARCHAR(36) NOT NULL COMMENT '所属巡检点ID',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '启用状态：0-禁用，1-启用',
    x_coordinate DECIMAL(10,4) NULL COMMENT 'X坐标（地图横坐标）',
    y_coordinate DECIMAL(10,4) NULL COMMENT 'Y坐标（地图纵坐标）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_device_name (device_name),
    INDEX idx_point_id (point_id),
    INDEX idx_enabled (enabled),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_device_name_active (device_name, is_deleted),
    FOREIGN KEY (point_id) REFERENCES tb_point(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备表';

-- 创建智能传感器表（必须在tb_device之后创建，因为tb_sensor引用tb_device）
CREATE TABLE tb_sensor (
    id VARCHAR(36) PRIMARY KEY COMMENT '传感器ID',
    device_id VARCHAR(36) NOT NULL COMMENT '关联设备ID',
    sensor_name VARCHAR(100) NOT NULL COMMENT '传感器名称',
    sensor_params JSON NULL COMMENT '传感器参数',
    group_id VARCHAR(36) NULL COMMENT '分组ID',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '启用状态：0-禁用，1-启用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_device_id (device_id),
    INDEX idx_sensor_name (sensor_name),
    INDEX idx_group_id (group_id),
    INDEX idx_enabled (enabled),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (device_id) REFERENCES tb_device(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='智能传感器表';

-- 创建传感器记录表（必须在tb_sensor之后创建，因为tb_sensorhistory引用tb_sensor）
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

-- 创建任务表
CREATE TABLE tb_task (
    id VARCHAR(36) PRIMARY KEY COMMENT '任务ID',
    task_name VARCHAR(100) NOT NULL COMMENT '任务名称',
    robot_id VARCHAR(36) NOT NULL COMMENT '执行机器人ID',
    task_items JSON NULL COMMENT '任务巡检项目ID列表',
    task_order INT NOT NULL DEFAULT 0 COMMENT '任务执行顺序',
    task_res_prior INT NOT NULL DEFAULT 1 COMMENT '响应优先级',
    task_int_prior INT NOT NULL DEFAULT 1 COMMENT '打断优先级',
    total_duration INT NULL COMMENT '任务总用时（分钟）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (robot_id) REFERENCES tb_robot(id) ON DELETE CASCADE,
    INDEX idx_task_name (task_name),
    INDEX idx_robot_id (robot_id),
    INDEX idx_task_order (task_order),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务表';

-- 创建任务日程表
CREATE TABLE tb_taskschedule (
    id VARCHAR(50) PRIMARY KEY COMMENT '日程ID',
    task_id VARCHAR(50) NOT NULL COMMENT '关联的任务ID',
    schedule_name VARCHAR(200) NOT NULL COMMENT '日程名称',
    start_date DATE NOT NULL COMMENT '开始日期',
    end_date DATE NOT NULL COMMENT '结束日期',
    enabled TINYINT(1) DEFAULT 1 COMMENT '启用状态：0-禁用，1-启用',
    item_count INT DEFAULT 0 COMMENT '关联的巡检项目数量',
    
    -- 执行周期配置
    cycle_type VARCHAR(20) NOT NULL COMMENT '周期类型：daily/monthly_days/weekly',
    cycle_config JSON COMMENT '周期详细配置（JSON格式）',
    -- cycle_config 结构示例：
    -- {"selectedDays": [1,5,10]} 或 {"selectedWeeks": [1,3,5]}
    
    -- 执行时间配置
    time_mode VARCHAR(20) NOT NULL COMMENT '时间模式：custom/interval',
    time_config JSON NOT NULL COMMENT '时间详细配置（JSON格式）',
    -- time_config 结构示例：
    -- 自定义模式: {"customTimes": ["08:00","12:00","18:00"]}
    -- 间隔模式: {"intervalTimeRange": ["08:00","18:00"], "intervalMinutes": 60}
    
    -- 用于显示的简化字段（便于查询和展示）
    frequency_display VARCHAR(200) COMMENT '周期显示文本（如"每天"、"每月1、5、10日"）',
    time_display_start TIME COMMENT '开始时间（用于时间轴显示）',
    time_display_end TIME COMMENT '结束时间（用于时间轴显示）',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(50) COMMENT '创建人',
    updated_by VARCHAR(50) COMMENT '更新人',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    
    FOREIGN KEY (task_id) REFERENCES tb_task(id) ON DELETE CASCADE,
    INDEX idx_task_id (task_id),
    INDEX idx_cycle_type (cycle_type),
    INDEX idx_enabled (enabled),
    INDEX idx_date_range (start_date, end_date),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务巡检日程表';

-- 创建巡检项目表（必须在tb_taskhistory之前创建，因为tb_taskhistory引用tb_item）
-- 创建检测类型表
CREATE TABLE tb_detection_type (
    id VARCHAR(36) PRIMARY KEY COMMENT '检测类型ID',
    type_name VARCHAR(50) NOT NULL UNIQUE COMMENT '检测类型名称',
    type_code VARCHAR(20) NOT NULL UNIQUE COMMENT '检测类型代码',
    description VARCHAR(200) NULL COMMENT '检测类型描述',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '启用状态：0-禁用，1-启用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_type_name (type_name),
    INDEX idx_type_code (type_code),
    INDEX idx_sort_order (sort_order),
    INDEX idx_enabled (enabled),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检测类型表';

-- 创建巡检项目表
CREATE TABLE tb_item (
    id VARCHAR(36) PRIMARY KEY COMMENT '巡检项目ID',
    item_name VARCHAR(100) NOT NULL COMMENT '巡检项目名称',
    item_info JSON NOT NULL COMMENT '巡检参数信息',
    device_id VARCHAR(36) NOT NULL COMMENT '所属设备ID',
    detection_type_id VARCHAR(36) NULL COMMENT '检测类型ID',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '启用状态：0-禁用，1-启用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_item_name (item_name),
    INDEX idx_device_id (device_id),
    INDEX idx_detection_type_id (detection_type_id),
    INDEX idx_enabled (enabled),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_item_name_active (item_name, is_deleted),
    FOREIGN KEY (device_id) REFERENCES tb_device(id) ON DELETE CASCADE,
    FOREIGN KEY (detection_type_id) REFERENCES tb_detection_type(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='巡检项目表';

-- 创建任务记录表（必须在tb_item之后创建，因为tb_taskhistory引用tb_item）
CREATE TABLE tb_taskhistory (
    id VARCHAR(36) PRIMARY KEY COMMENT '任务记录ID',
    task_id VARCHAR(36) NOT NULL COMMENT '关联任务ID',
    record_start_time DATETIME NOT NULL COMMENT '任务开始时间',
    record_end_time DATETIME NULL COMMENT '任务结束时间',
    record_status VARCHAR(20) NOT NULL COMMENT '任务状态：running-执行中, paused-已暂停, completed-已完成, failed-执行失败, cancelled-已取消',
    record_batch INT NOT NULL COMMENT '任务批次号',
    current_point_id VARCHAR(36) NULL COMMENT '当前执行的巡检点ID',
    current_item_id VARCHAR(36) NULL COMMENT '当前执行的巡检项目ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (task_id) REFERENCES tb_task(id) ON DELETE CASCADE,
    FOREIGN KEY (current_point_id) REFERENCES tb_point(id) ON DELETE SET NULL,
    FOREIGN KEY (current_item_id) REFERENCES tb_item(id) ON DELETE SET NULL,
    INDEX idx_task_id (task_id),
    INDEX idx_record_status (record_status),
    INDEX idx_record_batch (record_batch),
    INDEX idx_record_start_time (record_start_time),
    INDEX idx_record_end_time (record_end_time),
    INDEX idx_current_point_id (current_point_id),
    INDEX idx_current_item_id (current_item_id),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务记录表';

-- 创建巡检记录表
CREATE TABLE tb_itemhistory (
    id VARCHAR(36) PRIMARY KEY COMMENT '巡检记录ID',
    taskhistory_id VARCHAR(36) NOT NULL COMMENT '任务记录ID',
    item_id VARCHAR(36) NOT NULL COMMENT '巡检项目ID',
    item_result JSON NULL COMMENT '巡检结果',
    process_status VARCHAR(20) NULL COMMENT '处理状态：pending-待处理, processing-处理中, processed-已处理, failed-处理失败',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_taskhistory_id (taskhistory_id),
    INDEX idx_item_id (item_id),
    INDEX idx_process_status (process_status),
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
    result_status VARCHAR(20) NULL COMMENT '结果状态：success-成功, failed-失败, partial-部分成功, warning-警告',
    process_status VARCHAR(20) NULL COMMENT '处理状态：pending-待处理, processing-处理中, processed-已处理, failed-处理失败',
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
    INDEX idx_result_status (result_status),
    INDEX idx_process_status (process_status),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (taskhistory_id) REFERENCES tb_taskhistory(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务结果表';

-- 创建报警规则表
CREATE TABLE tb_alarm_rule (
    id VARCHAR(36) PRIMARY KEY COMMENT '报警规则ID',
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    alarm_category ENUM('robot', 'inspection', 'gimbal', 'sensor', 'other') NOT NULL COMMENT '报警分类',
    alarm_level INT NOT NULL COMMENT '报警等级 1-10',
    rule_type ENUM('value_range', 'bool_value', 'sum_value', 'diff_value', 'avg_range', 'complex') NOT NULL COMMENT '规则类型',
    rule_config JSON NULL COMMENT '规则配置（JSON格式）',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    description TEXT NULL COMMENT '规则描述',
    is_global BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否全局规则（true表示不关联具体对象）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_rule_name (rule_name),
    INDEX idx_alarm_category (alarm_category),
    INDEX idx_alarm_level (alarm_level),
    INDEX idx_rule_type (rule_type),
    INDEX idx_enabled (enabled),
    INDEX idx_is_global (is_global),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_rule_name_active (rule_name, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报警规则表';

-- 创建报警规则关联表
CREATE TABLE tb_alarm_rule_relation (
    id VARCHAR(36) PRIMARY KEY COMMENT '关联ID',
    alarm_rule_id VARCHAR(36) NOT NULL COMMENT '报警规则ID',
    relation_type ENUM('item', 'gimbal', 'sensor') NOT NULL COMMENT '关联类型',
    relation_id VARCHAR(36) NOT NULL COMMENT '关联对象ID',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '顺序，用于多数据源规则',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    INDEX idx_alarm_rule_id (alarm_rule_id),
    INDEX idx_relation_type_id (relation_type, relation_id),
    INDEX idx_sort_order (alarm_rule_id, sort_order),
    UNIQUE KEY uk_rule_relation (alarm_rule_id, relation_type, relation_id),
    FOREIGN KEY (alarm_rule_id) REFERENCES tb_alarm_rule(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报警规则关联表';

-- 创建报警信息表
CREATE TABLE tb_alarm_info (
    id VARCHAR(36) PRIMARY KEY COMMENT '报警信息ID',
    alarm_rule_id VARCHAR(36) NOT NULL COMMENT '报警规则ID',
    alarm_category ENUM('robot', 'inspection', 'gimbal', 'sensor', 'other') NOT NULL COMMENT '报警分类',
    alarm_level INT NOT NULL COMMENT '报警等级 1-10',
    alarm_status ENUM('unviewed', 'unprocessed', 'processed') NOT NULL DEFAULT 'unviewed' COMMENT '报警状态',
    source_type ENUM('itemhistory', 'gimbalhistory', 'sensorhistory', 'taskhistory', 'robot_status') NOT NULL COMMENT '数据源类型',
    source_ids JSON NOT NULL COMMENT '数据源ID列表，按关联表顺序排列，格式：["id1", "id2", "id3"]',
    relation_type ENUM('item', 'gimbal', 'sensor', 'none') NULL COMMENT '关联对象类型',
    relation_ids JSON NULL COMMENT '关联对象ID列表，格式：["id1", "id2"]',
    trigger_item_ids JSON NULL COMMENT '触发源对应的巡检项目ID列表（当source_type=itemhistory时）',
    trigger_project_ids JSON NULL COMMENT '触发源对应的云台巡检项目ID列表（当source_type=gimbalhistory时）',
    trigger_data JSON NULL COMMENT '触发时的完整数据快照',
    calculated_value JSON NULL COMMENT '计算后的值（如平均值、和值等）',
    alarm_message TEXT NULL COMMENT '报警信息',
    processed_by VARCHAR(100) NULL COMMENT '处理人',
    processed_at DATETIME NULL COMMENT '处理时间',
    process_remark TEXT NULL COMMENT '处理备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_alarm_rule_id (alarm_rule_id),
    INDEX idx_alarm_category (alarm_category),
    INDEX idx_alarm_level (alarm_level),
    INDEX idx_alarm_status (alarm_status),
    INDEX idx_source_type (source_type),
    INDEX idx_relation_type (relation_type),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    -- 注意：去重逻辑在应用层处理，因为JSON字段不能直接用于唯一索引
    FOREIGN KEY (alarm_rule_id) REFERENCES tb_alarm_rule(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报警信息表';

-- 创建手动操作记录表
CREATE TABLE tb_manual_operation (
    id VARCHAR(36) PRIMARY KEY COMMENT '手动操作记录ID',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    operation_time DATETIME NOT NULL COMMENT '操作时间',
    operation_content JSON NOT NULL COMMENT '操作内容JSON',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(50) NULL COMMENT '创建者',
    updated_by VARCHAR(50) NULL COMMENT '更新者',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_user_id (user_id),
    INDEX idx_username (username),
    INDEX idx_operation_time (operation_time),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='手动操作记录表';

-- 创建操作记录表
CREATE TABLE tb_operation_record (
    id VARCHAR(36) PRIMARY KEY COMMENT '操作记录ID',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    operation_time DATETIME NOT NULL COMMENT '操作时间',
    operation_content JSON NOT NULL COMMENT '操作内容JSON',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(50) NULL COMMENT '创建者',
    updated_by VARCHAR(50) NULL COMMENT '更新者',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_user_id (user_id),
    INDEX idx_username (username),
    INDEX idx_operation_time (operation_time),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作记录表';
