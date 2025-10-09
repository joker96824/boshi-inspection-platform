-- 重置admin账号密码为"admin"
-- 博实智能巡检平台 - 管理员密码重置脚本

USE boshirobot;

-- 更新admin用户的密码
UPDATE tb_users 
SET 
    password_hash = '$2b$12$1V3nujFOOo6ILl3J5U7gT.VuYEjJHK1i9nPZfP65RipQzccYT0cgK',
    updated_at = NOW(),
    updated_by = 'system'
WHERE 
    username = 'admin' 
    AND is_deleted = FALSE;

-- 使所有admin用户的现有会话失效（强制重新登录）
UPDATE tb_sessions 
SET 
    is_deleted = TRUE,
    updated_at = NOW(),
    updated_by = 'system'
WHERE 
    user_id = (
        SELECT id FROM tb_users 
        WHERE username = 'admin' AND is_deleted = FALSE 
        LIMIT 1
    )
    AND is_deleted = FALSE;

-- 显示重置结果
SELECT 
    'Admin password reset completed successfully!' as status,
    'Password: admin' as password_info,
    'All existing sessions have been invalidated' as session_info;

-- 验证admin用户信息
SELECT 
    id,
    username,
    role,
    updated_at,
    updated_by,
    'Password successfully reset' as password_status
FROM tb_users 
WHERE username = 'admin' AND is_deleted = FALSE;

