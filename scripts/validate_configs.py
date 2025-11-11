"""验证配置文件是否符合类型定义"""
import sys
from pathlib import Path

# 添加 backend 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from configs import load_site_configs, load_work_pool_configs

def main():
    print("Validating configurations...")
    
    # 验证站点配置
    try:
        site_configs = load_site_configs()
        print(f"✅ Site configs: {len(site_configs)} sites loaded")
        for site_name in site_configs.keys():
            print(f"   - {site_name}")
    except Exception as e:
        print(f"❌ Site configs validation failed: {e}")
        sys.exit(1)
    
    # 验证 Work Pool 配置
    try:
        pool_configs = load_work_pool_configs()
        print(f"✅ Work pool configs: {len(pool_configs)} pools loaded")
        for pool_name in pool_configs.keys():
            print(f"   - {pool_name}")
    except Exception as e:
        print(f"❌ Work pool configs validation failed: {e}")
        sys.exit(1)
    
    print("\n✅ All configurations are valid!")

if __name__ == "__main__":
    main()