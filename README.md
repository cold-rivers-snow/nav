# README

参考 https://github.com/shenweiyan/WebStack-Hugo 代码通过 github page 搭建自己的标签网站，便于各个平台访问，不依赖于浏览器，方便管理。防止每次换浏览器导致需要书签迁移。

## 功能特性

### 站内搜索
- 🔍 实时搜索所有导航链接
- 📋 智能下拉提示，显示最相关的结果
- 🎯 支持搜索标题、描述、URL、分类
- ⚡ 页面内容实时过滤和高亮
- 📱 响应式设计，支持各种设备

详细使用说明请查看：[站内搜索使用说明.md](./站内搜索使用说明.md)

### 书签管理
- 📥 支持从HTML书签文件导入 (`import_bookmarks.py`)
- 📤 支持导出为HTML书签文件 (`export_bookmarks.py`)
- 🧹 支持去重和清理 (`cleanup_webstack.py`)

## 本地开发

```bash
# 启动开发服务器
hugo server -D

# 构建静态网站
hugo --cleanDestinationDir
```

## 部署

推送到 GitHub 后会自动通过 GitHub Actions 部署到 GitHub Pages。
