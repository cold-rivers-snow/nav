#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webstack.yml导出为HTML书签脚本
将导航数据导出为可以导入浏览器的HTML书签格式
"""

import yaml
import os
from datetime import datetime


def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_bookmark_html(yaml_data, output_file):
    """生成HTML书签文件"""
    
    # HTML头部
    html_content = '''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<HTML>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<Title>导航网站书签</Title>
<H1>导航网站书签</H1>
<DL><p>
'''
    
    # 遍历分类
    for taxonomy in yaml_data:
        taxonomy_name = taxonomy.get('taxonomy', '未分类')
        
        # 添加分类文件夹
        html_content += f'\t<DT><H3 FOLDED>{taxonomy_name}</H3>\n'
        html_content += '\t<DL><p>\n'
        
        # 处理直接链接
        if 'links' in taxonomy:
            for link in taxonomy['links']:
                title = link.get('title', '未命名')
                url = link.get('url') or link.get('usrl', '')
                if url:
                    html_content += f'\t\t<DT><A HREF="{url}">{title}</A>\n'
        
        # 处理术语分组
        if 'list' in taxonomy:
            for term_item in taxonomy['list']:
                term_name = term_item.get('term', '其他')
                
                # 添加术语子文件夹
                html_content += f'\t\t<DT><H3 FOLDED>{term_name}</H3>\n'
                html_content += '\t\t<DL><p>\n'
                
                if 'links' in term_item:
                    for link in term_item['links']:
                        title = link.get('title', '未命名')
                        url = link.get('url') or link.get('usrl', '')
                        if url:
                            html_content += f'\t\t\t<DT><A HREF="{url}">{title}</A>\n'
                
                html_content += '\t\t</DL><p>\n'
        
        html_content += '\t</DL><p>\n'
    
    # HTML尾部
    html_content += '</DL><p>\n</HTML>'
    
    # 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    """主函数"""
    workspace = '/home/hjx/workspace/hjxnav'
    yaml_file = os.path.join(workspace, 'data/webstack.yml')
    
    # 生成输出文件名(带时间戳)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(workspace, f'导航书签导出_{timestamp}.html')
    
    print(f"正在读取导航数据: {yaml_file}")
    yaml_data = load_yaml(yaml_file)
    
    print(f"正在生成HTML书签文件...")
    generate_bookmark_html(yaml_data, output_file)
    
    print(f"\n导出成功!")
    print(f"文件保存位置: {output_file}")
    print(f"\n使用方法:")
    print(f"1. 打开浏览器的书签管理器")
    print(f"2. 选择'导入书签'功能")
    print(f"3. 选择生成的HTML文件: {os.path.basename(output_file)}")
    
    # 统计信息
    total_links = 0
    for taxonomy in yaml_data:
        if 'links' in taxonomy:
            total_links += len(taxonomy['links'])
        if 'list' in taxonomy:
            for term_item in taxonomy['list']:
                if 'links' in term_item:
                    total_links += len(term_item['links'])
    
    print(f"\n共导出 {len(yaml_data)} 个分类, {total_links} 个链接")


if __name__ == '__main__':
    main()
