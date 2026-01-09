#!/usr/bin/env python3
"""
mlp-train 使用手册网页生成脚本

将 docs/manual/ 目录下的 Markdown 文件转换为美观的本地网页。

使用方法:
    python generate_manual_website.py

输出:
    docs/manual/index.html - 主页面（包含所有内容）
    docs/manual/style.css - 样式文件
    docs/manual/script.js - 交互脚本
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

try:
    import markdown
    from markdown.extensions import codehilite, toc, fenced_code
except ImportError:
    print("错误: 需要安装 markdown 库")
    print("请运行: pip install markdown")
    exit(1)

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False
    print("警告: pygments 未安装，代码高亮功能将受限")
    print("建议运行: pip install pygments")


class ManualGenerator:
    """手册网页生成器"""
    
    def __init__(self, manual_dir: str = "docs/manual"):
        self.manual_dir = Path(manual_dir)
        self.output_dir = self.manual_dir
        self.manual_files = []
        self.manual_data = []
        
    def find_manual_files(self) -> List[Path]:
        """查找所有手册文件"""
        files = sorted(self.manual_dir.glob("*.md"))
        # 排除 README.md，它会被单独处理
        files = [f for f in files if f.name != "README.md"]
        return files
    
    def parse_markdown(self, filepath: Path) -> Dict:
        """解析 Markdown 文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题
        title_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else filepath.stem
        
        # 提取目录（所有标题）
        headings = []
        for line in content.split('\n'):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                if text:
                    headings.append({
                        'level': level,
                        'text': text,
                        'id': self.slugify(text)
                    })
        
        return {
            'filename': filepath.name,
            'title': title,
            'content': content,
            'headings': headings
        }
    
    def slugify(self, text: str) -> str:
        """将文本转换为 URL 友好的 slug"""
        # 移除特殊字符，替换空格为连字符
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.lower()
    
    def markdown_to_html(self, content: str) -> str:
        """将 Markdown 转换为 HTML"""
        # 配置 Markdown 扩展
        extensions = [
            'codehilite',
            'toc',
            'fenced_code',
            'tables',
            'nl2br',
        ]
        
        md = markdown.Markdown(extensions=extensions, extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': PYGMENTS_AVAILABLE,
            },
            'toc': {
                'permalink': True,
                'toc_depth': 3,
            }
        })
        
        html = md.convert(content)
        return html
    
    def generate_css(self) -> str:
        """生成 CSS 样式"""
        return """/* mlp-train 使用手册样式 */

:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --bg-color: #ffffff;
    --text-color: #1e293b;
    --code-bg: #f1f5f9;
    --border-color: #e2e8f0;
    --sidebar-width: 280px;
    --header-height: 60px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
}

/* 头部 */
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: var(--header-height);
    background: linear-gradient(135deg, var(--primary-color) 0%, #1e40af 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 1000;
}

.header h1 {
    font-size: 1.5rem;
    font-weight: 600;
}

.search-box {
    flex: 1;
    max-width: 400px;
    margin: 0 2rem;
}

.search-box input {
    width: 100%;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    font-size: 0.9rem;
}

.search-box input::placeholder {
    color: rgba(255, 255, 255, 0.7);
}

.search-box input:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.3);
}

/* 主容器 */
.container {
    display: flex;
    margin-top: var(--header-height);
    min-height: calc(100vh - var(--header-height));
}

/* 侧边栏 */
.sidebar {
    position: fixed;
    left: 0;
    top: var(--header-height);
    width: var(--sidebar-width);
    height: calc(100vh - var(--header-height));
    background: #f8fafc;
    border-right: 1px solid var(--border-color);
    overflow-y: auto;
    padding: 1.5rem;
}

.sidebar h2 {
    font-size: 1.1rem;
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.sidebar ul {
    list-style: none;
}

.sidebar li {
    margin-bottom: 0.5rem;
}

.sidebar a {
    display: block;
    padding: 0.5rem;
    color: var(--text-color);
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.sidebar a:hover {
    background-color: #e2e8f0;
}

.sidebar a.active {
    background-color: var(--primary-color);
    color: white;
}

/* 内容区域 */
.content {
    margin-left: var(--sidebar-width);
    padding: 2rem 3rem;
    max-width: 1200px;
    width: 100%;
}

.section {
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 2px solid var(--border-color);
}

.section:last-child {
    border-bottom: none;
}

.section h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: var(--primary-color);
    padding-bottom: 0.5rem;
    border-bottom: 3px solid var(--primary-color);
}

.section h2 {
    font-size: 2rem;
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: var(--text-color);
}

.section h3 {
    font-size: 1.5rem;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    color: var(--text-color);
}

.section h4 {
    font-size: 1.25rem;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    color: var(--secondary-color);
}

.section p {
    margin-bottom: 1rem;
    text-align: justify;
}

.section ul, .section ol {
    margin-left: 2rem;
    margin-bottom: 1rem;
}

.section li {
    margin-bottom: 0.5rem;
}

.section a {
    color: var(--primary-color);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s;
}

.section a:hover {
    border-bottom-color: var(--primary-color);
}

/* 代码块 */
pre {
    background: var(--code-bg);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
    margin: 1rem 0;
}

code {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 0.9em;
}

pre code {
    background: transparent;
    padding: 0;
}

.highlight {
    margin: 1rem 0;
}

/* 表格 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

table th, table td {
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    text-align: left;
}

table th {
    background-color: var(--code-bg);
    font-weight: 600;
}

table tr:nth-child(even) {
    background-color: #f8fafc;
}

/* 目录 */
.toc {
    background: #f8fafc;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 1.5rem;
    margin: 2rem 0;
}

.toc ul {
    list-style: none;
    margin-left: 0;
}

.toc li {
    margin-bottom: 0.5rem;
}

.toc a {
    color: var(--primary-color);
}

/* 返回顶部按钮 */
.back-to-top {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 50px;
    height: 50px;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: none;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    transition: transform 0.2s;
    z-index: 999;
}

.back-to-top:hover {
    transform: scale(1.1);
}

.back-to-top.show {
    display: flex;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s;
    }
    
    .sidebar.open {
        transform: translateX(0);
    }
    
    .content {
        margin-left: 0;
        padding: 1rem;
    }
    
    .header {
        padding: 0 1rem;
    }
    
    .search-box {
        max-width: 200px;
        margin: 0 1rem;
    }
}

/* 打印样式 */
@media print {
    .header, .sidebar, .back-to-top {
        display: none;
    }
    
    .content {
        margin-left: 0;
        padding: 0;
    }
    
    .section {
        page-break-inside: avoid;
    }
}
"""
    
    def generate_js(self) -> str:
        """生成 JavaScript 脚本"""
        return """// mlp-train 使用手册交互脚本

document.addEventListener('DOMContentLoaded', function() {
    // 搜索功能
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            if (query.length > 0) {
                searchContent(query);
            } else {
                clearSearch();
            }
        });
    }
    
    // 高亮当前导航项
    highlightCurrentNav();
    
    // 返回顶部按钮
    initBackToTop();
    
    // 平滑滚动
    initSmoothScroll();
});

// 搜索内容
function searchContent(query) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        const text = section.textContent.toLowerCase();
        if (text.includes(query)) {
            section.style.display = 'block';
            highlightText(section, query);
        } else {
            section.style.display = 'none';
        }
    });
}

// 清除搜索
function clearSearch() {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.display = 'block';
        removeHighlights(section);
    });
}

// 高亮文本
function highlightText(element, query) {
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    const textNodes = [];
    let node;
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    
    textNodes.forEach(textNode => {
        const text = textNode.textContent;
        const regex = new RegExp(`(${query})`, 'gi');
        if (regex.test(text)) {
            const highlighted = text.replace(regex, '<mark>$1</mark>');
            const span = document.createElement('span');
            span.innerHTML = highlighted;
            textNode.parentNode.replaceChild(span, textNode);
        }
    });
}

// 移除高亮
function removeHighlights(element) {
    const marks = element.querySelectorAll('mark');
    marks.forEach(mark => {
        const parent = mark.parentNode;
        parent.replaceChild(document.createTextNode(mark.textContent), mark);
        parent.normalize();
    });
}

// 高亮当前导航项
function highlightCurrentNav() {
    const links = document.querySelectorAll('.sidebar a');
    const currentHash = window.location.hash;
    
    links.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentHash || 
            (currentHash === '' && link.getAttribute('href') === '#section-0')) {
            link.classList.add('active');
        }
    });
}

// 返回顶部
function initBackToTop() {
    const button = document.createElement('button');
    button.className = 'back-to-top';
    button.innerHTML = '↑';
    button.setAttribute('aria-label', '返回顶部');
    document.body.appendChild(button);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            button.classList.add('show');
        } else {
            button.classList.remove('show');
        }
    });
    
    button.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 平滑滚动
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}
"""
    
    def generate_html(self) -> str:
        """生成完整的 HTML 页面"""
        # 读取 README
        readme_path = self.manual_dir / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        else:
            readme_content = "# mlp-train 使用手册"
        
        # 生成导航菜单
        nav_html = '<ul>\n'
        for i, data in enumerate(self.manual_data):
            nav_html += f'    <li><a href="#section-{i}">{data["title"]}</a></li>\n'
        nav_html += '</ul>'
        
        # 生成内容
        content_html = ''
        for i, data in enumerate(self.manual_data):
            html_content = self.markdown_to_html(data['content'])
            content_html += f'''
            <section id="section-{i}" class="section">
                {html_content}
            </section>
'''
        
        # 完整 HTML
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>mlp-train 使用手册</title>
    <link rel="stylesheet" href="style.css">
    <style>
        /* Pygments 代码高亮样式 */
        {self.get_pygments_css() if PYGMENTS_AVAILABLE else ''}
    </style>
</head>
<body>
    <header class="header">
        <h1>mlp-train 使用手册</h1>
        <div class="search-box">
            <input type="text" id="search-input" placeholder="搜索内容...">
        </div>
    </header>
    
    <div class="container">
        <nav class="sidebar">
            <h2>目录</h2>
            {nav_html}
        </nav>
        
        <main class="content">
            <section class="section" id="readme">
                {self.markdown_to_html(readme_content)}
            </section>
            {content_html}
        </main>
    </div>
    
    <script src="script.js"></script>
</body>
</html>'''
        
        return html
    
    def get_pygments_css(self) -> str:
        """获取 Pygments CSS 样式"""
        if not PYGMENTS_AVAILABLE:
            return ''
        formatter = HtmlFormatter(style='default')
        return formatter.get_style_defs('.highlight')
    
    def generate(self):
        """生成所有文件"""
        print("正在生成使用手册网页...")
        
        # 查找手册文件
        self.manual_files = self.find_manual_files()
        print(f"找到 {len(self.manual_files)} 个手册文件")
        
        # 解析所有文件
        for filepath in self.manual_files:
            print(f"  解析: {filepath.name}")
            data = self.parse_markdown(filepath)
            self.manual_data.append(data)
        
        # 生成文件
        print("生成 HTML...")
        html = self.generate_html()
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("生成 CSS...")
        css = self.generate_css()
        with open(self.output_dir / "style.css", 'w', encoding='utf-8') as f:
            f.write(css)
        
        print("生成 JavaScript...")
        js = self.generate_js()
        with open(self.output_dir / "script.js", 'w', encoding='utf-8') as f:
            f.write(js)
        
        print(f"\n完成！文件已生成到: {self.output_dir}")
        print(f"打开 {self.output_dir / 'index.html'} 查看手册")


def main():
    """主函数"""
    generator = ManualGenerator()
    generator.generate()


if __name__ == "__main__":
    main()

