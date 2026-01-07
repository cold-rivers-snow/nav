#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webstack.yml 整理和去重脚本
- 去除重复的URL
- 整理分类结构
- 生成去重报告
"""

import yaml
import os
from urllib.parse import urlparse
from collections import defaultdict


def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(data, file_path):
    """保存YAML文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def normalize_url(url):
    """标准化URL用于比较"""
    if not url:
        return ''
    
    url = url.strip()
    # 移除末尾的斜杠
    url = url.rstrip('/')
    # 统一协议
    url = url.replace('http://', 'https://')
    
    return url.lower()


def clean_and_deduplicate(yaml_data):
    """清理和去重数据"""
    
    # 用于跟踪URL和它们的位置
    url_registry = {}  # {normalized_url: {'taxonomy': '', 'term': '', 'link': {}}}
    duplicates = []  # 重复的URL记录
    
    cleaned_data = []
    
    for taxonomy in yaml_data:
        taxonomy_name = taxonomy.get('taxonomy', '未分类')
        cleaned_taxonomy = {
            'taxonomy': taxonomy_name,
            'icon': taxonomy.get('icon', 'fas fa-bookmark')
        }
        
        # 处理直接链接
        if 'links' in taxonomy:
            cleaned_links = []
            for link in taxonomy['links']:
                url = link.get('url') or link.get('usrl', '')
                if not url:
                    continue
                
                normalized = normalize_url(url)
                
                # 检查是否重复
                if normalized in url_registry:
                    duplicates.append({
                        'url': url,
                        'title': link.get('title', ''),
                        'current_location': f"{taxonomy_name}",
                        'first_location': f"{url_registry[normalized]['taxonomy']}"
                    })
                    continue
                
                # 记录URL
                url_registry[normalized] = {
                    'taxonomy': taxonomy_name,
                    'term': '',
                    'link': link
                }
                
                # 清理链接数据
                cleaned_link = {
                    'title': link.get('title', '未命名'),
                    'url': url,
                    'logo': link.get('logo', ''),
                    'description': link.get('description', '')
                }
                cleaned_links.append(cleaned_link)
            
            if cleaned_links:
                cleaned_taxonomy['links'] = cleaned_links
        
        # 处理术语列表
        if 'list' in taxonomy:
            cleaned_list = []
            for term_item in taxonomy['list']:
                term_name = term_item.get('term', '其他')
                cleaned_term = {'term': term_name}
                
                if 'links' in term_item:
                    cleaned_term_links = []
                    for link in term_item['links']:
                        url = link.get('url') or link.get('usrl', '')
                        if not url:
                            continue
                        
                        normalized = normalize_url(url)
                        
                        # 检查是否重复
                        if normalized in url_registry:
                            duplicates.append({
                                'url': url,
                                'title': link.get('title', ''),
                                'current_location': f"{taxonomy_name} > {term_name}",
                                'first_location': f"{url_registry[normalized]['taxonomy']}" + 
                                                (f" > {url_registry[normalized]['term']}" if url_registry[normalized]['term'] else "")
                            })
                            continue
                        
                        # 记录URL
                        url_registry[normalized] = {
                            'taxonomy': taxonomy_name,
                            'term': term_name,
                            'link': link
                        }
                        
                        # 清理链接数据
                        cleaned_link = {
                            'title': link.get('title', '未命名'),
                            'url': url,
                            'logo': link.get('logo', ''),
                            'description': link.get('description', '')
                        }
                        cleaned_term_links.append(cleaned_link)
                    
                    if cleaned_term_links:
                        cleaned_term['links'] = cleaned_term_links
                        cleaned_list.append(cleaned_term)
            
            if cleaned_list:
                cleaned_taxonomy['list'] = cleaned_list
        
        # 只添加有内容的分类
        if 'links' in cleaned_taxonomy or 'list' in cleaned_taxonomy:
            cleaned_data.append(cleaned_taxonomy)
    
    return cleaned_data, duplicates, url_registry


def generate_report(duplicates, url_registry, original_count, cleaned_count):
    """生成去重报告"""
    
    report = []
    report.append("=" * 80)
    report.append("WebStack.yml 整理和去重报告")
    report.append("=" * 80)
    report.append("")
    
    report.append(f"📊 统计信息:")
    report.append(f"  - 原始链接总数: {original_count}")
    report.append(f"  - 清理后链接数: {cleaned_count}")
    report.append(f"  - 去除重复数量: {len(duplicates)}")
    report.append(f"  - 去重率: {len(duplicates)/original_count*100:.2f}%" if original_count > 0 else "  - 去重率: 0%")
    report.append("")
    
    if duplicates:
        report.append(f"🔍 发现的重复链接 ({len(duplicates)} 个):")
        report.append("-" * 80)
        
        # 按分类分组显示
        by_taxonomy = defaultdict(list)
        for dup in duplicates:
            by_taxonomy[dup['current_location']].append(dup)
        
        for location, dups in sorted(by_taxonomy.items()):
            report.append(f"\n位置: {location}")
            for dup in dups:
                report.append(f"  ❌ {dup['title']}")
                report.append(f"     URL: {dup['url']}")
                report.append(f"     首次出现: {dup['first_location']}")
                report.append("")
    else:
        report.append("✅ 未发现重复链接")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def count_links(yaml_data):
    """统计链接总数"""
    count = 0
    for taxonomy in yaml_data:
        if 'links' in taxonomy:
            count += len(taxonomy['links'])
        if 'list' in taxonomy:
            for term_item in taxonomy['list']:
                if 'links' in term_item:
                    count += len(term_item['links'])
    return count


def main():
    """主函数"""
    workspace = '/home/hjx/workspace/hjxnav'
    yaml_file = os.path.join(workspace, 'data/webstack.yml')
    backup_file = os.path.join(workspace, 'data/webstack_backup.yml')
    report_file = os.path.join(workspace, 'deduplication_report.txt')
    
    print("🔧 开始整理和去重 webstack.yml...")
    print()
    
    # 加载数据
    print("📖 正在读取数据...")
    yaml_data = load_yaml(yaml_file)
    original_count = count_links(yaml_data)
    
    # 备份原文件
    print("💾 正在备份原文件...")
    save_yaml(yaml_data, backup_file)
    print(f"   备份已保存: {backup_file}")
    print()
    
    # 清理和去重
    print("🧹 正在清理和去重...")
    cleaned_data, duplicates, url_registry = clean_and_deduplicate(yaml_data)
    cleaned_count = count_links(cleaned_data)
    
    # 保存清理后的数据
    print("💾 正在保存清理后的数据...")
    save_yaml(cleaned_data, yaml_file)
    print()
    
    # 生成报告
    report = generate_report(duplicates, url_registry, original_count, cleaned_count)
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 显示报告
    print(report)
    print()
    print(f"📄 详细报告已保存: {report_file}")
    print()
    
    if duplicates:
        print("✨ 整理完成！已去除重复链接。")
        print(f"   如需恢复，请使用备份文件: {backup_file}")
    else:
        print("✨ 整理完成！未发现重复链接。")


if __name__ == '__main__':
    main()
