import re
import yaml
from datetime import datetime

def parse_news_line(line):
    """解析单条新闻行"""
    # 提取tag（如果有）
    tag_match = re.match(r'^- \*\*\[([^\]]+)\]\*\*', line)
    tag = tag_match.group(1) if tag_match else None
    
    # 提取日期（格式：YYYY.M或YYYY.M.D）
    date_match = re.search(r'(\d{4}\.\d{1,2}(?:\.\d{1,2})?),', line)
    date_str = date_match.group(1) if date_match else None
    
    # 转换日期格式为YYYY-MM-DD
    date = None
    if date_str:
        try:
            if len(date_str.split('.')) == 2:
                date = datetime.strptime(date_str, '%Y.%m').strftime('%Y-%m-%d')
            else:
                date = datetime.strptime(date_str, '%Y.%m.%d').strftime('%Y-%m-%d')
        except:
            date = None
    
    # 提取标题（排除tag和date部分）
    title_start = date_match.end() if date_match else (tag_match.end() if tag_match else 2)
    title_part = line[title_start:].strip()
    
    # 提取链接（如果有）
    links = []
    title = title_part
    link_matches = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', title_part)
    for match in link_matches:
        links.append({
            'name': match.group(1),
            'url': match.group(2)
        })
        # 从标题中移除链接标记
        title = title.replace(match.group(0), '').strip()
    
    # 构建新闻条目
    news_item = {'title': title}
    if tag:
        news_item['tag'] = tag
    if date:
        news_item['date'] = date
    if links:
        news_item['links'] = links
    
    return news_item

def convert_md_to_yaml(input_file, output_file, start_line=24):
    """转换Markdown文件到YAML"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    news_items = []
    for line in lines[start_line-1:]:  # 转换为0-based索引
        line = line.strip()
        if line.startswith('- **[') or line.startswith('- [') or line.startswith('['):
            news_item = parse_news_line(line)
            if news_item:
                news_items.append(news_item)
    
    # 写入YAML文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(news_items, f, allow_unicode=True, sort_keys=False, width=1000)
    
    print(f"成功转换 {len(news_items)} 条新闻到 {output_file}")

if __name__ == "__main__":
    input_md = "index.md"  # 输入的Markdown文件
    output_yaml = "news_manual_update.yml"  # 输出的YAML文件
    convert_md_to_yaml(input_md, output_yaml)