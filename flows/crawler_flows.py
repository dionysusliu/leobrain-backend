"""Crawler prefect flows"""
from prefect import flow, tags
from prefect.context import get_run_context
import logging
import os

from .crawler_tasks import pf_task_crawl_one_site 
from configs.types import SiteConfig

# 初始化日志（在容器环境中输出到 stdout）
from common.logging_config import setup_logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))

logger = logging.getLogger(__name__)

@flow(name="crawl_site_by_name", log_prints=True)
async def pf_flow_crawl_site_by_name(site_name: str, config: SiteConfig):
   """
    Crawl from one site
   
    Returns:
        Flow Run ID (for tracking) 
   """ 
   with tags("crawler", site_name):
        logger.info(f"Starting crawl flow for site: {site_name}")
        result = await pf_task_crawl_one_site(site_name, config)
       
        try:
           run_context = get_run_context()
           if run_context and hasattr(run_context, 'flow_run'):
               logger.info(f"Flow completed: {site_name}, run_id={run_context.flow_run.id}")
               return run_context.flow_run.id
        except Exception:
           pass
        
        return result

