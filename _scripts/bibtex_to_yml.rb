#!/usr/bin/env ruby

require 'bibtex'
require 'yaml'

# 转换单个BibTeX条目为YAML兼容格式
def convert_entry(entry)
  {
    'id' => entry.key,
    'title' => entry.title.to_s,
    'authors' => entry.authors ? entry.authors.map(&:to_s) : [],
    'year' => entry.year.to_s,
    'venue' => [entry.journal, entry.booktitle].compact.join(' '),
    'type' => entry.type.to_s,
    'links' => {
      'DOI' => entry.doi,
      'PDF' => entry.url
    }.compact,
    'tags' => entry.keywords.to_s.split(/\s*,\s*/)
  }.compact
end

begin
  # 读取BibTeX文件
  bib = BibTeX.open('_data/pubs.bib')
  
  # 转换为YAML数组
  yaml_data = bib.map { |entry| convert_entry(entry) }
  
  # 写入YAML文件
  File.open('_data/publication_collection.yml', 'w') do |f|
    f.write YAML.dump(yaml_data)
    puts "成功转换 #{yaml_data.size} 篇出版物到 _data/publications.yml"
  end

rescue => e
  puts "转换失败: #{e.message}"
  puts "请检查："
  puts "1. 是否已安装bibtex-ruby (gem install bibtex-ruby)"
  puts "2. _data/pubs.bib 文件是否存在"
  exit 1
end