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
    const dateElement = document.getElementById('last-updated');
    if (dateElement) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        dateElement.textContent = `© ${yyyy} Yuning Wang · 最后更新 ${yyyy}-${mm}-${dd}`;
    }
});
