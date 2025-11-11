# scripts/trigger_crawlers.py
#!/usr/bin/env python3
"""
批量触发爬虫任务脚本（直接使用 Prefect）

使用方法:
    # 触发所有站点
    python scripts/trigger_crawlers.py

    # 触发指定站点
    python scripts/trigger_crawlers.py --sites bbc hackernews techcrunch

    # 并行触发（默认串行）
    python scripts/trigger_crawlers.py --parallel
"""
import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flows.crawler_deployments import trigger_manual_crawl
from configs import load_site_configs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def trigger_single_crawl(site_name: str) -> dict:
    """触发单个站点的爬虫任务"""
    try:
        flow_run_id = await trigger_manual_crawl(site_name)
        return {
            "success": True,
            "site": site_name,
            "flow_run_id": flow_run_id
        }
    except Exception as e:
        logger.error(f"Error triggering {site_name}: {e}")
        return {
            "success": False,
            "site": site_name,
            "error": str(e)
        }


async def batch_trigger_crawl(
    sites: Optional[List[str]] = None,
    parallel: bool = False
) -> dict:
    """批量触发爬虫任务"""
    # 获取所有站点配置
    all_sites = load_site_configs()
    
    # 确定要触发的站点
    if sites is None:
        sites = list(all_sites.keys())
    
    # 验证站点是否存在
    invalid_sites = [s for s in sites if s not in all_sites]
    if invalid_sites:
        raise ValueError(f"Invalid sites: {', '.join(invalid_sites)}")
    
    results = {}
    
    if parallel:
        # 并行触发
        tasks = [trigger_single_crawl(site) for site in sites]
        results_list = await asyncio.gather(*tasks)
        for result in results_list:
            results[result["site"]] = result
    else:
        # 串行触发
        for site in sites:
            result = await trigger_single_crawl(site)
            results[result["site"]] = result
    
    total = len(sites)
    success = sum(1 for r in results.values() if r["success"])
    failed = total - success
    
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "results": results
    }


async def main():
    parser = argparse.ArgumentParser(description="批量触发爬虫任务")
    parser.add_argument(
        "--sites",
        nargs="+",
        help="要触发的站点名称列表（例如: bbc hackernews techcrunch）"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="触发所有配置的站点"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="并行触发所有任务（默认串行）"
    )
    
    args = parser.parse_args()
    
    # 设置 Prefect API URL
    api_url = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")
    os.environ["PREFECT_API_URL"] = api_url
    
    # 确定要触发的站点
    if args.all:
        sites = None  # None 表示触发所有站点
        print("📋 将触发所有配置的站点")
    elif args.sites:
        sites = args.sites
        print(f"📋 将触发以下站点: {', '.join(sites)}")
    else:
        # 默认触发所有站点
        sites = None
        print("📋 未指定站点，将触发所有配置的站点")
        print("💡 提示: 使用 --sites 指定站点，或使用 --all 明确触发所有站点")
    
    # 显示执行模式
    mode = "并行" if args.parallel else "串行"
    print(f"⚙️  执行模式: {mode}")
    print(f"🌐 Prefect API: {api_url}\n")
    
    try:
        # 触发任务
        result = await batch_trigger_crawl(
            sites=sites,
            parallel=args.parallel
        )
        
        # 显示结果
        print("\n" + "="*60)
        print("📊 执行结果")
        print("="*60)
        print(f"总计: {result['total']} 个任务")
        print(f"✅ 成功: {result['success']} 个")
        print(f"❌ 失败: {result['failed']} 个")
        print("\n详细结果:")
        
        for site_name, site_result in result['results'].items():
            if site_result.get('success'):
                flow_run_id = site_result.get('flow_run_id', 'N/A')
                print(f"  ✅ {site_name}: 成功 (Flow Run ID: {flow_run_id})")
            else:
                error = site_result.get('error', 'Unknown error')
                print(f"  ❌ {site_name}: 失败 - {error}")
        
        print("\n" + "="*60)
        print("💡 提示: 在 Prefect WebUI (http://localhost:4200) 查看任务执行状态")
        print("="*60)
        
        # 返回适当的退出码
        sys.exit(0 if result['failed'] == 0 else 1)
        
    except Exception as e:
        logger.error(f"执行失败: {e}")
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())