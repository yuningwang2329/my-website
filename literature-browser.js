/* global localStorage */

let allPapers = [];
let currentPapers = [];
let subscriptionIndex = null;
let currentScope = 'current';
let activeArchiveYear = null;
let baseView = 'archive';
let filterJournal = null;
let filterMonth = null;
let filterSourceGroup = null;
const archiveCache = new Map();

const JOURNAL_GROUPS = [
    { id: 'math-fluid-pde', label: '数学流体与非线性 PDE' },
    { id: 'top-general-math', label: '顶级综合数学' },
    { id: 'high-general-math', label: '综合数学高刊' },
];

const LEGACY_SOURCE_GROUPS = {
    'Arxiv (math.AP)': 'math-fluid-pde',
    'Appl. Math. Lett.': 'math-fluid-pde',
    'Arch. Ration. Mech. Anal.': 'math-fluid-pde',
    'Commun. Math. Phys.': 'math-fluid-pde',
    'Commun. Pure Appl. Math.': 'math-fluid-pde',
    'Calc. Var. Partial Differ. Equ.': 'math-fluid-pde',
    'J. Differ. Equ.': 'math-fluid-pde',
    'J. Funct. Anal.': 'math-fluid-pde',
    'SIAM J. Math. Anal.': 'math-fluid-pde',
    'J. Math. Pures Appl.': 'math-fluid-pde',
};

function getStoredList(key) {
    try {
        const value = JSON.parse(localStorage.getItem(key) || '[]');
        return Array.isArray(value) ? value : [];
    } catch (error) {
        return [];
    }
}

function getReadPapers() {
    return getStoredList('fluids_read');
}

function getStarredPapers() {
    return getStoredList('fluids_stars');
}

function paperKey(paper) {
    return paper.id || paper.filename || paper.link || paper.title;
}

function migrateLegacyLocalState(papers) {
    const stableIdsByFilename = new Map();
    papers.forEach(paper => {
        if (paper && typeof paper.id === 'string' && typeof paper.filename === 'string' && paper.filename) {
            stableIdsByFilename.set(paper.filename, paper.id);
        }
    });
    if (stableIdsByFilename.size === 0) return;
    ['fluids_read', 'fluids_stars'].forEach(key => {
        const stored = getStoredList(key);
        const migrated = stored.map(identifier => stableIdsByFilename.get(identifier) || identifier);
        const deduplicated = Array.from(new Set(migrated));
        if (deduplicated.some((identifier, index) => identifier !== stored[index]) || deduplicated.length !== stored.length) {
            localStorage.setItem(key, JSON.stringify(deduplicated));
        }
    });
}

function sourceGroupForPaper(paper) {
    return paper.source_group || LEGACY_SOURCE_GROUPS[paper.source] || null;
}

function markRead(identifier) {
    const read = getReadPapers();
    if (!read.includes(identifier)) {
        read.push(identifier);
        localStorage.setItem('fluids_read', JSON.stringify(read));
    }
}

function clearDataFilters() {
    filterJournal = null;
    filterMonth = null;
    filterSourceGroup = null;
}

function getPapersToRender() {
    const starredPapers = getStarredPapers();
    return allPapers.filter(p => {
        const identifier = paperKey(p);
        if (baseView === 'starred' && !starredPapers.includes(identifier)) return false;
        if (baseView.startsWith('topic:') && !(p.tags || []).includes(baseView.replace('topic:', ''))) return false;

        if (filterSourceGroup && sourceGroupForPaper(p) !== filterSourceGroup) return false;
        if (filterJournal && p.source !== filterJournal) return false;
        if (filterMonth && formatMonth(p.date) !== filterMonth) return false;
        return true;
    });
}

function markAllRead() {
    const read = getReadPapers();
    let added = false;
    getPapersToRender().forEach(paper => {
        const identifier = paperKey(paper);
        if (!read.includes(identifier)) {
            read.push(identifier);
            added = true;
        }
    });
    if (added) {
        localStorage.setItem('fluids_read', JSON.stringify(read));
        render();
    }
}

function toggleStar(event, identifier) {
    event.preventDefault();
    event.stopPropagation();
    let stars = getStarredPapers();
    if (stars.includes(identifier)) {
        stars = stars.filter(value => value !== identifier);
    } else {
        stars.push(identifier);
    }
    localStorage.setItem('fluids_stars', JSON.stringify(stars));
    render();
}

function toggleMobileFilters(button) {
    const panel = document.getElementById('mobile-filter-panel');
    const isOpen = panel.classList.toggle('mobile-filters-open');
    button.setAttribute('aria-expanded', String(isOpen));
    button.textContent = isOpen ? '收起筛选' : '筛选文献';
}

function switchScope(nextScope, element) {
    currentScope = nextScope;
    activeArchiveYear = null;
    baseView = 'archive';
    clearDataFilters();
    document.querySelectorAll('#scope-folders .folder-link').forEach(link => link.classList.remove('active'));
    if (element) element.classList.add('active');

    if (nextScope === 'current') {
        allPapers = currentPapers;
        render();
        return;
    }
    const newestArchive = archiveDescriptors()[0];
    if (!newestArchive) {
        allPapers = [];
        render();
        return;
    }
    loadArchiveYear(newestArchive.year);
}

async function loadArchiveYear(year) {
    const descriptor = archiveDescriptors().find(item => String(item.year) === String(year));
    if (!descriptor) {
        showMessage('找不到该年份的归档。');
        return;
    }
    currentScope = 'archive';
    activeArchiveYear = descriptor.year;
    baseView = 'archive';
    clearDataFilters();
    document.querySelectorAll('#scope-folders .folder-link').forEach(link => link.classList.toggle('active', link.textContent.includes('历史归档')));

    if (archiveCache.has(descriptor.year)) {
        allPapers = archiveCache.get(descriptor.year);
        render();
        return;
    }

    showMessage(`正在加载 ${descriptor.year} 年归档…`);
    try {
        const response = await fetch(descriptor.path);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const papers = await response.json();
        if (!Array.isArray(papers)) throw new Error('归档不是论文数组');
        if (papers.length !== descriptor.count) throw new Error('归档条数与索引不一致');
        if (currentScope !== 'archive' || String(activeArchiveYear) !== String(descriptor.year)) return;
        migrateLegacyLocalState(papers);
        archiveCache.set(descriptor.year, papers);
        allPapers = papers;
        render();
    } catch (error) {
        console.error(error);
        showMessage(`${descriptor.year} 年归档暂时无法加载；当前页面没有改写本地收藏或已读状态。`);
    }
}

function switchFolder(folderId, element) {
    baseView = folderId;
    document.querySelectorAll('#main-folders .folder-link, #topic-folders .folder-link').forEach(link => link.classList.remove('active'));
    if (element) element.classList.add('active');
    render();
}

function switchFilterTab(tabType, element) {
    document.querySelectorAll('.sidebar-tab').forEach(tab => tab.classList.remove('active'));
    element.classList.add('active');
    document.getElementById('journal-filters').style.display = tabType === 'journal' ? 'block' : 'none';
    document.getElementById('month-filters').style.display = tabType === 'month' ? 'block' : 'none';
}

function toggleSourceGroupFilter(groupId) {
    filterSourceGroup = filterSourceGroup === groupId ? null : groupId;
    render();
}

function clearSourceGroupFilter() {
    filterSourceGroup = null;
    render();
}

function toggleJournalFilter(journal) {
    filterJournal = filterJournal === journal ? null : journal;
    render();
}

function clearJournalFilter() {
    filterJournal = null;
    render();
}

function toggleMonthFilter(month) {
    filterMonth = filterMonth === month ? null : month;
    render();
}

function clearMonthFilter() {
    filterMonth = null;
    render();
}

function formatMonth(dateStr) {
    const parts = String(dateStr || '').split('-');
    return parts.length >= 2 ? `${parts[0]}年${parseInt(parts[1], 10)}月` : String(dateStr || '未知日期');
}

function archiveDescriptors() {
    if (!subscriptionIndex || !Array.isArray(subscriptionIndex.archives)) return [];
    return subscriptionIndex.archives
        .filter(item => item && Number.isInteger(item.year) && typeof item.path === 'string' && Number.isInteger(item.count))
        .slice()
        .sort((left, right) => right.year - left.year);
}

function scopeTitle() {
    if (currentScope === 'archive') {
        return activeArchiveYear ? `${activeArchiveYear} 年历史归档` : '历史归档';
    }
    return '最近 90 天';
}

function titleForCurrentView() {
    if (baseView === 'starred') return `${scopeTitle()} · 收藏夹`;
    if (baseView === 'topic:stability') return `${scopeTitle()} · 水动力稳定性`;
    return scopeTitle();
}

function renderSubscriptionStatus() {
    const status = document.getElementById('subscription-status');
    const footer = document.getElementById('last-updated');
    if (!subscriptionIndex) {
        status.textContent = '订阅快照尚未加载。';
        footer.textContent = '';
        return;
    }
    const sources = subscriptionIndex.sources || {};
    const total = Number.isInteger(sources.total) ? sources.total : 0;
    const succeeded = Number.isInteger(sources.succeeded) ? sources.succeeded : 0;
    const failedIds = Array.isArray(sources.failed_ids) ? sources.failed_ids : [];
    const sourceHealth = total > 0 ? `${succeeded}/${total} 个来源成功` : '来源健康信息不可用';
    const generated = subscriptionIndex.generated_at ? new Date(subscriptionIndex.generated_at) : null;
    const generatedText = generated && !Number.isNaN(generated.getTime())
        ? generated.toLocaleString('zh-CN', { hour12: false })
        : '未知时间';
    const cacheText = failedIds.length > 0
        ? `；${failedIds.length} 个来源暂不可用，已沿用该来源上次成功快照`
        : '；所有来源本次均成功读取';
    status.textContent = `生成于 ${generatedText} · canonical 数据镜像 · ${sourceHealth}${cacheText}`;
    status.classList.toggle('degraded', failedIds.length > 0);
    footer.textContent = `数据状态：${status.textContent}`;
}

function renderScopeNavigation() {
    const currentCount = currentPapers.length;
    const historyCount = archiveDescriptors().reduce((total, archive) => total + archive.count, 0);
    document.getElementById('count-archive').textContent = currentCount;
    document.getElementById('count-history').textContent = historyCount;
    const archiveYears = document.getElementById('archive-year-filters');
    archiveYears.replaceChildren();
    archiveDescriptors().forEach(descriptor => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = '#';
        link.className = 'folder-link archive-year-link';
        link.classList.toggle('active', currentScope === 'archive' && String(activeArchiveYear) === String(descriptor.year));
        link.onclick = event => {
            event.preventDefault();
            loadArchiveYear(descriptor.year);
        };
        const name = document.createElement('span');
        name.textContent = `${descriptor.year} 年`;
        const count = document.createElement('span');
        count.className = 'sidebar-count';
        count.textContent = descriptor.count;
        link.append(name, count);
        item.appendChild(link);
        archiveYears.appendChild(item);
    });
}

function renderFilterLists(sourceGroupCounts, journalCounts, monthCounts) {
    const sourceGroupList = document.getElementById('source-group-filters');
    sourceGroupList.replaceChildren();
    JOURNAL_GROUPS.forEach(group => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = '#';
        link.className = 'folder-link';
        link.classList.toggle('active', filterSourceGroup === group.id);
        link.onclick = event => {
            event.preventDefault();
            toggleSourceGroupFilter(group.id);
        };
        const name = document.createElement('span');
        name.textContent = group.label;
        const count = document.createElement('span');
        count.className = 'sidebar-count';
        count.textContent = sourceGroupCounts[group.id];
        link.append(name, count);
        item.appendChild(link);
        sourceGroupList.appendChild(item);
    });

    renderCountedFolderList('journal-filters', Object.keys(journalCounts).sort(), journalCounts, filterJournal, toggleJournalFilter);
    const months = Object.keys(monthCounts).sort((left, right) => right.localeCompare(left, 'zh-CN', { numeric: true }));
    renderCountedFolderList('month-filters', months, monthCounts, filterMonth, toggleMonthFilter);
}

function renderCountedFolderList(elementId, values, counts, selected, toggle) {
    const list = document.getElementById(elementId);
    list.replaceChildren();
    values.forEach(value => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = '#';
        link.className = 'folder-link';
        link.classList.toggle('active', selected === value);
        link.onclick = event => {
            event.preventDefault();
            toggle(value);
        };
        const name = document.createElement('span');
        name.textContent = value;
        const count = document.createElement('span');
        count.className = 'sidebar-count';
        count.textContent = counts[value];
        link.append(name, count);
        item.appendChild(link);
        list.appendChild(item);
    });
}

function addFilterTag(container, label, onClear) {
    const tag = document.createElement('div');
    tag.className = 'filter-tag';
    tag.appendChild(document.createTextNode(label));
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'filter-tag-close';
    close.setAttribute('aria-label', `清除筛选：${label}`);
    close.textContent = '×';
    close.onclick = onClear;
    tag.appendChild(close);
    container.appendChild(tag);
}

function renderFilterTags() {
    const container = document.getElementById('filter-tags-container');
    container.replaceChildren();
    if (filterSourceGroup) {
        const group = JOURNAL_GROUPS.find(item => item.id === filterSourceGroup);
        if (group) addFilterTag(container, group.label, clearSourceGroupFilter);
    }
    if (filterJournal) addFilterTag(container, filterJournal, clearJournalFilter);
    if (filterMonth) addFilterTag(container, filterMonth, clearMonthFilter);
    container.style.display = container.childElementCount > 0 ? 'flex' : 'none';
}

function showMessage(message) {
    const container = document.getElementById('fluids-list-container');
    const paragraph = document.createElement('p');
    paragraph.className = 'status-message';
    paragraph.textContent = message;
    container.replaceChildren(paragraph);
    const markButton = document.getElementById('mark-all-read');
    markButton.style.display = 'none';
}

function renderPaperList(papers, readPapers, starredPapers) {
    const container = document.getElementById('fluids-list-container');
    container.replaceChildren();
    if (papers.length === 0) {
        showMessage('该筛选条件下无文献。');
        return 0;
    }

    const groups = new Map();
    papers.forEach(paper => {
        const month = formatMonth(paper.date);
        if (!groups.has(month)) groups.set(month, []);
        groups.get(month).push(paper);
    });
    let unreadCount = 0;
    Array.from(groups.keys())
        .sort((left, right) => right.localeCompare(left, 'zh-CN', { numeric: true }))
        .forEach(month => {
            const group = document.createElement('div');
            group.className = 'paper-group';
            const heading = document.createElement('h2');
            heading.className = 'paper-group-header';
            heading.textContent = month;
            const list = document.createElement('ul');
            list.className = 'paper-list';
            groups.get(month)
                .slice()
                .sort((left, right) => String(right.date).localeCompare(String(left.date)))
                .forEach(paper => {
                    const identifier = paperKey(paper);
                    const isRead = readPapers.includes(identifier);
                    const isStarred = starredPapers.includes(identifier);
                    if (!isRead) unreadCount += 1;

                    const item = document.createElement('li');
                    const link = document.createElement('a');
                    const archiveQuery = currentScope === 'archive' && activeArchiveYear
                        ? `&year=${encodeURIComponent(activeArchiveYear)}`
                        : '';
                    link.href = 'post.html?id=' + encodeURIComponent(p.id) + archiveQuery;
                    link.className = `paper-link${isRead ? ' read' : ''}`;
                    link.onclick = () => markRead(identifier);

                    const titleRow = document.createElement('div');
                    titleRow.className = 'paper-title-row';
                    const star = document.createElement('button');
                    star.type = 'button';
                    star.className = `paper-star${isStarred ? ' active' : ''}`;
                    star.setAttribute('aria-label', isStarred ? '取消收藏' : '收藏论文');
                    star.textContent = '★';
                    star.onclick = event => toggleStar(event, identifier);
                    const title = document.createElement('span');
                    title.className = 'paper-title';
                    title.textContent = paper.title;
                    const meta = document.createElement('div');
                    meta.className = 'paper-meta';
                    meta.textContent = paper.source + ' · ' + paper.date + ' · ' + paper.authors;
                    titleRow.append(star, title);
                    link.append(titleRow, meta);
                    item.appendChild(link);
                    list.appendChild(item);
                });
            group.append(heading, list);
            container.appendChild(group);
        });
    return unreadCount;
}

function render() {
    const readPapers = getReadPapers();
    const starredPapers = getStarredPapers();
    const topicCounts = { stability: 0 };
    const sourceGroupCounts = {};
    const journalCounts = {};
    const monthCounts = {};
    JOURNAL_GROUPS.forEach(group => { sourceGroupCounts[group.id] = 0; });

    allPapers.forEach(paper => {
        journalCounts[paper.source] = (journalCounts[paper.source] || 0) + 1;
        const sourceGroup = sourceGroupForPaper(paper);
        if (sourceGroup && sourceGroupCounts[sourceGroup] !== undefined) sourceGroupCounts[sourceGroup] += 1;
        const month = formatMonth(paper.date);
        monthCounts[month] = (monthCounts[month] || 0) + 1;
        (paper.tags || []).forEach(tag => {
            if (topicCounts[tag] !== undefined) topicCounts[tag] += 1;
        });
    });

    document.getElementById('count-starred').textContent = starredPapers.length;
    document.getElementById('count-current-view').textContent = allPapers.length;
    document.getElementById('count-stability').textContent = topicCounts.stability;
    document.getElementById('view-title').textContent = titleForCurrentView();
    renderSubscriptionStatus();
    renderScopeNavigation();
    renderFilterLists(sourceGroupCounts, journalCounts, monthCounts);
    renderFilterTags();

    const unreadCount = renderPaperList(getPapersToRender(), readPapers, starredPapers);
    const markButton = document.getElementById('mark-all-read');
    markButton.style.display = unreadCount > 0 ? 'inline-block' : 'none';
}

async function loadCurrentIndex() {
    try {
        const response = await fetch('fluids-index.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const index = await response.json();
        if (!index || !Array.isArray(index.papers) || !index.papers.every(paper => paper && typeof paper.id === 'string')) {
            throw new Error('首页索引不符合 canonical 数据格式');
        }
        subscriptionIndex = index;
        currentPapers = index.papers;
        migrateLegacyLocalState(currentPapers);
        allPapers = currentPapers;
        render();
    } catch (error) {
        console.error(error);
        document.getElementById('subscription-status').textContent = '订阅快照暂时不可用；已保留浏览器中的收藏与已读状态。';
        showMessage('最近 90 天文献索引暂时无法加载。请稍后重试。');
    }
}

document.addEventListener('DOMContentLoaded', loadCurrentIndex);
