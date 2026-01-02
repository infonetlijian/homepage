import yaml
import re

def process_publications(yaml_file):
    # 读取YAML文件
    with open(yaml_file, 'r', encoding='utf-8') as f:
        publications = yaml.safe_load(f)
    
    for pub in publications:
        # 处理期刊论文的卷期页码信息
        if pub['type'] == 'journal':
            # 从publisher信息中提取卷期页码
            publisher_info = pub.get('publisher', '')
            
            # 尝试从publisher信息中提取卷号、期号和页码
            volume_match = re.search(r'Volume:\s*(\d+)', publisher_info)
            number_match = re.search(r'Issue:\s*(\d+)', publisher_info)
            pages_match = re.search(r'Pages?:\s*([\d\-]+)', publisher_info)
            
            # 如果找到匹配项且字段不存在，则添加
            if volume_match and 'volume' not in pub:
                pub['volume'] = int(volume_match.group(1))
            if number_match and 'number' not in pub:
                pub['number'] = int(number_match.group(1))
            if pages_match and 'pages' not in pub:
                pub['pages'] = pages_match.group(1)
        
        # 标准化links字段
        pub['links'] = []
        
        # 检查并添加标准化的链接类型
        link_types = {'DOI': '', 'PDF': '', 'Code': '', 'BibTeX': '', 'GB/T 7714': '',}
        
        for link_type in link_types:
            pub['links'].append({'name': link_type, 'url': ""})
    
    # 写回YAML文件
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(publications, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print(f"成功处理 {len(publications)} 篇论文")

# 使用示例
process_publications('publications_manual_update.yml')