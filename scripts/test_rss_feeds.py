#!/usr/bin/env python3
"""
RSS Feed 测试脚本
用于验证 RSS feed 是否有效，并显示基本信息
"""
import sys
from pathlib import Path
import feedparser
from datetime import datetime
from typing import Dict, List, Tuple
import time

# 添加 backend 目录到路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# RSS Feed 配置
RSS_FEEDS = {
    # 新闻类
    "theguardian": {
        "url": "https://www.theguardian.com/world/rss",
        "category": "新闻",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    "npr": {
        "url": "https://feeds.npr.org/1001/rss.xml",
        "category": "新闻",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    "cnbc": {
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "category": "新闻",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    "wsj_cn": {
        "url": "https://cn.wsj.com/zh-hans/rss",
        "category": "新闻",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    
    # 财经类
    "yahoo_finance_news": {
        "url": "https://finance.yahoo.com/news/rssindex",
        "category": "财经",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    "yahoo_finance_top": {
        "url": "https://finance.yahoo.com/rss/topstories",
        "category": "财经",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    "yahoo_news_finance": {
        "url": "https://news.yahoo.com/rss/finance",
        "category": "财经",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    "financial_times": {
        "url": "https://www.ft.com/rss/home/uk",
        "category": "财经",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    "dowjones": {
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "category": "财经",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    "thomsonreuters": {
        "url": "https://ir.thomsonreuters.com/rss/news-releases.xml?items=15",
        "category": "财经",
        "interval": "1day",
        "cron": "0 0 * * *"
    },
    "xueqiu": {
        "url": "https://xueqiu.com/hots/topic/rss",
        "category": "财经",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
    
    # 科技类
    "techcrunch": {
        "url": "https://techcrunch.com/feed/",
        "category": "科技",
        "interval": "6hrs",
        "cron": "0 */6 * * *"
    },
    "36kr": {
        "url": "https://www.36kr.com/feed",
        "category": "科技",
        "interval": "2hr",
        "cron": "0 */2 * * *"
    },
    "huxiu": {
        "url": "https://www.huxiu.com/rss/0.xml",
        "category": "科技",
        "interval": "1hr",
        "cron": "0 * * * *"
    },
}


def test_feed(name: str, config: Dict) -> Tuple[bool, Dict]:
    """
    测试单个 RSS feed
    
    Returns:
        (is_valid, info_dict)
    """
    url = config["url"]
    print(f"\n{'='*60}")
    print(f"测试: {name} ({config['category']})")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        # 解析 feed
        feed = feedparser.parse(url)
        
        # 检查是否有效
        is_valid = feed.bozo == 0
        
        # 收集信息
        info = {
            "valid": is_valid,
            "title": feed.feed.get("title", "N/A"),
            "link": feed.feed.get("link", "N/A"),
            "description": feed.feed.get("description", "N/A")[:100],
            "item_count": len(feed.entries),
            "last_updated": feed.feed.get("updated", "N/A"),
            "bozo_exception": str(feed.bozo_exception) if feed.bozo_exception else None,
        }
        
        # 显示结果
        if is_valid:
            print(f"✅ 有效")
            print(f"   标题: {info['title']}")
            print(f"   链接: {info['link']}")
            print(f"   条目数: {info['item_count']}")
            if info['last_updated'] != "N/A":
                print(f"   最后更新: {info['last_updated']}")
            
            # 显示前3个条目
            if feed.entries:
                print(f"\n   最新条目:")
                for i, entry in enumerate(feed.entries[:3], 1):
                    title = entry.get("title", "N/A")[:60]
                    published = entry.get("published", entry.get("updated", "N/A"))
                    print(f"   {i}. {title}")
                    print(f"      发布时间: {published}")
        else:
            print(f"❌ 无效")
            if info['bozo_exception']:
                print(f"   错误: {info['bozo_exception']}")
        
        return is_valid, info
        
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False, {"valid": False, "error": str(e)}


def test_all_feeds():
    """测试所有 RSS feeds"""
    print("="*60)
    print("RSS Feed 测试脚本")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    valid_count = 0
    invalid_count = 0
    
    # 按分类测试
    categories = {}
    for name, config in RSS_FEEDS.items():
        category = config["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append((name, config))
    
    # 测试每个分类
    for category, feeds in categories.items():
        print(f"\n\n{'#'*60}")
        print(f"# {category}类 ({len(feeds)} 个)")
        print(f"{'#'*60}")
        
        for name, config in feeds:
            is_valid, info = test_feed(name, config)
            results[name] = {
                "config": config,
                "info": info,
                "valid": is_valid
            }
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
            
            # 避免请求过快
            time.sleep(1)
    
    # 汇总报告
    print(f"\n\n{'='*60}")
    print("测试汇总")
    print(f"{'='*60}")
    print(f"总计: {len(RSS_FEEDS)} 个 feed")
    print(f"✅ 有效: {valid_count} 个")
    print(f"❌ 无效: {invalid_count} 个")
    print(f"成功率: {valid_count/len(RSS_FEEDS)*100:.1f}%")
    
    # 无效的 feed
    if invalid_count > 0:
        print(f"\n无效的 Feed:")
        for name, result in results.items():
            if not result["valid"]:
                print(f"  - {name}: {result['config']['url']}")
                if result['info'].get('error'):
                    print(f"    错误: {result['info']['error']}")
    
    return results


def generate_yaml_config(results: Dict):
    """根据测试结果生成 YAML 配置"""
    print(f"\n\n{'='*60}")
    print("生成的 YAML 配置")
    print(f"{'='*60}")
    
    yaml_lines = [
        "# Site configurations for crawlers",
        "# Generated from RSS feed test results",
        "",
    ]
    
    # 按分类组织
    categories = {}
    for name, result in results.items():
        if result["valid"]:
            category = result["config"]["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((name, result))
    
    for category in ["新闻", "财经", "科技"]:
        if category not in categories:
            continue
        
        yaml_lines.append(f"# ==================== {category}类 ====================")
        yaml_lines.append("")
        
        for name, result in categories[category]:
            config = result["config"]
            yaml_lines.append(f"{name}:")
            yaml_lines.append(f"  spider: rss")
            yaml_lines.append(f"  source_name: {name}")
            yaml_lines.append(f'  feed_url: "{config["url"]}"')
            yaml_lines.append(f'  cron: "{config["cron"]}"  # {config["interval"]}')
            yaml_lines.append(f"  qps: 1.0")
            yaml_lines.append(f"  concurrency: 2")
            yaml_lines.append(f"  max_items: 50")
            yaml_lines.append(f"  fetch_full_content: false")
            yaml_lines.append(f"  headers:")
            yaml_lines.append(f'    User-Agent: "LeoBrain/1.0"')
            yaml_lines.append(f"  use_render: false")
            yaml_lines.append("")
    
    yaml_content = "\n".join(yaml_lines)
    print(yaml_content)
    
    # 保存到文件
    output_file = Path(__file__).parent.parent / "crawlers" / "configs" / "sites_generated.yaml"
    output_file.write_text(yaml_content, encoding="utf-8")
    print(f"\n✅ 配置已保存到: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试 RSS Feeds")
    parser.add_argument("--generate", action="store_true", help="生成 YAML 配置文件")
    parser.add_argument("--feed", type=str, help="只测试指定的 feed 名称")
    
    args = parser.parse_args()
    
    if args.feed:
        # 只测试指定的 feed
        if args.feed in RSS_FEEDS:
            test_feed(args.feed, RSS_FEEDS[args.feed])
        else:
            print(f"错误: 找不到 feed '{args.feed}'")
            print(f"可用的 feeds: {', '.join(RSS_FEEDS.keys())}")
    else:
        # 测试所有 feeds
        results = test_all_feeds()
        
        if args.generate:
            generate_yaml_config(results)