#!/usr/bin/env python3
"""
Google Scholar Crawler using the scholarly library
Fetches author profile and publication citation data
"""

from scholarly import scholarly, ProxyGenerator
import json
from datetime import datetime
import os
import time

max_attempts = 100
wait_seconds = 600  # 10分钟

for attempt in range(1, max_attempts + 1):
    try:
        print(f"Attempt {attempt}: Fetching Google Scholar data...")
        
        # 设置代理以防止被限制
        pg = ProxyGenerator()
        pg.FreeProxies()  # 使用免费旋转代理
        scholarly.use_proxy(pg)
        
        # 获取作者信息
        author = scholarly.search_author_id(os.environ['GOOGLE_SCHOLAR_ID'])
        scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
        
        print(f"✓ 第 {attempt} 次尝试成功")
        break
        
    except Exception as e:
        print(f"✗ 第 {attempt} 次尝试失败: {e}")
        if attempt < max_attempts:
            print(f"  等待 {wait_seconds} 秒后重试...")
            time.sleep(wait_seconds)
        else:
            print("❌ 所有100次尝试均失败")
            exit(1)

# 处理作者数据
name = author['name']
author['updated'] = str(datetime.now())
author['publications'] = {v['author_pub_id']: v for v in author['publications']}

print("\n📊 获取的数据:")
print(f"  姓名: {name}")
print(f"  被引用次数: {author['citedby']}")
print(f"  论文数: {len(author['publications'])}")

# 创建输出目录
os.makedirs('results', exist_ok=True)

# 保存完整的Google Scholar数据
with open('results/gs_data.json', 'w', encoding='utf-8') as outfile:
    json.dump(author, outfile, ensure_ascii=False, indent=2)
print("\n✓ 已保存: results/gs_data.json")

# 为shields.io badge创建数据文件（用于展示在README或主页）
shieldio_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": f"{author['citedby']}",
}
with open('results/gs_data_shieldsio.json', 'w', encoding='utf-8') as outfile:
    json.dump(shieldio_data, outfile, ensure_ascii=False)
print("✓ 已保存: results/gs_data_shieldsio.json (用于badge展示)")

print("\n✅ Google Scholar爬虫执行完成!")
