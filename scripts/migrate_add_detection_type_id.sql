-- 添加 detection_type_id 字段到 tb_item 表
-- 如果字段已存在，则跳过

-- 检查并添加 detection_type_id 字段
SET @dbname = DATABASE();
SET @tablename = "tb_item";
SET @columnname = "detection_type_id";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 'Column already exists.'",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " VARCHAR(36) NULL COMMENT '检测类型ID'")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 检查并添加索引
SET @indexname = "idx_detection_type_id";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (index_name = @indexname)
  ) > 0,
  "SELECT 'Index already exists.'",
  CONCAT("CREATE INDEX ", @indexname, " ON ", @tablename, " (", @columnname, ")")
));
PREPARE createIndexIfNotExists FROM @preparedStatement;
EXECUTE createIndexIfNotExists;
DEALLOCATE PREPARE createIndexIfNotExists;

-- 检查并添加外键（需要先确保 tb_detection_type 表存在）
SET @fkname = "fk_item_detection_type";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (constraint_name = @fkname)
  ) > 0,
  "SELECT 'Foreign key already exists.'",
  CONCAT("ALTER TABLE ", @tablename, " ADD CONSTRAINT ", @fkname, " FOREIGN KEY (", @columnname, ") REFERENCES tb_detection_type(id) ON DELETE SET NULL")
));
PREPARE createFKIfNotExists FROM @preparedStatement;
EXECUTE createFKIfNotExists;
DEALLOCATE PREPARE createFKIfNotExists;

