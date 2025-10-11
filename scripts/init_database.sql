-- 博实智能巡检平台 - 数据库初始化SQL
-- 创建数据库
CREATE DATABASE IF NOT EXISTS boshirobot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE boshirobot;

-- 删除现有表（如果存在）- 按外键依赖顺序删除
DROP TABLE IF EXISTS tb_alarminfo;
DROP TABLE IF EXISTS tb_alarmrule;
DROP TABLE IF EXISTS tb_taskresult;
DROP TABLE IF EXISTS tb_itemhistory;
DROP TABLE IF EXISTS tb_point_item;
DROP TABLE IF EXISTS tb_item;
DROP TABLE IF EXISTS tb_taskhistory;
DROP TABLE IF EXISTS tb_taskschedule;
DROP TABLE IF EXISTS tb_task;
DROP TABLE IF EXISTS tb_point;
DROP TABLE IF EXISTS tb_mapnet;
DROP TABLE IF EXISTS tb_robot;
DROP TABLE IF EXISTS tb_map;
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
    INDEX idx_token (token),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表';

-- 创建地图表
CREATE TABLE tb_map (
    id VARCHAR(36) PRIMARY KEY COMMENT '地图ID',
    map_name VARCHAR(100) NOT NULL COMMENT '地图名称',
    map_image_url VARCHAR(500) NULL COMMENT '图片地址',
    map_scale DECIMAL(10,6) NULL COMMENT '比例尺',
    map_center_x DECIMAL(15,6) NULL COMMENT '中心点横坐标',
    map_center_y DECIMAL(15,6) NULL COMMENT '中心点纵坐标',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_map_name (map_name),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_map_name_active (map_name, is_deleted)
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
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_robot_name (robot_name),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_robot_name_active (robot_name, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='机器人表';

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
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_item_name (item_name),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_item_name_active (item_name, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='巡检项目表';

-- 创建巡检中间表
CREATE TABLE tb_point_item (
    id VARCHAR(36) PRIMARY KEY COMMENT '巡检中间表ID',
    point_id VARCHAR(36) NOT NULL COMMENT '巡检点ID',
    item_id VARCHAR(36) NOT NULL COMMENT '巡检项目ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_point_id (point_id),
    INDEX idx_item_id (item_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_point_item_active (point_id, item_id, is_deleted),
    FOREIGN KEY (point_id) REFERENCES tb_point(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES tb_item(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='巡检中间表';

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
    INDEX idx_taskhistory_id (taskhistory_id),
    INDEX idx_record_batch (record_batch),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (taskhistory_id) REFERENCES tb_taskhistory(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务结果表';

-- 创建报警规则表
CREATE TABLE tb_alarmrule (
    id VARCHAR(36) PRIMARY KEY COMMENT '报警规则ID',
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    item_id VARCHAR(36) NOT NULL COMMENT '巡检项目ID',
    alarm_param JSON NULL COMMENT '报警参数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_rule_name (rule_name),
    INDEX idx_item_id (item_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    UNIQUE KEY uk_rule_name_active (rule_name, is_deleted),
    FOREIGN KEY (item_id) REFERENCES tb_item(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报警规则表';

-- 创建报警信息表
CREATE TABLE tb_alarminfo (
    id VARCHAR(36) PRIMARY KEY COMMENT '报警信息ID',
    alarmrule_id VARCHAR(36) NOT NULL COMMENT '报警规则ID',
    itemhistory_id VARCHAR(36) NOT NULL COMMENT '巡检记录ID',
    alarm_data JSON NULL COMMENT '触发数据',
    alarm_info TEXT NULL COMMENT '报警信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(100) NULL COMMENT '创建人',
    updated_by VARCHAR(100) NULL COMMENT '更新人',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否删除',
    INDEX idx_alarmrule_id (alarmrule_id),
    INDEX idx_itemhistory_id (itemhistory_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY (alarmrule_id) REFERENCES tb_alarmrule(id) ON DELETE CASCADE,
    FOREIGN KEY (itemhistory_id) REFERENCES tb_itemhistory(id) ON DELETE CASCADE
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

-- 插入示例地图数据
INSERT INTO tb_map (
    id,
    map_name,
    map_image_url,
    map_scale,
    map_center_x,
    map_center_y,
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
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440002',
    '巡检机器人001',
    '{"model": "BOSHI-RB-01", "battery": 100, "status": "idle"}',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
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
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655440009',
    '拍照记录',
    '{}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440010',
    '安全检查',
    '{}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440011',
    '设备状态检查',
    '{}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440012',
    '环境监测',
    '{}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440013',
    '清洁检查',
    '{}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440014',
    '照明检查',
    '{}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440601',
    '温度检测',
    '{}',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440602',
    '消防检查',
    '{}',
    NOW(),
    NOW(),
    'operator',
    'operator',
    FALSE
);

-- 插入示例巡检中间表数据（体现多对多关系）
INSERT INTO tb_point_item (
    id,
    point_id,
    item_id,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    -- 一楼入口检查点的项目
    '550e8400-e29b-41d4-a716-446655440015',
    '550e8400-e29b-41d4-a716-446655440005',
    '550e8400-e29b-41d4-a716-446655440009',
    NOW(),
    NOW(),
    'superadmin',
    'superadmin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440016',
    '550e8400-e29b-41d4-a716-446655440005',
    '550e8400-e29b-41d4-a716-446655440010',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    -- 设备间检查点的项目
    '550e8400-e29b-41d4-a716-446655440017',
    '550e8400-e29b-41d4-a716-446655440006',
    '550e8400-e29b-41d4-a716-446655440011',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440018',
    '550e8400-e29b-41d4-a716-446655440006',
    '550e8400-e29b-41d4-a716-446655440012',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    -- 走廊检查点的项目
    '550e8400-e29b-41d4-a716-446655440019',
    '550e8400-e29b-41d4-a716-446655440007',
    '550e8400-e29b-41d4-a716-446655440013',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440020',
    '550e8400-e29b-41d4-a716-446655440007',
    '550e8400-e29b-41d4-a716-446655440014',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    -- 多对多关系：拍照记录被多个检查点使用
    '550e8400-e29b-41d4-a716-446655440021',
    '550e8400-e29b-41d4-a716-446655440006',
    '550e8400-e29b-41d4-a716-446655440009',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440022',
    '550e8400-e29b-41d4-a716-446655440007',
    '550e8400-e29b-41d4-a716-446655440009',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    -- 多对多关系：安全检查被多个检查点使用
    '550e8400-e29b-41d4-a716-446655440023',
    '550e8400-e29b-41d4-a716-446655440006',
    '550e8400-e29b-41d4-a716-446655440010',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440024',
    '550e8400-e29b-41d4-a716-446655440007',
    '550e8400-e29b-41d4-a716-446655440010',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    -- 出口检查点
    '550e8400-e29b-41d4-a716-446655440701',
    '550e8400-e29b-41d4-a716-446655440008',
    '550e8400-e29b-41d4-a716-446655440009',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655440702',
    '550e8400-e29b-41d4-a716-446655440008',
    '550e8400-e29b-41d4-a716-446655440010',
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
    item_id,
    alarm_param,
    created_at,
    updated_at,
    created_by,
    updated_by,
    is_deleted
) VALUES (
    '550e8400-e29b-41d4-a716-446655441101',
    '温度异常报警',
    '550e8400-e29b-41d4-a716-446655440601',
    '{"threshold": 40, "operator": "gt", "level": "warning"}',
    NOW(),
    NOW(),
    'admin',
    'admin',
    FALSE
), (
    '550e8400-e29b-41d4-a716-446655441102',
    '设备故障报警',
    '550e8400-e29b-41d4-a716-446655440011',
    '{"check_field": "equipment_status", "expected": "正常", "level": "critical"}',
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
    itemhistory_id,
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
    '550e8400-e29b-41d4-a716-446655441003',
    '{"actual_value": "正常", "expected_value": "正常", "match": true}',
    '设备状态正常，符合预期',
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
SELECT '3个用户, 1个地图, 1个机器人, 1个任务' as summary1;
SELECT '3条地图路网, 4个巡检点, 8个巡检项目, 12个点-项关联' as summary2;
SELECT '2条任务日程, 3条任务记录, 3条任务结果, 5条巡检记录' as summary3;
SELECT '2条报警规则, 1条报警信息' as summary4;
SELECT 'Token expiry: 30 days (2592000 seconds)' as token_info;
SELECT 'Roles: super_admin > admin > operator > viewer > user' as role_info;
