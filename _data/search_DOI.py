import yaml
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import scholarly
from habanero import Crossref
import re

# 配置参数
YAML_FILE = 'publications_manual_update.yml'
DELAY = 2  # 请求之间的延迟(秒)，避免被封锁
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def save_yaml(file_path, data):
    """保存YAML文件"""
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, sort_keys=False)

def search_google_scholar(title):
    """通过Google Scholar搜索DOI"""
    try:
        search_query = scholarly.search_pubs(title)
        pub = next(search_query)
        if hasattr(pub, 'bib') and 'doi' in pub.bib:
            return pub.bib['doi']
    except Exception as e:
        print(f"Google Scholar搜索出错: {e}")
    return None

def search_ieee_xplore(title):
    """通过IEEE Xplore搜索DOI"""
    try:
        base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp"
        params = {
            "newsearch": "true",
            "queryText": f'"{title}"'
        }
        headers = {'User-Agent': USER_AGENT}
        
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find('div', {'class': 'List-results-items'})
        if result:
            doi_link = result.find('a', {'href': re.compile(r'doi.org')})
            if doi_link:
                return doi_link['href'].split('doi.org/')[-1]
    except Exception as e:
        print(f"IEEE Xplore搜索出错: {e}")
    return None

def search_crossref(title):
    """通过Crossref API搜索DOI"""
    try:
        cr = Crossref()
        result = cr.works(query=title, limit=1)
        if result['message']['items']:
            return result['message']['items'][0]['DOI']
    except Exception as e:
        print(f"Crossref搜索出错: {e}")
    return None

def extract_doi_from_text(text):
    """从文本中提取DOI"""
    doi_pattern = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)
    match = doi_pattern.search(text)
    return match.group(0) if match else None

def find_doi(title):
    """尝试多种方法获取DOI"""
    # 1. 先尝试Crossref API
    doi = search_crossref(title)
    if doi:
        return doi
    
    # 2. 尝试Google Scholar
    doi = search_google_scholar(title)
    if doi:
        return extract_doi_from_text(doi) if isinstance(doi, str) else None
    
    # 3. 最后尝试IEEE Xplore
    doi = search_ieee_xplore(title)
    if doi:
        return doi
    
    return None

def update_dois(publications):
    """更新所有论文的DOI信息"""
    updated_count = 0
    
    for pub in publications:
        # 检查是否已有DOI
        has_doi = any(link['name'] == 'DOI' and link['url'] for link in pub.get('links', []))
        
        if not has_doi:
            title = pub['title']
            print(f"\n正在搜索: {title}")
            
            doi = find_doi(title)
            
            if doi:
                print(f"找到DOI: {doi}")
                # 标准化DOI URL
                doi_url = f"https://doi.org/{doi}"
                
                # 更新或添加DOI链接
                doi_link = next((link for link in pub.get('links', []) if link['name'] == 'DOI'), None)
                if doi_link:
                    doi_link['url'] = doi_url
                else:
                    pub.setdefault('links', []).append({'name': 'DOI', 'url': doi_url})
                
                updated_count += 1
            else:
                print("未找到DOI")
            
            time.sleep(DELAY)  # 避免请求过于频繁
    
    print(f"\n完成! 共更新了 {updated_count} 篇论文的DOI信息")
    return publications

if __name__ == "__main__":
    # 加载YAML文件
    publications = load_yaml(YAML_FILE)
    
    # 更新DOI信息
    updated_publications = update_dois(publications)
    
    # 保存更新后的YAML文件
    save_yaml(YAML_FILE, updated_publications)