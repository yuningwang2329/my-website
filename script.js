document.addEventListener('DOMContentLoaded', function () {
    // ---- 动态问候 ----
    var greetingEl = document.getElementById('greeting');
    if (greetingEl) {
        var hour = new Date().getHours();
        var text = '你好';
        if (hour >= 5 && hour < 12)       text = '早上好';
        else if (hour >= 12 && hour < 18) text = '下午好';
        else if (hour >= 18 && hour < 22) text = '晚上好';
        else                              text = '夜深了';
        greetingEl.textContent = text;
    }

    // ---- 最后更新时间 ----
    var updatedEl = document.getElementById('last-updated');
    if (updatedEl) {
        // 使用 GitHub Pages 的最后部署时间：每次 push 后自动更新
        // 这里使用页面实际渲染时间作为近似值
        var now = new Date();
        var dateStr = now.getFullYear() + '-' +
            String(now.getMonth() + 1).padStart(2, '0') + '-' +
            String(now.getDate()).padStart(2, '0');
        updatedEl.textContent = '最后更新 ' + dateStr;
    }
});
