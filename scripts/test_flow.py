# scripts/test_flow.py
"""测试 Flow 能否正常调用"""
import asyncio
import sys
from pathlib import Path

# 添加 backend 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from flows.crawler_flows import pf_flow_crawl_site_by_name
from configs import load_site_configs
from unittest.mock import patch, AsyncMock
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_flow_call():
    """测试 flow 能否正常调用"""
    site_configs = load_site_configs()
    
    if not site_configs:
        print("❌ No site configurations found")
        return False
    
    site_name = list(site_configs.keys())[0]
    site_config = site_configs[site_name]
    
    print(f"Testing flow with site: {site_name}")
    print(f"  Feed URL: {site_config.feed_url}")
    print(f"  Cron: {site_config.cron}")
    
    # Mock 业务逻辑层
    # 注意：需要 mock flows.crawler_tasks.crawl_site，因为 task 中导入的是这个引用
    # 或者 mock workers.crawler_task.crawl_site（原始定义）
    # 这里使用 task 模块中的引用路径
    with patch('flows.crawler_tasks.crawl_site', new_callable=AsyncMock) as mock_crawl_site:
        mock_crawl_site.return_value = None
        
        try:
            # 调用 flow
            result = await pf_flow_crawl_site_by_name(site_name, site_config)
            
            print(f"✅ Flow executed successfully")
            print(f"   Result: {result}")
            
            # 验证 mock 被调用
            assert mock_crawl_site.called, "crawl_site should be called"
            call_args = mock_crawl_site.call_args
            print(f"   Called with site_name: {call_args[0][0]}")
            print(f"   Called with config type: {type(call_args[0][1])}")
            print(f"   Config is dict: {isinstance(call_args[0][1], dict)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Flow execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_flow_parameter_types():
    """测试 flow 参数类型是否正确"""
    from configs.types import SiteConfig
    
    site_configs = load_site_configs()
    
    if not site_configs:
        print("❌ No site configurations found")
        return False
    
    site_name = list(site_configs.keys())[0]
    site_config = site_configs[site_name]
    
    # 验证类型
    assert isinstance(site_config, SiteConfig), f"Expected SiteConfig, got {type(site_config)}"
    assert isinstance(site_name, str), f"Expected str, got {type(site_name)}"
    
    print(f"✅ Parameter types are correct")
    print(f"   site_name: {type(site_name).__name__}")
    print(f"   config: {type(site_config).__name__}")
    
    return True


async def test_flow_without_prefect_server():
    """测试 flow 在本地模式下的调用（不连接 Prefect Server）"""
    import os
    
    # 设置 Prefect 为本地模式（不连接 Server）
    # 这会让 Prefect 在本地执行，不尝试连接 API
    os.environ["PREFECT_API_URL"] = ""
    
    site_configs = load_site_configs()
    
    if not site_configs:
        print("❌ No site configurations found")
        return False
    
    site_name = list(site_configs.keys())[0]
    site_config = site_configs[site_name]
    
    print(f"Testing flow in local mode (no Prefect Server)")
    print(f"  Site: {site_name}")
    
    # Mock 业务逻辑层
    with patch('flows.crawler_tasks.crawl_site', new_callable=AsyncMock) as mock_crawl_site:
        mock_crawl_site.return_value = None
        
        try:
            result = await pf_flow_crawl_site_by_name(site_name, site_config)
            print(f"✅ Flow executed in local mode")
            print(f"   Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Flow execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """主测试函数"""
    print("=" * 60)
    print("Testing Flow Call")
    print("=" * 60)
    
    # 测试 1: 参数类型
    print("\n[Test 1] Parameter Types")
    print("-" * 60)
    type_test = await test_flow_parameter_types()
    
    # 测试 2: Flow 调用（使用 mock）
    print("\n[Test 2] Flow Execution (with Mock)")
    print("-" * 60)
    flow_test = await test_flow_call()
    
    # 总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Parameter Types: {'✅ PASS' if type_test else '❌ FAIL'}")
    print(f"  Flow Execution:  {'✅ PASS' if flow_test else '❌ FAIL'}")
    
    if type_test and flow_test:
        print("\n✅ All tests passed!")
        print("\nNote: Flow execution test uses mocks to avoid external dependencies.")
        print("      To test with real dependencies, ensure MinIO and database are running.")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)