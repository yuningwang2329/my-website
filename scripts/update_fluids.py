import os
import json
import uuid
import datetime
import urllib.request
import feedparser
import re
from deep_translator import GoogleTranslator

# Constants
JSON_FILE = 'fluids.json'
MD_DIR = 'fluids'

# --- 订阅配置池 (Feeds Config) ---
FEEDS = [
    {
        "name": "Arxiv (math.AP)",
        "url": "http://export.arxiv.org/api/query?search_query=cat:math.AP&sortBy=submittedDate&sortOrder=descending&max_results=5",
        "type": "arxiv"
    },
    {
        "name": "AML",
        "url": "https://rss.sciencedirect.com/publication/science/08939659",
        "type": "standard_rss"
    },
    {
        "name": "ARMA",
        "url": "https://kill-the-newsletter.com/feeds/pwrewx6t1kh3dojlxg99.xml",
        "type": "email_rss"
    }
]

def translate_to_zh(text):
    if not text or len(text.strip()) == 0:
        return "无摘要内容。"
    try:
        translator = GoogleTranslator(source='auto', target='zh-CN')
        if len(text) > 4999:
            text = text[:4999]
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def create_markdown(title, authors, date, source, link, abstract_en, abstract_zh):
    safe_title = "".join([c if c.isalnum() else "-" for c in title])[:40].strip('-')
    if not safe_title:
        safe_title = "paper"
    filename = f"{date}-{safe_title}-{str(uuid.uuid4())[:6]}.md"
    
    filepath = os.path.join(MD_DIR, filename)
    
    md_content = f"""# {title}

- **作者 (Authors)**: {authors}
- **来源 (Source)**: {source}
- **日期 (Date)**: {date}
- **原文链接 (Link)**: [查看原始论文]({link})

## 中文摘要

{abstract_zh}

---

## 英文摘要

{abstract_en}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    return filename

def extract_doi(text):
    match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9a-z]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).rstrip('."\'<>)')
    return None

def query_crossref_by_doi(doi):
    try:
        url = f"https://api.crossref.org/works/{doi}"
        req = urllib.request.Request(url, headers={'User-Agent': 'mailto:test@example.com'})
        res = urllib.request.urlopen(req, timeout=5)
        data = json.loads(res.read())['message']
        title = data.get('title', [''])[0]
        authors = ", ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in data.get('author', [])])
        abstract = data.get('abstract', '')
        # CrossRef XML abstract stripping
        abstract = re.sub(r'<[^>]+>', '', abstract)
        return title, authors, abstract
    except Exception:
        return None, None, None

def query_crossref_by_title(title):
    try:
        safe_title = urllib.parse.quote(title)
        url = f"https://api.crossref.org/works?query.title={safe_title}&select=DOI,title,author,abstract&rows=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'mailto:test@example.com'})
        res = urllib.request.urlopen(req, timeout=5)
        data = json.loads(res.read())['message']['items']
        if not data:
            return None, None, None
        item = data[0]
        cr_title = item.get('title', [''])[0]
        authors = ", ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get('author', [])])
        abstract = item.get('abstract', '')
        abstract = re.sub(r'<[^>]+>', '', abstract)
        return cr_title, authors, abstract
    except Exception:
        return None, None, None

def fetch_feed(feed_config):
    papers = []
    source_name = feed_config['name']
    f_type = feed_config['type']
    url = feed_config['url']
    
    print(f"Fetching {source_name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=15)
        feed = feedparser.parse(res.read())
        
        for entry in feed.entries[:5]: # Limit to 5 per feed per run to save time
            title = entry.get('title', '').replace('\n', ' ').strip()
            link = entry.get('link', '')
            summary = entry.get('summary', entry.get('description', ''))
            date_str = ""
            
            if 'published_parsed' in entry and entry.published_parsed:
                date_str = f"{entry.published_parsed.tm_year}-{entry.published_parsed.tm_mon:02d}-{entry.published_parsed.tm_mday:02d}"
            else:
                date_str = datetime.datetime.now().strftime("%Y-%m-%d")

            authors = ""
            abstract_en = ""
            
            if f_type == "arxiv":
                authors = ", ".join(author.name for author in entry.get('authors', []))
                abstract_en = summary.replace('\n', ' ')
            
            elif f_type == "standard_rss":
                # AML etc. Usually don't have abstract. Try CrossRef by Title
                cr_title, cr_auth, cr_abs = query_crossref_by_title(title)
                authors = cr_auth if cr_auth else "见原链接 (See link)"
                abstract_en = cr_abs if cr_abs else "无摘要提供，请点击原文链接查看。"
                if not cr_abs:
                    clean_summary = re.sub(r'<[^>]+>', ' ', summary)
                    abstract_en = clean_summary[:1000]

            elif f_type == "email_rss":
                # Email RSS (ARMA). Real info is inside HTML content.
                content = ""
                if 'content' in entry:
                    content = entry.content[0].value
                else:
                    content = summary
                
                doi = extract_doi(content)
                if doi:
                    cr_title, cr_auth, cr_abs = query_crossref_by_doi(doi)
                    if cr_title:
                        title = cr_title
                    authors = cr_auth if cr_auth else "见原链接 (See link)"
                    abstract_en = cr_abs if cr_abs else "摘要提取失败，请点击原文链接查看。"
                    link = f"https://doi.org/{doi}"
                else:
                    clean_text = re.sub(r'<[^>]+>', ' ', content)
                    abstract_en = clean_text[:2000]
                    authors = "Email Sender"
            
            if not title or "ToC Alert" in title or "Table of Contents" in title:
                continue
                
            papers.append({
                'title': title,
                'authors': authors,
                'date': date_str,
                'source': source_name,
                'link': link,
                'abstract_en': abstract_en
            })
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
        
    return papers

def main():
    if not os.path.exists(MD_DIR):
        os.makedirs(MD_DIR)

    existing_papers = []
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                existing_papers = json.load(f)
        except:
            pass

    existing_titles = {p['title'].strip().lower() for p in existing_papers}
    
    new_papers_data = []
    all_fetched = []
    
    for feed_conf in FEEDS:
        all_fetched.extend(fetch_feed(feed_conf))
        
    for p in all_fetched:
        compare_title = p['title'].strip().lower()
        if compare_title not in existing_titles:
            print(f"-> 发现新论文: {p['title'][:50]}...")
            abstract_zh = translate_to_zh(p['abstract_en'])
            
            filename = create_markdown(p['title'], p['authors'], p['date'], p['source'], p['link'], p['abstract_en'], abstract_zh)
            
            new_papers_data.append({
                'title': p['title'],
                'authors': p['authors'],
                'date': p['date'],
                'source': p['source'],
                'filename': filename
            })
            existing_titles.add(compare_title)

    if new_papers_data:
        all_papers = new_papers_data + existing_papers
        all_papers.sort(key=lambda x: x['date'], reverse=True)
        
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_papers, f, ensure_ascii=False, indent=4)
        print(f"✅ 更新完成。新增了 {len(new_papers_data)} 篇论文。")
    else:
        print("ℹ️ 没有发现新论文。")

if __name__ == "__main__":
    main()
