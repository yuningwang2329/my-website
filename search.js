/*
 * search.js - 全站客户端搜索
 * 维护一份内容索引，用户输入时实时过滤匹配。
 */

// ---- 内容索引 ----
// 每次新增笔记或出版物时，在这里加一条即可。
var SEARCH_INDEX = [
    {
        title: '主页',
        desc:  '随便记点东西的地方',
        url:   'index.html',
        tags:  '首页 主页 home'
    },
    {
        title: 'Linear and Nonlinear Enhanced Dissipation for the 2-D Micropolar Equations Near Couette Flow',
        desc:  '2026 · Discrete and Continuous Dynamical Systems - Series B',
        url:   'post.html?file=micropolar-equations.md',
        tags:  '出版物 论文 micropolar couette PDE 偏微分方程'
    },
    {
        title: 'Global Well-Posedness and Large Time Behavior of Boussinesq Equations With Fractional Dissipation',
        desc:  '2026 · Studies in Applied Mathematics',
        url:   'post.html?file=boussinesq-equations.md',
        tags:  '出版物 论文 boussinesq fractional PDE 偏微分方程'
    },
    {
        title: '简历',
        desc:  '教育背景、工作经历与技能',
        url:   'resume.html',
        tags:  '简历 resume CV 经历'
    },
    {
        title: '你好，世界！我的第一篇测试笔记',
        desc:  '2026-07-10',
        url:   'post.html?file=hello-world.md',
        tags:  '笔记 hello world markdown'
    }
];

// ---- DOM ----
function initSearch() {
    var overlay = document.getElementById('search-overlay');
    var input   = document.getElementById('search-input');
    var results = document.getElementById('search-results');
    var btn     = document.getElementById('search-btn');

    if (!overlay || !input || !results || !btn) return;

    // 打开
    btn.addEventListener('click', function (e) {
        e.preventDefault();
        overlay.classList.add('open');
        input.value = '';
        results.innerHTML = '';
        setTimeout(function () { input.focus(); }, 50);
    });

    // 关闭
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) overlay.classList.remove('open');
    });

    document.addEventListener('keydown', function (e) {
        // Cmd/Ctrl + K 打开搜索
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            overlay.classList.add('open');
            input.value = '';
            results.innerHTML = '';
            setTimeout(function () { input.focus(); }, 50);
        }
        // Esc 关闭
        if (e.key === 'Escape') {
            overlay.classList.remove('open');
        }
    });

    // 实时搜索
    input.addEventListener('input', function () {
        var q = input.value.trim().toLowerCase();
        results.innerHTML = '';

        if (!q) return;

        var matches = SEARCH_INDEX.filter(function (item) {
            var haystack = (item.title + ' ' + item.desc + ' ' + item.tags).toLowerCase();
            return haystack.indexOf(q) !== -1;
        });

        if (matches.length === 0) {
            results.innerHTML = '<div class="search-empty">没有找到相关内容</div>';
            return;
        }

        matches.forEach(function (item) {
            var a = document.createElement('a');
            a.href = item.url;
            a.className = 'search-result-item';
            a.innerHTML =
                '<span class="search-result-title">' + item.title + '</span>' +
                '<span class="search-result-desc">' + item.desc + '</span>';
            results.appendChild(a);
        });
    });
}

document.addEventListener('DOMContentLoaded', initSearch);
