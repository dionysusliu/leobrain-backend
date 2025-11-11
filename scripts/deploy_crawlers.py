# scripts/register_crawler_deployments.py
#!/usr/bin/env python3
"""
根据 sites.yaml 配置文件注册所有爬虫任务到 Prefect

使用方法:
    python scripts/register_crawler_deployments.py

环境变量:
    PREFECT_API_URL: Prefect API URL (默认: http://localhost:4200/api)
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 在导入 Prefect 相关模块之前设置环境变量
api_url = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")
os.environ["PREFECT_API_URL"] = api_url

from flows.crawler_deployments import deploy_crawler_flows
from configs import load_site_configs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)
logging.getLogger('prefect').setLevel(logging.INFO)


def check_prefect_server(api_url: str = "http://localhost:4200/api") -> bool:
    """检查 Prefect 服务器是否可用"""
    import urllib.request
    try:
        health_url = api_url.replace('/api', '/api/health')
        urllib.request.urlopen(health_url, timeout=5)
        return True
    except Exception as e:
        logger.debug(f"Prefect server check failed: {e}")
        return False


async def main():
    """主函数"""
    api_url = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")
    os.environ["PREFECT_API_URL"] = api_url
    
    # 检查 Prefect 服务器
    logger.info(f"检查 Prefect 服务器: {api_url}")
    if not check_prefect_server(api_url):
        logger.error(f"无法连接到 Prefect 服务器: {api_url}")
        logger.error("请确保 Prefect 服务器正在运行: docker compose up -d prefect-server")
        sys.exit(1)
    
    logger.info("Prefect 服务器连接成功")
    
    # 检查配置
    site_configs = load_site_configs()
    if not site_configs:
        logger.error("没有找到站点配置，请检查 configs/sites.yaml")
        sys.exit(1)
    
    logger.info(f"找到 {len(site_configs)} 个站点配置")
    
    # 部署所有配置
    try:
        result = await deploy_crawler_flows(ensure_work_pools_first=True)
        
        if result["errors"] > 0:
            logger.warning(f"部署完成，但有 {result['errors']} 个错误")
            for error in result["error_details"]:
                logger.error(f"  - {error}")
            sys.exit(1)
        else:
            logger.info(f"✅ 成功部署 {result['deployed']} 个部署配置")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"部署过程中出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())