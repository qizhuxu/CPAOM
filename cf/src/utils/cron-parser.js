/**
 * 简单的 Cron 表达式解析器
 * 支持标准的 5 字段格式：分 时 日 月 周
 */

/**
 * 解析 Cron 表达式
 * @param {string} expression - Cron 表达式，如 "0 * * * *"
 * @returns {object} 解析后的对象
 */
export function parseCronExpression(expression) {
  const parts = expression.trim().split(/\s+/);
  
  if (parts.length !== 5) {
    throw new Error('Cron expression must have 5 fields: minute hour day month weekday');
  }
  
  return {
    minute: parts[0],
    hour: parts[1],
    day: parts[2],
    month: parts[3],
    weekday: parts[4]
  };
}

/**
 * 获取下次执行时间
 * @param {string} cronExpression - Cron 表达式
 * @param {Date} from - 起始时间，默认为当前时间
 * @returns {string} ISO 8601 格式的下次执行时间
 */
export function getNextRunTime(cronExpression, from = new Date()) {
  const cron = parseCronExpression(cronExpression);
  const now = new Date(from);
  
  // 简化实现：只支持常见模式
  // 完整实现需要更复杂的逻辑
  
  // 每小时执行（0 * * * *）
  if (cron.minute === '0' && cron.hour === '*') {
    const next = new Date(now);
    next.setHours(next.getHours() + 1);
    next.setMinutes(0);
    next.setSeconds(0);
    next.setMilliseconds(0);
    return next.toISOString();
  }
  
  // 每天特定时间执行（0 2 * * *）
  if (cron.minute !== '*' && cron.hour !== '*' && cron.day === '*') {
    const next = new Date(now);
    next.setHours(parseInt(cron.hour));
    next.setMinutes(parseInt(cron.minute));
    next.setSeconds(0);
    next.setMilliseconds(0);
    
    // 如果今天的时间已过，设置为明天
    if (next <= now) {
      next.setDate(next.getDate() + 1);
    }
    
    return next.toISOString();
  }
  
  // 每 N 分钟执行（*/15 * * * *）
  if (cron.minute.startsWith('*/')) {
    const interval = parseInt(cron.minute.substring(2));
    const next = new Date(now);
    const currentMinute = next.getMinutes();
    const nextMinute = Math.ceil((currentMinute + 1) / interval) * interval;
    
    if (nextMinute >= 60) {
      next.setHours(next.getHours() + 1);
      next.setMinutes(nextMinute - 60);
    } else {
      next.setMinutes(nextMinute);
    }
    
    next.setSeconds(0);
    next.setMilliseconds(0);
    return next.toISOString();
  }
  
  // 默认：1小时后
  const next = new Date(now);
  next.setHours(next.getHours() + 1);
  return next.toISOString();
}

/**
 * 常用的 Cron 表达式预设
 */
export const CRON_PRESETS = {
  EVERY_HOUR: '0 * * * *',           // 每小时
  EVERY_2_HOURS: '0 */2 * * *',      // 每2小时
  EVERY_6_HOURS: '0 */6 * * *',      // 每6小时
  EVERY_12_HOURS: '0 */12 * * *',    // 每12小时
  DAILY_2AM: '0 2 * * *',            // 每天凌晨2点
  DAILY_MIDNIGHT: '0 0 * * *',       // 每天午夜
  EVERY_15_MIN: '*/15 * * * *',      // 每15分钟
  EVERY_30_MIN: '*/30 * * * *',      // 每30分钟
};

/**
 * 验证 Cron 表达式是否有效
 */
export function isValidCronExpression(expression) {
  try {
    parseCronExpression(expression);
    return true;
  } catch {
    return false;
  }
}
