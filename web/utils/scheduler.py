"""
定时任务调度器 - 动态任务管理
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = None


def init_scheduler(app, db_service, config_manager):
    """初始化定时任务调度器"""
    global scheduler
    
    if scheduler is not None:
        logger.warning("调度器已经初始化")
        return scheduler
    
    scheduler = BackgroundScheduler()
    
    # 启动调度器
    scheduler.start()
    logger.info("定时任务调度器已启动")
    
    # 加载所有服务器的同步任务
    load_sync_tasks(app, db_service, config_manager)
    
    return scheduler


def load_sync_tasks(app, db_service, config_manager):
    """加载所有服务器的同步任务"""
    try:
        servers = config_manager.get_servers()
        
        for server in servers:
            server_id = server['id']
            server_name = server['name']
            
            # 获取同步配置
            sync_config = db_service.get_sync_config(server_id)
            
            if not sync_config:
                logger.info(f"服务器 {server_name} 没有同步配置，跳过")
                continue
            
            sync_interval = sync_config.get('sync_interval', 3600)
            
            # 添加定时同步任务
            add_sync_task(app, db_service, config_manager, server_id, server_name, sync_interval)
            
        logger.info(f"已加载 {len(servers)} 个服务器的同步任务")
        
    except Exception as e:
        logger.error(f"加载同步任务失败: {e}")


def add_sync_task(app, db_service, config_manager, server_id, server_name, interval_seconds):
    """添加服务器同步任务"""
    global scheduler
    
    if scheduler is None:
        logger.error("调度器未初始化")
        return
    
    job_id = f"sync_{server_id}"
    
    # 移除已存在的任务
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"移除旧的同步任务: {server_name}")
    
    # 创建同步任务函数（使用默认参数捕获变量）
    def sync_task(sid=server_id, sname=server_name, db=db_service, cfg=config_manager):
        """执行服务器同步"""
        with app.app_context():
            try:
                logger.info(f"开始自动同步: {sname}")
                
                # 导入同步函数
                from routes.sync import perform_enhanced_sync
                
                # 执行增强同步
                result = perform_enhanced_sync(sid, db, cfg)
                
                if result['success']:
                    logger.info(f"自动同步完成: {sname}, 处理了 {result['total_processed']} 个账号")
                else:
                    logger.error(f"自动同步失败: {sname}, {result.get('error')}")
                
            except Exception as e:
                logger.error(f"自动同步异常: {sname}, {e}")
                import traceback
                logger.error(traceback.format_exc())
    
    # 添加定时任务
    scheduler.add_job(
        sync_task,
        trigger=IntervalTrigger(seconds=interval_seconds),
        id=job_id,
        name=f"同步 {server_name}",
        replace_existing=True
    )
    
    logger.info(f"已添加同步任务: {server_name}, 间隔 {interval_seconds} 秒")


def remove_sync_task(server_id):
    """移除服务器同步任务"""
    global scheduler
    
    if scheduler is None:
        logger.error("调度器未初始化")
        return
    
    job_id = f"sync_{server_id}"
    
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"已移除同步任务: {server_id}")


def update_sync_task(app, db_service, config_manager, server_id, server_name, interval_seconds):
    """更新服务器同步任务"""
    logger.info(f"更新同步任务: {server_name}, 新间隔 {interval_seconds} 秒")
    add_sync_task(app, db_service, config_manager, server_id, server_name, interval_seconds)


def get_all_jobs():
    """获取所有任务"""
    global scheduler
    
    if scheduler is None:
        return []
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
        })
    
    return jobs


def shutdown_scheduler():
    """关闭调度器"""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")
        scheduler = None

