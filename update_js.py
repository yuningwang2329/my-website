with open('fluids.html', 'r') as f:
    content = f.read()

import re

# Find the exact script block to replace
start_idx = content.find('<script>')
end_idx = content.find('</script>', start_idx) + len('</script>')
old_script = content[start_idx:end_idx]

new_script = """<script>
        let allPapers = [];
        let baseView = 'archive'; // archive | starred | topic:stability
        let filterJournal = null;
        let filterMonth = null;
        
        function getReadPapers() {
            return JSON.parse(localStorage.getItem('fluids_read') || '[]');
        }
        function getStarredPapers() {
            return JSON.parse(localStorage.getItem('fluids_stars') || '[]');
        }
        
        function markRead(filename) {
            let read = getReadPapers();
            if (!read.includes(filename)) {
                read.push(filename);
                localStorage.setItem('fluids_read', JSON.stringify(read));
            }
        }
        
        function getPapersToRender() {
            let readPapers = getReadPapers();
            let starredPapers = getStarredPapers();
            return allPapers.filter(p => {
                if (baseView === 'starred' && !starredPapers.includes(p.filename)) return false;
                if (baseView.startsWith('topic:') && !(p.tags || []).includes(baseView.replace('topic:', ''))) return false;
                
                if (filterJournal && p.source !== filterJournal) return false;
                if (filterMonth && formatMonth(p.date) !== filterMonth) return false;
                return true;
            });
        }
        
        function markAllRead() {
            let read = getReadPapers();
            let added = false;
            let currentPapers = getPapersToRender();
            
            currentPapers.forEach(p => {
                if (!read.includes(p.filename)) {
                    read.push(p.filename);
                    added = true;
                }
            });
            if (added) {
                localStorage.setItem('fluids_read', JSON.stringify(read));
                render();
            }
        }
        
        function toggleStar(e, filename) {
            e.preventDefault();
            e.stopPropagation();
            let stars = getStarredPapers();
            if (stars.includes(filename)) {
                stars = stars.filter(f => f !== filename);
            } else {
                stars.push(filename);
            }
            localStorage.setItem('fluids_stars', JSON.stringify(stars));
            render();
        }

        function switchFolder(folderId, element) {
            baseView = folderId;
            document.querySelectorAll('#main-folders .folder-link, #topic-folders .folder-link').forEach(el => el.classList.remove('active'));
            if (element) {
                element.classList.add('active');
            }
            
            const titles = { 'starred': '收藏夹', 'archive': '所有文献', 'topic:stability': '水动力稳定性' };
            document.getElementById('view-title').textContent = titles[baseView] || '文献库';
            render();
        }
        
        function toggleJournalFilter(j, element) {
            if (filterJournal === j) {
                filterJournal = null; 
            } else {
                filterJournal = j;
            }
            render();
        }
        
        function clearJournalFilter() {
            filterJournal = null;
            render();
        }
        
        function toggleMonthFilter(m, element) {
            if (filterMonth === m) {
                filterMonth = null; 
            } else {
                filterMonth = m;
            }
            render();
        }
        
        function clearMonthFilter() {
            filterMonth = null;
            render();
        }
        
        function formatMonth(dateStr) {
            var parts = dateStr.split('-');
            return parts[0] + '年' + parseInt(parts[1]) + '月';
        }

        function render() {
            let readPapers = getReadPapers();
            let starredPapers = getStarredPapers();
            
            let starredCount = starredPapers.length;
            let archiveCount = allPapers.length;
            let topicCounts = { 'stability': 0 };
            let journalCounts = {};
            let monthCounts = {};
            
            allPapers.forEach(p => {
                journalCounts[p.source] = (journalCounts[p.source] || 0) + 1;
                
                let m = formatMonth(p.date);
                monthCounts[m] = (monthCounts[m] || 0) + 1;
                
                let tags = p.tags || [];
                tags.forEach(t => {
                    if (topicCounts[t] !== undefined) topicCounts[t]++;
                });
            });
            
            document.getElementById('count-starred').textContent = starredCount;
            document.getElementById('count-archive').textContent = archiveCount;
            document.getElementById('count-stability').textContent = topicCounts['stability'];
            
            let journalList = document.getElementById('journal-filters');
            if (journalList.children.length === 0) {
                let sortedJournals = Object.keys(journalCounts).sort();
                sortedJournals.forEach(j => {
                    let li = document.createElement('li');
                    let a = document.createElement('a');
                    a.href = '#';
                    a.className = 'folder-link';
                    a.onclick = function(e) { e.preventDefault(); toggleJournalFilter(j, this); };
                    
                    let spanName = document.createElement('span');
                    spanName.textContent = j;
                    let spanCount = document.createElement('span');
                    spanCount.className = 'sidebar-count';
                    spanCount.textContent = journalCounts[j];
                    
                    a.appendChild(spanName);
                    a.appendChild(spanCount);
                    li.appendChild(a);
                    journalList.appendChild(li);
                });
            }
            
            let monthList = document.getElementById('month-filters');
            if (monthList.children.length === 0) {
                let sortedMonths = Object.keys(monthCounts).sort((a, b) => {
                    let pa = a.match(/(\d+)年(\d+)月/);
                    let pb = b.match(/(\d+)年(\d+)月/);
                    if (!pa || !pb) return 0;
                    if (pa[1] !== pb[1]) return parseInt(pb[1]) - parseInt(pa[1]);
                    return parseInt(pb[2]) - parseInt(pa[2]);
                });
                sortedMonths.forEach(m => {
                    let li = document.createElement('li');
                    let a = document.createElement('a');
                    a.href = '#';
                    a.className = 'folder-link';
                    a.onclick = function(e) { e.preventDefault(); toggleMonthFilter(m, this); };
                    
                    let spanName = document.createElement('span');
                    spanName.textContent = m;
                    let spanCount = document.createElement('span');
                    spanCount.className = 'sidebar-count';
                    spanCount.textContent = monthCounts[m];
                    
                    a.appendChild(spanName);
                    a.appendChild(spanCount);
                    li.appendChild(a);
                    monthList.appendChild(li);
                });
            }
            
            document.querySelectorAll('#journal-filters .folder-link').forEach(el => {
                el.classList.toggle('active', el.querySelector('span').textContent === filterJournal);
            });
            document.querySelectorAll('#month-filters .folder-link').forEach(el => {
                el.classList.toggle('active', el.querySelector('span').textContent === filterMonth);
            });
            
            let tagsContainer = document.getElementById('filter-tags-container');
            tagsContainer.innerHTML = '';
            if (filterJournal) {
                let tag = document.createElement('div');
                tag.className = 'filter-tag';
                tag.innerHTML = `${filterJournal} <span class="filter-tag-close" onclick="clearJournalFilter()">✕</span>`;
                tagsContainer.appendChild(tag);
            }
            if (filterMonth) {
                let tag = document.createElement('div');
                tag.className = 'filter-tag';
                tag.innerHTML = `${filterMonth} <span class="filter-tag-close" onclick="clearMonthFilter()">✕</span>`;
                tagsContainer.appendChild(tag);
            }

            let papersToRender = getPapersToRender();

            let container = document.getElementById('fluids-list-container');
            container.innerHTML = '';
            
            let markBtn = document.getElementById('mark-all-read');
            if (papersToRender.length === 0) {
                container.innerHTML = '<p style="color:var(--text-secondary);padding:20px 0;">该筛选条件下无文献。</p>';
                if (markBtn) markBtn.style.display = 'none';
                return;
            }
            
            let groups = {};
            let groupOrder = [];
            let unreadInCurrentFolder = 0;
            
            papersToRender.forEach(p => {
                if (!readPapers.includes(p.filename)) unreadInCurrentFolder++;
                
                let month = formatMonth(p.date);
                if (!groups[month]) {
                    groups[month] = [];
                    groupOrder.push(month);
                }
                groups[month].push(p);
            });
            
            groupOrder.forEach(month => {
                let groupDiv = document.createElement('div');
                groupDiv.className = 'paper-group';
                
                let header = document.createElement('h2');
                header.className = 'paper-group-header';
                header.textContent = month;
                groupDiv.appendChild(header);
                
                let ul = document.createElement('ul');
                ul.className = 'paper-list';
                
                groups[month].forEach(p => {
                    let li = document.createElement('li');
                    
                    let isRead = readPapers.includes(p.filename);
                    let isStarred = starredPapers.includes(p.filename);
                    
                    let link = document.createElement('a');
                    link.href = 'post.html?file=fluids/' + p.filename;
                    link.className = 'paper-link' + (isRead ? ' read' : '');
                    link.onclick = function() { markRead(p.filename); };
                    
                    let titleRow = document.createElement('div');
                    titleRow.className = 'paper-title-row';
                    
                    let title = document.createElement('span');
                    title.className = 'paper-title';
                    title.textContent = p.title;
                    
                    let starBtn = document.createElement('button');
                    starBtn.className = 'paper-star' + (isStarred ? ' active' : '');
                    starBtn.innerHTML = '★';
                    starBtn.onclick = function(e) { toggleStar(e, p.filename); };
                    
                    titleRow.appendChild(starBtn);
                    titleRow.appendChild(title);
                    
                    let meta = document.createElement('div');
                    meta.className = 'paper-meta';
                    meta.textContent = p.source + ' · ' + p.date + ' · ' + p.authors;
                    
                    link.appendChild(titleRow);
                    link.appendChild(meta);
                    li.appendChild(link);
                    ul.appendChild(li);
                });
                
                groupDiv.appendChild(ul);
                container.appendChild(groupDiv);
            });
            
            if (markBtn) {
                markBtn.style.display = unreadInCurrentFolder > 0 ? 'inline-block' : 'none';
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            fetch('fluids.json')
                .then(response => {
                    if (!response.ok) throw new Error('网络请求失败');
                    return response.json();
                })
                .then(data => {
                    allPapers = data;
                    render();
                })
                .catch(error => {
                    console.error(error);
                    document.getElementById('fluids-list-container').innerHTML = '<p style="color:var(--text-secondary);padding:20px 0;">加载失败。</p>';
                });
        });
    </script>"""

content = content.replace(old_script, new_script)

with open('fluids.html', 'w') as f:
    f.write(content)

