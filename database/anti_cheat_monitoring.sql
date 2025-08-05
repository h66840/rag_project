-- =====================================================
-- 游戏反作弊监控系统 SQL 脚本
-- 功能：检测玩家货币余额异常增长，防止外挂和非法工作室
-- 作者：反作弊系统开发团队
-- 创建时间：2025-01-05
-- =====================================================

-- 1. 创建玩家钱包表
-- 存储玩家的货币余额信息
CREATE TABLE IF NOT EXISTS player_wallets (
    player_id INTEGER NOT NULL,
    currency_balance BIGINT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    previous_balance BIGINT,
    CONSTRAINT pk_player_wallets PRIMARY KEY (player_id)
);

-- 2. 创建可疑活动记录表
-- 用于记录检测到的可疑货币交易
CREATE TABLE IF NOT EXISTS suspicious_activity (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    previous_balance BIGINT NOT NULL,
    new_balance BIGINT NOT NULL,
    currency_increase BIGINT NOT NULL,
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    notes TEXT,
    CONSTRAINT fk_suspicious_activity_player 
        FOREIGN KEY (player_id) REFERENCES player_wallets(player_id)
);

-- 3. 创建触发器函数
-- 检测货币余额异常增长的核心逻辑
CREATE OR REPLACE FUNCTION check_suspicious_currency_increase()
RETURNS TRIGGER AS $$
DECLARE
    currency_increase BIGINT;
    threshold CONSTANT BIGINT := 1000000; -- 1,000,000 阈值
BEGIN
    -- 只在UPDATE操作时检查
    IF TG_OP = 'UPDATE' THEN
        -- 计算货币增量
        currency_increase := NEW.currency_balance - OLD.currency_balance;
        
        -- 检查增量是否超过阈值
        IF currency_increase > threshold THEN
            -- 记录可疑活动
            INSERT INTO suspicious_activity (
                player_id,
                previous_balance,
                new_balance,
                currency_increase,
                detected_at,
                status,
                notes
            ) VALUES (
                NEW.player_id,
                OLD.currency_balance,
                NEW.currency_balance,
                currency_increase,
                CURRENT_TIMESTAMP,
                'PENDING',
                '检测到可疑货币增长: 单次交易增加 ' || currency_increase || ' 金币'
            );
            
            -- 记录日志（可选）
            RAISE NOTICE '检测到玩家 % 的可疑活动: 货币增加 % 金币', 
                NEW.player_id, currency_increase;
        END IF;
        
        -- 更新previous_balance用于跟踪
        NEW.previous_balance := OLD.currency_balance;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. 创建触发器
-- 在player_wallets表更新时自动调用检测函数
DROP TRIGGER IF EXISTS anti_cheat_monitor ON player_wallets;
CREATE TRIGGER anti_cheat_monitor
    BEFORE UPDATE ON player_wallets
    FOR EACH ROW
    EXECUTE FUNCTION check_suspicious_currency_increase();

-- 5. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_player_wallets_player_id 
    ON player_wallets(player_id);

CREATE INDEX IF NOT EXISTS idx_suspicious_activity_player_id 
    ON suspicious_activity(player_id);

CREATE INDEX IF NOT EXISTS idx_suspicious_activity_detected_at 
    ON suspicious_activity(detected_at);

CREATE INDEX IF NOT EXISTS idx_suspicious_activity_status 
    ON suspicious_activity(status);

-- 6. 插入测试数据（可选）
INSERT INTO player_wallets (player_id, currency_balance, previous_balance) VALUES 
(1001, 50000, 45000),
(1002, 120000, 115000),
(1003, 75000, 70000),
(1004, 200000, 180000),
(1005, 30000, 25000)
ON CONFLICT (player_id) DO NOTHING;

-- 7. 创建管理员查询视图
-- 方便GM查看可疑活动
CREATE OR REPLACE VIEW v_suspicious_activity_summary AS
SELECT 
    sa.id,
    sa.player_id,
    sa.previous_balance,
    sa.new_balance,
    sa.currency_increase,
    sa.detected_at,
    sa.status,
    sa.notes,
    pw.currency_balance as current_balance
FROM suspicious_activity sa
LEFT JOIN player_wallets pw ON sa.player_id = pw.player_id
ORDER BY sa.detected_at DESC;

-- 8. 创建管理员操作函数
-- 用于GM审查和处理可疑活动
CREATE OR REPLACE FUNCTION update_suspicious_activity_status(
    activity_id INTEGER,
    new_status VARCHAR(20),
    admin_notes TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE suspicious_activity 
    SET 
        status = new_status,
        notes = CASE 
            WHEN admin_notes IS NOT NULL THEN 
                notes || ' | GM处理: ' || admin_notes 
            ELSE notes 
        END
    WHERE id = activity_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- 9. 创建统计查询函数
-- 获取反作弊系统统计信息
CREATE OR REPLACE FUNCTION get_anti_cheat_stats(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '7 days',
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    total_suspicious_activities BIGINT,
    pending_reviews BIGINT,
    confirmed_cheats BIGINT,
    false_positives BIGINT,
    avg_suspicious_amount NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_suspicious_activities,
        COUNT(*) FILTER (WHERE status = 'PENDING') as pending_reviews,
        COUNT(*) FILTER (WHERE status = 'CONFIRMED') as confirmed_cheats,
        COUNT(*) FILTER (WHERE status = 'FALSE_POSITIVE') as false_positives,
        AVG(currency_increase) as avg_suspicious_amount
    FROM suspicious_activity 
    WHERE detected_at::DATE BETWEEN start_date AND end_date;
END;
$$ LANGUAGE plpgsql;

-- 10. 权限设置（根据实际需求调整）
-- 为游戏服务器账户授予必要权限
-- GRANT SELECT, INSERT, UPDATE ON player_wallets TO game_server_user;
-- GRANT SELECT, INSERT ON suspicious_activity TO game_server_user;
-- GRANT SELECT ON v_suspicious_activity_summary TO gm_user;
-- GRANT EXECUTE ON FUNCTION update_suspicious_activity_status TO gm_user;
-- GRANT EXECUTE ON FUNCTION get_anti_cheat_stats TO gm_user;

-- =====================================================
-- 使用说明：
-- 1. 执行此脚本创建反作弊监控系统
-- 2. 游戏服务器更新玩家货币时，触发器会自动检测异常
-- 3. GM可通过 v_suspicious_activity_summary 视图查看可疑活动
-- 4. 使用 update_suspicious_activity_status() 函数处理可疑活动
-- 5. 使用 get_anti_cheat_stats() 函数获取统计信息
-- =====================================================

-- 测试示例：
-- 更新玩家货币（触发检测）
-- UPDATE player_wallets SET currency_balance = 1150000 WHERE player_id = 1001;

-- 查看可疑活动
-- SELECT * FROM v_suspicious_activity_summary;

-- 处理可疑活动
-- SELECT update_suspicious_activity_status(1, 'CONFIRMED', '确认为外挂行为');

-- 获取统计信息
-- SELECT * FROM get_anti_cheat_stats();