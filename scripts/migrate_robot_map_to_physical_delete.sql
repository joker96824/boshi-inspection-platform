-- 博实智能巡检平台 - 机器人-地图关联表改为物理删除
-- 此脚本用于更新已有数据库的唯一约束

USE boshirobot;

-- ============================================
-- 1. 删除旧的唯一约束
-- ============================================
SET @dbname = DATABASE();
SET @tablename = 'tb_robot_map';
SET @constraintname = 'uk_robot_map_active';

SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE
            (TABLE_SCHEMA = @dbname)
            AND (TABLE_NAME = @tablename)
            AND (CONSTRAINT_NAME = @constraintname)
    ) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP INDEX ', @constraintname),
    'SELECT 1'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- ============================================
-- 2. 物理删除所有已软删除的记录
-- ============================================
DELETE FROM tb_robot_map WHERE is_deleted = TRUE;

-- ============================================
-- 3. 创建新的唯一约束（不包含 is_deleted）
-- ============================================
SET @constraintname = 'uk_robot_map';
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE
            (TABLE_SCHEMA = @dbname)
            AND (TABLE_NAME = @tablename)
            AND (CONSTRAINT_NAME = @constraintname)
    ) > 0,
    'SELECT 1',
    CONCAT('ALTER TABLE ', @tablename, ' ADD CONSTRAINT ', @constraintname, ' UNIQUE (robot_id, map_id)')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- 4. 删除 is_deleted 索引（可选，保留字段但不使用）
-- ============================================
SET @indexname = 'idx_is_deleted';
SET @preparedStatement = (SELECT IF(
    (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
        WHERE
            (TABLE_SCHEMA = @dbname)
            AND (TABLE_NAME = @tablename)
            AND (INDEX_NAME = @indexname)
    ) > 0,
    CONCAT('ALTER TABLE ', @tablename, ' DROP INDEX ', @indexname),
    'SELECT 1'
));
PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- ============================================
-- 脚本执行完成
-- ============================================
SELECT '机器人-地图关联表已改为物理删除' AS message;

