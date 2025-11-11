"""Logging helper functions for structured logging with context"""
import logging
from typing import Any, Dict, Optional, List
from crawlers.core.types import Item, Request, Response


def _get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)


def log_crawl_start(logger: logging.Logger, site_name: str, config: Dict[str, Any]):
    """Log crawl task start with context"""
    logger.info(
        f"Starting crawl task for {site_name}",
        extra={
            "extra_fields": {
                "site_name": site_name,
                "spider_type": config.get('spider', 'rss'),
                "feed_url": config.get('feed_url'),
                "max_items": config.get('max_items'),
                "fetch_full_content": config.get('fetch_full_content', False),
            }
        }
    )


def log_crawl_complete(logger: logging.Logger, site_name: str, items_processed: int):
    """Log crawl task completion with context"""
    logger.info(
        f"Completed crawl task for {site_name}, processed {items_processed} items",
        extra={
            "extra_fields": {
                "site_name": site_name,
                "items_processed": items_processed,
            }
        }
    )


def log_crawl_error(logger: logging.Logger, site_name: str, error: Exception, config: Dict[str, Any]):
    """Log crawl task error with context"""
    logger.error(
        f"Error in crawl task for {site_name}: {error}",
        exc_info=True,
        extra={
            "extra_fields": {
                "site_name": site_name,
                "error_type": type(error).__name__,
                "spider_type": config.get('spider', 'rss'),
            }
        }
    )


def log_spider_start(logger: logging.Logger, site_name: str, spider_name: str, feed_url: Optional[str] = None):
    """Log spider start with context"""
    logger.info(
        f"Starting crawl for spider: {spider_name}",
        extra={
            "extra_fields": {
                "site_name": site_name,
                "spider_name": spider_name,
                "feed_url": feed_url,
            }
        }
    )


def log_fetch_failed(logger: logging.Logger, site_name: str, url: str, request_type: str = "feed"):
    """Log failed fetch with context"""
    logger.warning(
        f"Failed to fetch: {url}",
        extra={
            "extra_fields": {
                "site_name": site_name,
                "url": url,
                "request_type": request_type,
            }
        }
    )


def log_parse_success(logger: logging.Logger, site_name: str, url: str, items_count: int, request_type: str = "feed"):
    """Log successful parse with context"""
    logger.debug(
        f"Parsed {items_count} items from {url}",
        extra={
            "extra_fields": {
                "site_name": site_name,
                "url": url,
                "items_count": items_count,
                "request_type": request_type,
            }
        }
    )


def log_parse_error(logger: logging.Logger, site_name: str, url: str, error: Exception, request_type: str = "feed"):
    """Log parse error with context"""
    logger.error(
        f"Error parsing response from {url}: {error}",
        exc_info=True,
        extra={
            "extra_fields": {
                "site_name": site_name,
                "url": url,
                "error_type": type(error).__name__,
                "request_type": request_type,
            }
        }
    )


def log_crawl_summary(logger: logging.Logger, site_name: str, total_items: int, success_count: int, failed_requests: List[str]):
    """Log crawl summary with context"""
    logger.info(
        f"Crawled {success_count}/{total_items} items successfully",
        extra={
            "extra_fields": {
                "site_name": site_name,
                "total_items": total_items,
                "success_count": success_count,
                "failed_count": total_items - success_count,
                "failed_requests": len(failed_requests),
            }
        }
    )


def log_no_items_processed(logger: logging.Logger, site_name: str, failed_requests: List[str]):
    """Log when no items were processed"""
    logger.warning(
        f"No items processed, all requests failed",
        extra={
            "extra_fields": {
                "site_name": site_name,
                "failed_requests": failed_requests,
            }
        }
    )


def log_item_stored(logger: logging.Logger, item: Item, content_uuid: str, db_id: int, body_size: int):
    """Log successful item storage with context"""
    logger.info(
        f"Stored item: {item.title[:50]}... (UUID: {content_uuid}, DB ID: {db_id})",
        extra={
            "extra_fields": {
                "url": item.url,
                "source": item.source,
                "content_uuid": content_uuid,
                "db_id": db_id,
                "title": item.title[:100] if item.title else None,
                "body_size": body_size,
            }
        }
    )


def log_item_exists(logger: logging.Logger, item: Item, existing_id: int):
    """Log when item already exists"""
    logger.debug(
        f"Content already exist: {item.url}",
        extra={
            "extra_fields": {
                "url": item.url,
                "source": item.source,
                "existing_id": existing_id,
            }
        }
    )


def log_item_error(logger: logging.Logger, item: Item, error: Exception):
    """Log item processing error with context"""
    logger.error(
        f"Error processing item {item.url}: {error}",
        exc_info=True,
        extra={
            "extra_fields": {
                "url": item.url,
                "source": item.source,
                "error_type": type(error).__name__,
                "title": item.title[:100] if item.title else None,
            }
        }
    )


def log_http_rate_limit(logger: logging.Logger, url: str, status_code: int, attempt: int, wait_time: int):
    """Log HTTP rate limit with context"""
    logger.warning(
        f"Rate limited, waiting {wait_time}s",
        extra={
            "extra_fields": {
                "url": url,
                "status_code": status_code,
                "attempt": attempt + 1,
                "wait_time": wait_time,
            }
        }
    )


def log_http_server_error(logger: logging.Logger, url: str, status_code: int, attempt: int, wait_time: int):
    """Log HTTP server error with context"""
    logger.warning(
        f"Server error, waiting {wait_time}s",
        extra={
            "extra_fields": {
                "url": url,
                "status_code": status_code,
                "attempt": attempt + 1,
                "wait_time": wait_time,
            }
        }
    )


def log_http_error(logger: logging.Logger, url: str, status_code: int, method: str, error: Exception):
    """Log HTTP error with context"""
    logger.error(
        f"HTTP error {status_code}: {error}",
        extra={
            "extra_fields": {
                "url": url,
                "status_code": status_code,
                "method": method,
                "error_type": type(error).__name__,
            }
        }
    )


def log_request_error(logger: logging.Logger, url: str, method: str, error: Exception, attempt: int):
    """Log request error with context"""
    logger.error(
        f"Request error: {error}",
        exc_info=True,
        extra={
            "extra_fields": {
                "url": url,
                "method": method,
                "error_type": type(error).__name__,
                "attempt": attempt + 1,
            }
        }
    )
