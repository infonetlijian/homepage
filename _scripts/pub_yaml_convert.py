import re
import yaml

def parse_publications(md_content):
    publications = []
    lines = md_content.split('\n')
    i = 65  # 从第65行开始读取
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # 解析论文缩写和标题
        abbrev_match = re.search(r'<font color=red>\[\*\*(.*?)\*\*\]</font>', line)
        if abbrev_match:
            # 提取缩写，去除<font color=red>**[和]**</font>
            abbrev = abbrev_match.group(1)
            title = line[abbrev_match.end():].strip()
        else:
            # 没有缩写的情况，直接读取标题
            abbrev = None
            title = line.strip()
        
        # 获取作者行
        i += 1
        if i >= len(lines):
            break
        authors_line = lines[i].strip()
        
        # 处理作者信息 - 去除加粗标记并处理星号
        authors = []
        if authors_line:  # 只有非空行才处理
            for author in re.split(r',|\band\b', authors_line):
                author = author.strip()
                if not author:
                    continue
                # 处理**Jian Li**和**Jian Li\***的情况
                if '**Jian Li' in author:
                    if r'\*' in author:
                        author = 'Jian Li*'
                    else:
                        author = 'Jian Li'
                authors.append(author)
        
        # 获取出版社信息行
        i += 1
        if i >= len(lines):
            break
        publisher_line = lines[i].strip()
        
        # 提取出版社和年份
        publisher = None
        year = None
        if publisher_line:  # 只有非空行才处理
            publisher_parts = [p.strip() for p in publisher_line.split(',')]
            publisher = publisher_parts[0]
            for part in reversed(publisher_parts):
                year_match = re.search(r'(\d{4})', part)
                if year_match:
                    year = int(year_match.group(1))
                    break
        
        # 获取链接行
        i += 1
        if i >= len(lines):
            break
        links_line = lines[i].strip()
        links = []
        # 查找代码链接
        if links_line:  # 只有非空行才处理
            code_links = re.findall(r'\[Code\]\((.*?)\)', links_line)
            for url in code_links:
                links.append({'name': 'Code', 'url': url})
        
        # 如果缺少必要字段则跳过
        if not authors or not publisher or not year:
            i += 1
            continue
        
        # 生成ID (第一作者的姓 + 年份 + 标题第一个关键词)
        first_author = authors[0]
        first_author_parts = first_author.split()
        first_author_last_name = first_author_parts[-1].replace('*', '') if first_author_parts else 'unknown'
        
        # 从标题获取第一个关键词(跳过常见词)
        words = re.findall(r'\b\w+\b', title.lower())
        first_keyword = next((word for word in words if word not in ['a', 'an', 'the', 'towards']), 'paper')
        
        paper_id = f"{first_author_last_name.lower()}{year}{first_keyword.lower()}"
        
        # 创建论文条目
        publication = {
            'id': paper_id,
            'title': title,
            'date': f"{year}-01-01",  # 默认日期，因为原文未提供
            'type': 'journal' if 'Transactions' in publisher or 'Journal' in publisher or 'Physical Review' in publisher else 'conference',
            'publisher': publisher,
            'abbr': abbrev,  # 缩写(可能为None)
            'year': year,
            'authors': authors,
            'selected': False,  # 默认为False
            'tags': [],  # 默认为空
            'links': links
        }
        
        publications.append(publication)
        i += 1
    
    return publications

# 读取markdown文件
with open('publications.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# 解析论文信息
publications = parse_publications(md_content)

# 写入YAML文件
with open('publications_db.yml', 'w', encoding='utf-8') as f:
    yaml.dump(publications, f, allow_unicode=True, sort_keys=False)

print(f"成功转换 {len(publications)} 篇论文到YAML格式。")