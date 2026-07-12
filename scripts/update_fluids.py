import os
import json
import uuid
import datetime
import urllib.request
import feedparser
from deep_translator import GoogleTranslator
from imap_tools import MailBox, AND

# Constants
JSON_FILE = 'fluids.json'
MD_DIR = 'fluids'

# Email Config
# 用户需要在 GitHub Secrets 中配置 EMAIL_USER 和 EMAIL_PASS
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'imap.qq.com') # 默认QQ邮箱，可根据情况在 Secrets 配置
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

def translate_to_zh(text):
    try:
        translator = GoogleTranslator(source='auto', target='zh-CN')
        # 简单截断处理超长文本
        if len(text) > 4999:
            text = text[:4999]
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def create_markdown(title, authors, date, source, link, abstract_en, abstract_zh):
    # Sanitize title for filename
    safe_title = "".join([c if c.isalnum() else "-" for c in title])[:30].strip('-')
    filename = f"{date}-{safe_title}-{str(uuid.uuid4())[:6]}.md"
    
    filepath = os.path.join(MD_DIR, filename)
    
    md_content = f"""# {title}

**作者 (Authors)**: {authors}
**来源 (Source)**: {source}
**日期 (Date)**: {date}
**原文链接 (Link)**: [查看原始论文]({link})

## 中文摘要

{abstract_zh}

---

## 英文摘要

{abstract_en}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return filename

def get_arxiv_papers():
    # 抓取 math.AP
    url = "http://export.arxiv.org/api/query?search_query=cat:math.AP&sortBy=submittedDate&sortOrder=descending&max_results=5"
    papers = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            date_str = entry.published[:10]
            title = entry.title.replace('\n', ' ')
            authors = ", ".join(author.name for author in entry.authors)
            abstract_en = entry.summary.replace('\n', ' ')
            link = entry.link
            
            papers.append({
                'title': title,
                'authors': authors,
                'date': date_str,
                'source': 'Arxiv (math.AP)',
                'link': link,
                'abstract_en': abstract_en
            })
    except Exception as e:
        print(f"Arxiv Fetch Error: {e}")
    return papers

def get_email_papers():
    papers = []
    if not EMAIL_USER or not EMAIL_PASS:
        print("未提供邮箱凭据 EMAIL_USER/EMAIL_PASS。跳过邮件解析。")
        return papers
    
    print(f"Connecting to IMAP {EMAIL_HOST} with {EMAIL_USER}...")
    try:
        with MailBox(EMAIL_HOST).login(EMAIL_USER, EMAIL_PASS) as mailbox:
            # 获取所有未读邮件
            for msg in mailbox.fetch(AND(seen=False)):
                date_str = msg.date.strftime("%Y-%m-%d")
                title = msg.subject
                
                # 简单粗暴地提取正文作为摘要（针对推送邮件）
                # 实际应用中可能需要针对不同期刊（如JFM, PoF）的 HTML 结构用 BeautifulSoup 做解析
                abstract_en = msg.text[:3000] if msg.text else "请查看原邮件。暂无法提取纯文本。"
                if not msg.text and msg.html:
                    abstract_en = msg.html[:3000]
                
                papers.append({
                    'title': title,
                    'authors': msg.from_,
                    'date': date_str,
                    'source': 'Email Subscription',
                    'link': '#',
                    'abstract_en': abstract_en
                })
    except Exception as e:
        print(f"IMAP Error: {e}")
        
    return papers

def main():
    if not os.path.exists(MD_DIR):
        os.makedirs(MD_DIR)

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            existing_papers = json.load(f)
    else:
        existing_papers = []

    # 去重判定：根据标题
    existing_titles = {p['title'] for p in existing_papers}
    
    new_papers_data = []
    
    print("Fetching Arxiv...")
    arxiv_papers = get_arxiv_papers()
    
    print("Fetching Emails...")
    email_papers = get_email_papers()
    
    all_fetched = arxiv_papers + email_papers
    
    for p in all_fetched:
        if p['title'] not in existing_titles:
            print(f"-> 发现新论文: {p['title'][:50]}...")
            abstract_zh = translate_to_zh(p['abstract_en'])
            
            filename = create_markdown(p['title'], p['authors'], p['date'], p['source'], p['link'], p['abstract_en'], abstract_zh)
            
            new_item = {
                'title': p['title'],
                'authors': p['authors'],
                'date': p['date'],
                'source': p['source'],
                'filename': filename
            }
            new_papers_data.append(new_item)
            existing_titles.add(p['title'])

    if new_papers_data:
        all_papers = new_papers_data + existing_papers
        # 按照日期倒序排序
        all_papers.sort(key=lambda x: x['date'], reverse=True)
        
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_papers, f, ensure_ascii=False, indent=4)
        print(f"✅ 更新完成。新增了 {len(new_papers_data)} 篇论文。")
    else:
        print("ℹ️ 没有发现新论文。")

if __name__ == "__main__":
    main()
