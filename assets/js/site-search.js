/**
 * 站内导航搜索功能
 * 实时搜索导航链接的标题、描述和URL
 */

(function() {
    'use strict';

    // 搜索数据缓存
    let searchData = [];
    let searchIndex = null;

    /**
     * 初始化搜索数据
     * 从页面中提取所有导航链接信息
     */
    function initSearchData() {
        searchData = [];
        
        // 遍历所有导航卡片
        $('.url-card').each(function(index) {
            const $card = $(this);
            // 查找链接元素
            const $link = $card.find('a.card');
            
            // 提取信息
            const title = $card.find('.url-info strong').text().trim();
            const description = $card.find('.url-info p').text().trim();
            const url = $link.attr('href') || '';
            const logo = $card.find('.url-img img').attr('src') || '';
            
            // 获取所属分类
            // 向上找到所在的row，然后找前面的h4
            const $row = $card.closest('.row');
            let taxonomy = '';
            
            // 尝试从前面的h4获取分类名
            const $prevHeader = $row.prevAll('h4').first();
            if ($prevHeader.length > 0) {
                taxonomy = $prevHeader.text().trim();
            }
            
            if (title) {
                searchData.push({
                    index: index,
                    title: title,
                    description: description,
                    url: url,
                    logo: logo,
                    taxonomy: taxonomy,
                    term: taxonomy, // 暂时将term设为相同，因为结构上只显示了一级
                    element: $card
                });
            }
        });
        
        console.log(`站内搜索已加载 ${searchData.length} 个链接`);
    }

    /**
     * 执行搜索
     * @param {string} keyword - 搜索关键词
     * @returns {Array} 搜索结果数组
     */
    function performSearch(keyword) {
        if (!keyword || keyword.trim() === '') {
            return [];
        }

        keyword = keyword.toLowerCase().trim();
        const results = [];

        searchData.forEach(function(item) {
            const titleMatch = item.title.toLowerCase().indexOf(keyword) !== -1;
            const descMatch = item.description.toLowerCase().indexOf(keyword) !== -1;
            const urlMatch = item.url.toLowerCase().indexOf(keyword) !== -1;
            const taxonomyMatch = item.taxonomy.toLowerCase().indexOf(keyword) !== -1;

            if (titleMatch || descMatch || urlMatch || taxonomyMatch) {
                // 计算匹配度分数
                let score = 0;
                if (titleMatch) score += 10;
                if (descMatch) score += 5;
                if (taxonomyMatch) score += 3;
                if (urlMatch) score += 1;

                results.push({
                    ...item,
                    score: score
                });
            }
        });

        // 按分数排序
        results.sort((a, b) => b.score - a.score);
        
        return results;
    }

    /**
     * 高亮显示搜索结果
     * @param {string} keyword - 搜索关键词
     */
    function highlightResults(keyword) {
        if (!keyword || keyword.trim() === '') {
            // 清除所有高亮和隐藏
            $('.url-card').removeClass('search-highlight search-hidden').show();
            // 恢复所有标题和容器的显示
            $('.row, h4, .d-flex.flex-fill').show();
            return;
        }

        const results = performSearch(keyword);
        const resultIndexes = new Set(results.map(r => r.index));

        // 隐藏所有项目
        $('.url-card').addClass('search-hidden').removeClass('search-highlight');

        // 显示并高亮匹配的项目
        results.forEach(function(result) {
            result.element.removeClass('search-hidden').addClass('search-highlight').show();
        });

        // 隐藏空的行和标题
        $('.row').each(function() {
            const $row = $(this);
            const visibleItems = $row.find('.url-card:not(.search-hidden)').length;
            
            // 找到关联的标题（前面的h4和.d-flex）
            const $header = $row.prevAll('h4').first();
            const $flexHeader = $row.prevAll('.d-flex.flex-fill').first();

            if (visibleItems === 0) {
                $row.hide();
                $header.hide();
                $flexHeader.hide();
            } else {
                $row.show();
                $header.show();
                $flexHeader.show();
            }
        });
    }

    /**
     * 显示搜索结果下拉列表
     * @param {string} keyword - 搜索关键词
     * @param {jQuery} $input - 输入框元素
     */
    function showSearchDropdown(keyword, $input) {
        const results = performSearch(keyword);
        const $dropdown = $('#site-search-dropdown');
        
        if (results.length === 0) {
            $dropdown.html('<div class="search-no-result">未找到匹配结果</div>').show();
            return;
        }

        let html = '<div class="search-results-list">';
        
        // 最多显示10个结果
        const displayResults = results.slice(0, 10);
        
        displayResults.forEach(function(result) {
            const highlightedTitle = highlightKeyword(result.title, keyword);
            const highlightedDesc = highlightKeyword(result.description, keyword);
            const category = result.term || result.taxonomy;
            
            html += `
                <div class="search-result-item" data-url="${escapeHtml(result.url)}">
                    <div class="search-result-icon">
                        ${result.logo ? `<img src="${escapeHtml(result.logo)}" alt="">` : '<i class="iconfont icon-link"></i>'}
                    </div>
                    <div class="search-result-content">
                        <div class="search-result-title">${highlightedTitle}</div>
                        <div class="search-result-desc">${highlightedDesc || result.url}</div>
                        <div class="search-result-category">${escapeHtml(category)}</div>
                    </div>
                </div>
            `;
        });
        
        if (results.length > 10) {
            html += `<div class="search-result-more">还有 ${results.length - 10} 个结果...</div>`;
        }
        
        html += '</div>';
        
        $dropdown.html(html).show();
    }

    /**
     * 高亮关键词
     * @param {string} text - 原文本
     * @param {string} keyword - 关键词
     * @returns {string} 高亮后的HTML
     */
    function highlightKeyword(text, keyword) {
        if (!text || !keyword) return escapeHtml(text);
        
        const regex = new RegExp(`(${escapeRegex(keyword)})`, 'gi');
        return escapeHtml(text).replace(regex, '<mark>$1</mark>');
    }

    /**
     * 转义HTML特殊字符
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 转义正则表达式特殊字符
     */
    function escapeRegex(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * 初始化搜索功能
     */
    function initSiteSearch() {
        // 创建搜索下拉容器
        if ($('#site-search-dropdown').length === 0) {
            $('body').append('<div id="site-search-dropdown" class="site-search-dropdown"></div>');
        }

        // 添加站内搜索输入框（在导航栏）
        const $searchContainer = $('.navbar-form, .search-form').first();
        if ($searchContainer.length > 0 && $('#site-search-input').length === 0) {
            const searchHtml = `
                <div class="site-search-container">
                    <input type="text" 
                           id="site-search-input" 
                           class="form-control" 
                           placeholder="站内搜索导航..." 
                           autocomplete="off">
                    <i class="iconfont icon-search site-search-icon"></i>
                    <i class="iconfont icon-close site-search-clear" style="display:none;"></i>
                </div>
            `;
            $searchContainer.prepend(searchHtml);
        }

        // 绑定搜索事件
        let searchTimeout;
        $(document).on('input', '#site-search-input', function() {
            const keyword = $(this).val();
            const $input = $(this);
            
            // 显示/隐藏清除按钮
            if (keyword) {
                $('.site-search-clear').show();
            } else {
                $('.site-search-clear').hide();
            }

            // 防抖处理
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                highlightResults(keyword);
                if (keyword) {
                    showSearchDropdown(keyword, $input);
                } else {
                    $('#site-search-dropdown').hide();
                }
            }, 300);
        });

        // 清除搜索
        $(document).on('click', '.site-search-clear', function() {
            $('#site-search-input').val('').trigger('input').focus();
        });

        // 点击搜索结果
        $(document).on('click', '.search-result-item', function() {
            const url = $(this).data('url');
            if (url && url !== 'javascript:' && url !== '#') {
                window.open(url, '_blank');
            }
        });

        // 点击页面其他地方关闭下拉
        $(document).on('click', function(e) {
            if (!$(e.target).closest('#site-search-input, #site-search-dropdown').length) {
                $('#site-search-dropdown').hide();
            }
        });

        // ESC键关闭搜索
        $(document).on('keydown', function(e) {
            if (e.key === 'Escape') {
                $('#site-search-input').val('').trigger('input');
                $('#site-search-dropdown').hide();
            }
        });

        console.log('站内搜索功能已初始化');
    }

    // 页面加载完成后初始化
    $(document).ready(function() {
        // 等待页面内容加载完成
        setTimeout(function() {
            initSearchData();
            initSiteSearch();
        }, 1000);
    });

})();
