#!/usr/bin/env python3
"""
Google Scholar全功能爬虫脚本
功能：
1. 自动抓取指定学者的所有论文
2. 提取每篇论文的完整元数据
3. 生成符合学术主页要求的YAML文件
"""

import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException,
                                      TimeoutException,
                                      StaleElementReferenceException)
import time
import argparse
from bs4 import BeautifulSoup
import textwrap
import random
from urllib.parse import urljoin
import re

# 配置参数
WAIT_TIMEOUT = 20  # 元素等待超时(秒)
DELAY_RANGE = (5, 10)  # 随机延迟范围(秒)
MAX_RETRIES = 3  # 最大重试次数
MAX_PAPERS = 200  # 默认最大处理论文数

def init_driver(headless=True):
    """初始化浏览器驱动"""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

def random_delay():
    """随机延迟防止被封"""
    time.sleep(random.uniform(*DELAY_RANGE))

def scrape_scholar_profile(driver, profile_id):
    """抓取用户论文列表"""
    base_url = "https://scholar.google.com"
    profile_url = f"{base_url}/citations?user={profile_id}&hl=zh-CN"
    
    print(f"\n正在访问学者主页: {profile_url}")
    driver.get(profile_url)
    random_delay()
    
    try:
        # 等待论文列表加载
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "gsc_a_b"))
        )
        
        # 获取学者姓名
        try:
            scholar_name = driver.find_element(By.ID, "gsc_prf_in").text
            print(f"学者姓名: {scholar_name}")
        except:
            scholar_name = ""
        
        # 滚动加载所有论文
        print("正在加载全部论文列表...")
        while True:
            try:
                more_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "gsc_bpf_more")))
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(3)  # 固定延迟确保加载完成
            except (TimeoutException, NoSuchElementException):
                break
        
        # 解析论文条目
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        papers = []
        
        for item in soup.select('#gsc_a_b .gsc_a_tr'):
            title_elem = item.select_one('.gsc_a_at')
            if title_elem:
                papers.append({
                    'title': title_elem.text.strip(),
                    'url': urljoin(base_url, title_elem['href']),
                    'year': item.select_one('.gsc_a_y').text.strip() if item.select_one('.gsc_a_y') else ""
                })
        
        print(f"共发现 {len(papers)} 篇论文")
        return papers
        
    except Exception as e:
        print(f"抓取论文列表失败: {str(e)}")
        return []

def extract_paper_details(driver, paper_url, retry_count=0):
    """提取论文详细信息"""
    try:
        driver.get(paper_url)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, 'gsc_oci_title')))
        random_delay()
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 提取标题
        title = soup.find('div', id='gsc_oci_title').text.strip()
        
        # 提取作者
        authors = []
        authors_div = soup.find('div', class_='gsc_oci_value', string='Authors')
        if authors_div:
            authors = [a.text.strip() for a in authors_div.find_next_sibling('div').find_all('a')]
        
        # 提取出版信息
        details = {}
        for row in soup.select('.gsc_oci_table .gs_scl'):
            field = row.find('div', class_='gsc_oci_field').text.strip().lower()
            value_div = row.find('div', class_='gsc_oci_value')
            value = value_div.text.strip() if value_div else ""
            details[field] = value
        
        # 结构化数据 - 特别注意这里的括号匹配
        doi = (details.get('doi', '') or 
              next((link['href'].split('doi.org/')[-1] 
                   for link in soup.select('a[href*="doi.org"]') 
                   if 'href' in link.attrs), ""))
        
        return {
            'title': title,
            'authors': authors,
            'year': details.get('year', '').split()[0] if details.get('year') else "",
            'journal': details.get('journal', details.get('conference', '')),
            'volume': re.sub(r'[^\d]', '', details.get('volume', '')) or "",
            'issue': re.sub(r'[^\d]', '', details.get('issue', '')) or "",
            'pages': details.get('pages', '').replace('–', '-'),
            'doi': doi[0] if isinstance(doi, tuple) else doi,
            'citations': details.get('cited by', '').split()[0] if details.get('cited by') else "0"
        }
        
    except (TimeoutException, StaleElementReferenceException) as e:
        if retry_count < MAX_RETRIES:
            print(f"尝试 {retry_count+1}/{MAX_RETRIES} 失败，重试中...")
            return extract_paper_details(driver, paper_url, retry_count+1)
        print(f"论文详情解析失败: {str(e)}")
        return None
    except Exception as e:
        print(f"意外错误: {str(e)}")
        return None

def save_to_yml(papers, output_file):
    """保存为YAML格式"""
    valid_papers = []
    
    for paper in papers:
        if not paper or not paper.get('title'):
            continue
            
        # 构建标准条目
        entry = {
            'id': re.sub(r'[^\w]', '_', paper['title'][:30].lower()),
            'title': paper['title'],
            'date': f"{paper.get('year', '2023')}-01-01",
            'type': 'journal' if 'journal' in paper.get('journal', '').lower() else 'conference',
            'publisher': paper.get('journal', ''),
            'year': paper.get('year', ''),
            'volume': paper.get('volume', ''),
            'number': paper.get('issue', ''),
            'pages': paper.get('pages', ''),
            'authors': paper.get('authors', []),
            'selected': False,
            'tags': [],
            'links': [
                {'name': 'Scholar', 'url': paper['url']}
            ]
        }
        
        # 添加DOI链接
        if paper.get('doi'):
            entry['links'].insert(0, {
                'name': 'DOI',
                'url': f"https://doi.org/{paper['doi']}"
            })
            
        # 清理空值字段
        valid_papers.append({k: v for k, v in entry.items() if v not in (None, "", [])})
    
    # 按年份倒序排序
    valid_papers.sort(key=lambda x: x.get('year', '0'), reverse=True)
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(valid_papers, f, allow_unicode=True, sort_keys=False, width=1000)
    
    print(f"\n成功保存 {len(valid_papers)} 篇论文到 {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--profile-id', required=True, help='Google Scholar用户ID，如 ZuP2MtEAAAAJ')
    parser.add_argument('--output', default='publications.yml', help='输出YAML文件路径')
    parser.add_argument('--max-papers', type=int, default=MAX_PAPERS, 
                       help=f'最大处理论文数 (默认: {MAX_PAPERS})')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    parser.add_argument('--delay', type=float, default=0, 
                       help='固定延迟秒数 (覆盖随机延迟)')
    args = parser.parse_args()

    # 初始化浏览器
    driver = None
    try:
        driver = init_driver(args.headless)
        
        # 获取论文列表
        papers = scrape_scholar_profile(driver, args.profile_id)
        if not papers:
            print("未找到论文信息，请检查用户ID或网络连接")
            return
        
        # 处理每篇论文
        detailed_papers = []
        for i, paper in enumerate(papers[:args.max_papers]):
            print(f"\n[{i+1}/{min(len(papers), args.max_papers)}] 处理: {paper['title'][:50]}...")
            
            # 应用延迟
            if args.delay > 0:
                time.sleep(args.delay)
            else:
                random_delay()
            
            # 获取详情
            details = extract_paper_details(driver, paper['url'])
            if details:
                detailed_papers.append({**paper, **details})
                print(f"  已提取: {details.get('journal', '')} {details.get('year', '')}")
            else:
                print("  跳过无法解析的论文")
        
        # 保存结果
        if detailed_papers:
            save_to_yml(detailed_papers, args.output)
        else:
            print("未成功提取任何论文详情")
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()