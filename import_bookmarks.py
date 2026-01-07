#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML书签导入到webstack.yml脚本
支持导入Chrome、Firefox、Safari等浏览器导出的HTML书签文件
"""

import yaml
import re
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import sys


class BookmarkParser(HTMLParser):
    """HTML书签解析器"""
    
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.current_folder = []
        self.current_link = {}
        self.in_link = False
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'h3':
            # 文件夹标题
            self.current_folder_name = ''
            self.in_folder = True
        elif tag == 'a':
            # 书签链接
            self.in_link = True
            self.current_link = {
                'url': attrs_dict.get('href', ''),
                'title': '',
                'folder': '/'.join(self.current_folder) if self.current_folder else '未分类'
            }
    
    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_folder = False
        elif tag == 'a' and self.in_link:
            if self.current_link.get('url'):
                self.bookmarks.append(self.current_link.copy())
            self.in_link = False
            self.current_link = {}
        elif tag == 'dl':
            # 退出文件夹
            if self.current_folder:
                self.current_folder.pop()
    
    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
            
        if hasattr(self, 'in_folder') and self.in_folder:
            self.current_folder.append(data)
            self.in_folder = False
        elif self.in_link:
            self.current_link['title'] = data


def categorize_bookmark(bookmark):
    """根据书签信息自动分类"""
    title = bookmark.get('title', '').lower()
    url = bookmark.get('url', '').lower()
    folder = bookmark.get('folder', '').lower()
    
    text = f"{title} {url} {folder}"
    
    # 分类规则
    if any(k in text for k in ['ai', '人工智能', 'gpt', 'chatgpt', 'claude', 'gemini', 'kimi', '豆包', '千问', '文心']):
        return 'AI工具', 'fas fa-robot'
    if any(k in text for k in ['视频', '音乐', '电影', 'bilibili', 'youtube', '哔哩', '优酷', '爱奇艺', '腾讯视频']):
        return '影音视频', 'fas fa-video'
    if any(k in text for k in ['github', '开发', '代码', '编程', 'stackoverflow', 'csdn', '博客', 'blog']):
        return '开发设计', 'fas fa-laptop-code'
    if any(k in text for k in ['图标', '素材', '图片', '设计', 'icon', 'pixabay', 'unsplash']):
        return '素材资源', 'fas fa-fill-drip'
    if any(k in text for k in ['新闻', '资讯', '知乎', 'v2ex', '论坛', '社区']):
        return '资讯学习', 'fas fa-book-open'
    if any(k in text for k in ['翻译', '文档', '笔记', 'notion', '语雀', '飞书']):
        return '办公学习', 'fas fa-graduation-cap'
    if any(k in text for k in ['工具', 'tool', '在线', 'online']):
        return '实用工具', 'fas fa-toolbox'
    
    return '其他收藏', 'fas fa-bookmark'


def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(data, file_path):
    """保存YAML文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def get_existing_urls(yaml_data):
    """获取已存在的URL集合"""
    urls = set()
    if not yaml_data:
        return urls
    
    for taxonomy in yaml_data:
        if 'links' in taxonomy:
            for link in taxonomy['links']:
                url = link.get('url') or link.get('usrl')
                if url:
                    urls.add(url.strip('/'))
        if 'list' in taxonomy:
            for term_item in taxonomy['list']:
                if 'links' in term_item:
                    for link in term_item['links']:
                        url = link.get('url') or link.get('usrl')
                        if url:
                            urls.add(url.strip('/'))
    return urls


def add_bookmark_to_yaml(yaml_data, bookmark, category_name, icon):
    """将书签添加到YAML数据中"""
    # 查找或创建分类
    target_taxonomy = None
    for taxonomy in yaml_data:
        if taxonomy.get('taxonomy') == category_name:
            target_taxonomy = taxonomy
            break
    
    if not target_taxonomy:
        target_taxonomy = {
            'taxonomy': category_name,
            'icon': icon,
            'list': []
        }
        yaml_data.append(target_taxonomy)
    
    # 查找或创建术语
    term_name = '浏览器书签'
    target_term = None
    
    if 'list' in target_taxonomy:
        for term in target_taxonomy['list']:
            if term.get('term') == term_name:
                target_term = term
                break
        
        if not target_term:
            target_term = {'term': term_name, 'links': []}
            target_taxonomy['list'].append(target_term)
    else:
        target_taxonomy['list'] = [{'term': term_name, 'links': []}]
        target_term = target_taxonomy['list'][0]
    
    # 添加链接
    if 'links' not in target_term:
        target_term['links'] = []
    
    target_term['links'].append({
        'title': bookmark['title'],
        'url': bookmark['url'],
        'logo': '',
        'description': f"来自: {bookmark['folder']}"
    })


def import_bookmarks(html_file, yaml_file):
    """导入书签到YAML文件"""
    print(f"正在读取书签文件: {html_file}")
    
    # 解析HTML书签
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    parser = BookmarkParser()
    parser.feed(html_content)
    
    print(f"共解析到 {len(parser.bookmarks)} 个书签")
    
    # 加载现有YAML数据
    yaml_data = load_yaml(yaml_file)
    existing_urls = get_existing_urls(yaml_data)
    
    # 导入书签
    imported_count = 0
    skipped_count = 0
    
    for bookmark in parser.bookmarks:
        url = bookmark['url'].strip('/')
        
        # 跳过无效URL
        if not url or url.startswith('javascript:') or url.startswith('chrome://'):
            continue
        
        # 跳过已存在的URL
        if url in existing_urls:
            skipped_count += 1
            continue
        
        # 分类并添加
        category_name, icon = categorize_bookmark(bookmark)
        add_bookmark_to_yaml(yaml_data, bookmark, category_name, icon)
        existing_urls.add(url)
        imported_count += 1
        
        print(f"导入: {bookmark['title']} -> {category_name}")
    
    # 保存YAML文件
    save_yaml(yaml_data, yaml_file)
    
    print(f"\n导入完成!")
    print(f"成功导入: {imported_count} 个书签")
    print(f"跳过重复: {skipped_count} 个书签")


def main():
    """主函数"""
    # 配置文件路径
    workspace = '/home/hjx/workspace/hjxnav'
    yaml_file = os.path.join(workspace, 'data/webstack.yml')
    
    # 查找HTML书签文件
    bookmark_files = []
    for filename in os.listdir(workspace):
        if filename.endswith('.html') and '书签' in filename:
            bookmark_files.append(os.path.join(workspace, filename))
    
    if not bookmark_files:
        print("未找到书签文件!")
        print("请将浏览器导出的HTML书签文件放在项目根目录下")
        return
    
    print("找到以下书签文件:")
    for i, f in enumerate(bookmark_files, 1):
        print(f"{i}. {os.path.basename(f)}")
    
    # 导入所有书签文件
    for bookmark_file in bookmark_files:
        print(f"\n{'='*60}")
        import_bookmarks(bookmark_file, yaml_file)


if __name__ == '__main__':
    main()
