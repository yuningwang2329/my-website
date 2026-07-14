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

    // ---- 动态日历 ----
    initCalendar();
});

let currentCalDate = new Date();
let activityData = {};

async function initCalendar() {
    const calContainer = document.querySelector('.calendar-container');
    if (!calContainer) return; // Only on homepage

    try {
        const response = await fetch('activity.json');
        if (response.ok) {
            activityData = await response.json();
        }
    } catch (e) {
        console.error('Failed to load activity.json', e);
    }

    document.getElementById('cal-prev').addEventListener('click', () => {
        currentCalDate.setMonth(currentCalDate.getMonth() - 1);
        renderCalendar();
    });
    document.getElementById('cal-next').addEventListener('click', () => {
        currentCalDate.setMonth(currentCalDate.getMonth() + 1);
        renderCalendar();
    });

    renderCalendar();
}

function renderCalendar() {
    const year = currentCalDate.getFullYear();
    const month = currentCalDate.getMonth();
    
    document.getElementById('cal-month').textContent = `${year}年${month + 1}月`;
    
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    const grid = document.querySelector('.calendar-grid');
    // Keep the headers (first 7 elements)
    const headers = Array.from(grid.children).slice(0, 7);
    grid.innerHTML = '';
    headers.forEach(h => grid.appendChild(h));
    
    // Empty cells before 1st day
    for (let i = 0; i < firstDay; i++) {
        const empty = document.createElement('div');
        empty.className = 'cal-cell empty';
        grid.appendChild(empty);
    }
    
    const todayStr = new Date().toISOString().split('T')[0];
    
    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        const cell = document.createElement('div');
        cell.className = 'cal-cell fade-in';
        if (dateStr > todayStr) cell.classList.add('disabled');
        if (dateStr === todayStr) cell.style.borderColor = 'var(--text)'; // Highlight today subtly
        
        let html = `<div class="cal-date-num">${d}</div>`;
        
        const act = activityData[dateStr];
        if (act && dateStr <= todayStr) {
            html += `<div class="cal-activity">`;
            if (act.papers) {
                html += `<div class="act-badge paper">+${act.papers} <span>论文</span></div>`;
            }
            if (act.notes) {
                html += `<div class="act-badge note">+${act.notes} <span>笔记</span></div>`;
            }
            html += `</div>`;
            
            cell.onclick = () => showActivityDetail(dateStr, act);
        } else {
            cell.onclick = () => showActivityDetail(dateStr, null);
        }
        
        cell.innerHTML = html;
        grid.appendChild(cell);
    }
}

function showActivityDetail(dateStr, act) {
    document.querySelectorAll('.cal-cell').forEach(c => c.classList.remove('active-day'));
    const targetCell = Array.from(document.querySelectorAll('.cal-cell')).find(c => {
        const num = c.querySelector('.cal-date-num');
        return num && dateStr.endsWith('-' + num.textContent.padStart(2, '0'));
    });
    if (targetCell) targetCell.classList.add('active-day');

    const detailContainer = document.getElementById('activity-detail');
    const content = document.getElementById('activity-content');
    document.getElementById('activity-date').textContent = `${dateStr} 更新详情`;
    
    if (!act || (!act.papers && !act.notes)) {
        content.innerHTML = '<p style="color: var(--text-secondary);">今日无更新或在闭关修炼中...</p>';
    } else {
        let html = '<ul class="activity-list">';
        if (act.papers && act.details && act.details.papers) {
            html += `
            <li class="activity-item">
                <div class="act-icon">📄</div>
                <div class="act-text">
                    <strong>新增 ${act.papers} 篇流体论文</strong><br>
                    <span style="color: var(--text-secondary); font-size: 0.85rem;">
                        ${act.details.papers.slice(0, 3).map(p => `• ${p}`).join('<br>')}
                        ${act.details.papers.length > 3 ? `<br>• 以及另外 ${act.details.papers.length - 3} 篇...` : ''}
                    </span>
                    <br><a href="fluids.html">前往文献库查看 →</a>
                </div>
            </li>`;
        }
        if (act.notes && act.details && act.details.notes) {
            html += `
            <li class="activity-item">
                <div class="act-icon">📝</div>
                <div class="act-text">
                    <strong>新增 ${act.notes} 篇笔记</strong><br>
                    <span style="color: var(--text-secondary); font-size: 0.85rem;">
                        ${act.details.notes.slice(0, 3).map(p => `• ${p}`).join('<br>')}
                    </span>
                    <br><a href="notes.html">前往笔记查看 →</a>
                </div>
            </li>`;
        }
        html += '</ul>';
        content.innerHTML = html;
    }
    
    detailContainer.style.display = 'block';
}
