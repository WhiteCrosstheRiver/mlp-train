// mlp-train 使用手册交互脚本

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
