# 游戏反作弊监控系统

## 概述

本系统是为了打击游戏内的外挂和非法工作室而设计的反作弊监控机制。当玩家的货币余额发生更新时，系统会自动检查单次交易的货币增量是否超过预设阈值（1,000,000金币），如果超过则将该次交易的详细信息记录到可疑活动表中，供游戏管理员（GM）审查。

## 系统架构

### 核心组件

1. **player_wallets表** - 存储玩家货币余额信息
2. **suspicious_activity表** - 记录可疑的货币交易活动
3. **触发器函数** - 自动检测异常货币增长
4. **管理视图** - 方便GM查看和管理可疑活动
5. **统计函数** - 提供反作弊系统运行统计

### 工作流程

```
玩家货币更新 → 触发器检测 → 超过阈值 → 记录可疑活动 → GM审查处理
```

## 部署指南

### 1. 环境要求

- PostgreSQL 12+
- 具有CREATE TABLE、CREATE FUNCTION权限的数据库用户

### 2. 安装步骤

```bash
# 1. 连接到数据库
psql -h localhost -U your_user -d your_database

# 2. 执行安装脚本
\i database/anti_cheat_monitoring.sql
```

### 3. 权限配置

根据实际需求，为不同角色分配适当权限：

```sql
-- 游戏服务器权限
GRANT SELECT, INSERT, UPDATE ON player_wallets TO game_server_user;
GRANT SELECT, INSERT ON suspicious_activity TO game_server_user;

-- GM权限
GRANT SELECT ON v_suspicious_activity_summary TO gm_user;
GRANT EXECUTE ON FUNCTION update_suspicious_activity_status TO gm_user;
GRANT EXECUTE ON FUNCTION get_anti_cheat_stats TO gm_user;
```

## 使用说明

### GM操作指南

#### 1. 查看可疑活动

```sql
-- 查看所有可疑活动
SELECT * FROM v_suspicious_activity_summary;

-- 查看待处理的可疑活动
SELECT * FROM v_suspicious_activity_summary WHERE status = 'PENDING';
```

#### 2. 处理可疑活动

```sql
-- 确认为作弊行为
SELECT update_suspicious_activity_status(1, 'CONFIRMED', '确认为外挂行为，已封号处理');

-- 标记为误报
SELECT update_suspicious_activity_status(2, 'FALSE_POSITIVE', '正常的游戏内交易');
```

#### 3. 获取统计信息

```sql
-- 获取最近7天的统计
SELECT * FROM get_anti_cheat_stats();

-- 获取指定时间段的统计
SELECT * FROM get_anti_cheat_stats('2025-01-01', '2025-01-31');
```

### 开发者集成

#### 游戏服务器端集成

```python
# Python示例：更新玩家货币
import psycopg2

def update_player_currency(player_id, new_balance):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 更新玩家货币余额（触发器会自动检测）
        cur.execute(
            "UPDATE player_wallets SET currency_balance = %s WHERE player_id = %s",
            (new_balance, player_id)
        )
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"更新失败: {e}")
        return False
    finally:
        conn.close()
```

## 配置参数

### 阈值调整

如需修改检测阈值，可以更新触发器函数：

```sql
-- 修改阈值为500,000
CREATE OR REPLACE FUNCTION check_suspicious_currency_increase()
RETURNS TRIGGER AS $$
DECLARE
    currency_increase BIGINT;
    threshold CONSTANT BIGINT := 500000; -- 修改这里
BEGIN
    -- ... 其余代码保持不变
END;
$$ LANGUAGE plpgsql;
```

### 状态类型

可疑活动的状态类型：

- `PENDING` - 待审查
- `CONFIRMED` - 确认作弊
- `FALSE_POSITIVE` - 误报
- `INVESTIGATING` - 调查中

## 监控和维护

### 1. 性能监控

```sql
-- 检查触发器性能
SELECT schemaname, tablename, n_tup_upd, n_tup_hot_upd 
FROM pg_stat_user_tables 
WHERE tablename = 'player_wallets';

-- 检查可疑活动表大小
SELECT pg_size_pretty(pg_total_relation_size('suspicious_activity'));
```

### 2. 数据清理

建议定期清理已处理的旧记录：

```sql
-- 删除30天前已处理的记录
DELETE FROM suspicious_activity 
WHERE detected_at < CURRENT_DATE - INTERVAL '30 days' 
AND status IN ('CONFIRMED', 'FALSE_POSITIVE');
```

### 3. 备份策略

```bash
# 备份可疑活动数据
pg_dump -h localhost -U user -d database -t suspicious_activity > suspicious_activity_backup.sql
```

## 故障排除

### 常见问题

1. **触发器未生效**
   - 检查触发器是否正确创建：`\dS player_wallets`
   - 确认函数权限：`\df check_suspicious_currency_increase`

2. **性能问题**
   - 检查索引是否存在：`\di`
   - 考虑分区大表

3. **误报过多**
   - 调整检测阈值
   - 增加更复杂的检测逻辑

### 日志查看

```sql
-- 查看PostgreSQL日志中的NOTICE信息
SHOW log_destination;
SHOW log_statement;
```

## 安全考虑

1. **权限最小化** - 严格控制数据库访问权限
2. **数据加密** - 敏感数据传输加密
3. **审计日志** - 记录所有GM操作
4. **定期审查** - 定期检查系统配置和权限

## 版本历史

- v1.0.0 (2025-01-05) - 初始版本，基础反作弊监控功能

## 联系方式

如有问题或建议，请联系开发团队或提交Issue。