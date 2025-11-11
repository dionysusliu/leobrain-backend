# crawlers/core/crawler_service.py (新建)
"""爬虫服务层"""
import logging
import os
from typing import Dict

from crawlers.core.engine import CrawlerEngine
from crawlers.core.spiders.rss_spider import RSSSpider
from common.logging_helpers import (
    log_crawl_start,
    log_crawl_complete,
    log_crawl_error
)

# 初始化日志配置（确保在容器环境中正确输出）
from common.logging_config import setup_logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))

logger = logging.getLogger(__name__)


async def crawl_site(site_name: str, config: Dict):
    """
    Crawl a single site
    
    Args:
        site_name: Name of the site
        config: Site configuration
    """
    log_crawl_start(logger, site_name, config)
    
    try:
        # Create spider based on config
        spider_type = config.get('spider', 'rss')
        
        if spider_type == 'rss':
            spider = RSSSpider(
                source_name=config['source_name'],
                feed_url=config['feed_url'],
                max_items=config.get('max_items'),
                fetch_full_content=config.get('fetch_full_content', False)
            )
        else:
            raise ValueError(f"Unknown spider type: {spider_type}")
        
        # Create engine and crawl
        engine = CrawlerEngine()
        result = await engine.crawl_spider(spider, config)
        await engine.close()
        
        log_crawl_complete(logger, site_name, result)
        
    except Exception as e:
        log_crawl_error(logger, site_name, e, config)
        raise