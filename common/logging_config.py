"""Structured logging configuration for JSON output to file"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path
import os
from prefect.context import get_run_context

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add Prefect context if available
        try:
            from prefect.context import get_run_context
            run_context = get_run_context()
            if run_context:
                if hasattr(run_context, 'flow_run') and run_context.flow_run:
                    log_data["flow_run_id"] = str(run_context.flow_run.id)
                    log_data["flow_run_name"] = run_context.flow_run.name
                if hasattr(run_context, 'task_run') and run_context.task_run:
                    log_data["task_run_id"] = str(run_context.task_run.id)
                    log_data["task_run_name"] = run_context.task_run.name
        except Exception:
            pass

        return json.dumps(log_data)

def is_container_env() -> bool:
    """检测是否在容器环境中运行"""
    # 检查常见的容器环境标识
    return (
        os.path.exists("/.dockerenv") or
        os.getenv("CONTAINER_ENV") == "true" or
        os.getenv("PREFECT_API_URL") is not None  # Prefect 通常在容器中运行
    )

def setup_logging(level: str = "INFO", log_dir: Optional[str] = None, force_stdout: Optional[bool] = None):
    """
    Setup structured JSON logging
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files (default: /var/log/leobrain or from LOG_DIR env)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    formatter = JSONFormatter()

    in_container = force_stdout if force_stdout is not None else is_container_env() 

    if in_container:
        # 容器环境：所有日志输出到 stdout（JSON 格式），Promtail 会自动收集
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(getattr(logging, level.upper()))
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)
        
        # 也输出到 stderr（某些情况下需要）
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(formatter)
        root_logger.addHandler(stderr_handler)
        
        logging.info("Logging configured for container: level=%s, output=stdout (JSON)", level)
    else:
        # 非容器环境：同时输出到文件和 stdout
        # Determine log directory
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            default_log_dir = project_root / "logs" if (project_root / "backend").exists() or (project_root / "backend").name == "backend" else "/var/log/leobrain"
            log_dir = os.getenv("LOG_DIR", str(default_log_dir))
        log_path = Path(log_dir)
        try:
            log_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            log_path = Path("./logs")
            log_path.mkdir(parents=True, exist_ok=True)
            log_dir = str(log_path)
        
        # File handler for Promtail collection
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_path / "leobrain-api.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Also output to stdout (all levels in dev)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(getattr(logging, level.upper()))
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)
        
        logging.info("Logging configured: level=%s, log_dir=%s", level, log_path)


    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    # prefect logging
    prefect_logger = logging.getLogger("prefect")
    prefect_logger.setLevel(getattr(logging, level.upper()))