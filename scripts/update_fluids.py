import os
import json
import uuid
import datetime
import time
import urllib.request
import feedparser
import re
from deep_translator import GoogleTranslator

# Constants
JSON_FILE = 'fluids.json'
MD_DIR = 'fluids'

LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1") # Defaulting to SiliconFlow as an example
LLM_MODEL = os.environ.get("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct") # Fast cheap model

def ai_paper_filter(title, abstract):
    fallback_keywords = [
        'fluid', 'navier', 'euler', 'hydrodynamic', 'mhd', 'magnetohydrodynamic',
        'boussinesq', 'water wave', 'boundary layer', 'compressible', 'incompressible',
        'vortex', 'vorticity', 'plasma', 'boltzmann', 'viscous', 'inviscid',
        'burgers', 'korteweg', 'stokes', 'capillary', 'convection', 'turbulence', 'shallow water',
        'dispersive', 'blow-up', 'blow up', 'well-posedness', 'operator', 'kdv', 'vlasov',
        'schrodinger', 'schrödinger', 'dongyi wei', 'camassa', 'fluid-structure'
    ]
    text = (title + " " + abstract).lower()
    
    if not LLM_API_KEY:
        return any(kw in text for kw in fallback_keywords)
        
    try:
        url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }
        system_prompt = "You are a strict expert in fluid dynamics and PDEs. Does this paper belong to fluid mechanics, or abstract mathematics explicitly motivated by fluid mechanics (e.g., Navier-Stokes, Euler, fluid-related dispersive/parabolic equations, or fluid-related operator theory like Dongyi Wei's work)? Note: General operator theory, pure geometry, relativity, or unrelated PDEs must be 'NO'. Answer ONLY 'YES' or 'NO'."
        user_prompt = f"Title: {title}\nAbstract: {abstract}"
        data = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 10
        }
        req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode('utf-8'))
        res = urllib.request.urlopen(req, timeout=15)
        res_data = json.loads(res.read().decode('utf-8'))
        answer = res_data['choices'][0]['message']['content'].strip().upper()
        time.sleep(2) # rate limit prevention
        return "YES" in answer
    except Exception as e:
        print(f"AI Filter Error: {e}. Using fallback.")
        return any(kw in text for kw in fallback_keywords)


# --- 订阅配置池 (Feeds Config) ---
FEEDS = [
    {
        "name": "Arxiv (math.AP)",
        "url": "http://export.arxiv.org/api/query?search_query=cat:math.AP&sortBy=submittedDate&sortOrder=descending&max_results=5",
        "type": "arxiv"
    },
    {
        "name": "Appl. Math. Lett.",
        "url": "https://rss.sciencedirect.com/publication/science/08939659",
        "type": "standard_rss"
    },
    {
        "name": "Arch. Ration. Mech. Anal.",
        "url": "1432-0673",
        "type": "crossref_journal"
    },
    {
        "name": "Commun. Math. Phys.",
        "url": "1432-0916",
        "type": "crossref_journal"
    },
    {
        "name": "Commun. Pure Appl. Math.",
        "url": "https://onlinelibrary.wiley.com/action/showFeed?type=etoc&feed=rss&jc=10970312",
        "type": "standard_rss"
    },
    {
        "name": "Calc. Var. Partial Differ. Equ.",
        "url": "1432-0835",
        "type": "crossref_journal"
    },
    {
        "name": "J. Differ. Equ.",
        "url": "https://rss.sciencedirect.com/publication/science/00220396",
        "type": "standard_rss"
    },
    {
        "name": "J. Funct. Anal.",
        "url": "https://rss.sciencedirect.com/publication/science/00221236",
        "type": "standard_rss"
    },
    {
        "name": "SIAM J. Math. Anal.",
        "url": "https://epubs.siam.org/action/showFeed?type=etoc&feed=rss&jc=sjmaah",
        "type": "standard_rss"
    },
    {
        "name": "J. Math. Pures Appl.",
        "url": "https://rss.sciencedirect.com/publication/science/00217824",
        "type": "standard_rss"
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

def extract_all_dois(text):
    dois = re.findall(r'(10\.\d{4,9}/[-._;()/:A-Z0-9a-z]+)', text, re.IGNORECASE)
    # Deduplicate and clean up
    cleaned = []
    seen = set()
    for d in dois:
        d = d.rstrip('."\'<>)')
        if d.lower() not in seen:
            seen.add(d.lower())
            cleaned.append(d)
    return cleaned

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
    if f_type == "crossref_journal":
        try:
            cr_url = f"https://api.crossref.org/journals/{url}/works?sort=published&order=desc&rows=5"
            cr_req = urllib.request.Request(cr_url, headers={'User-Agent': 'mailto:test@example.com'})
            cr_res = urllib.request.urlopen(cr_req, timeout=15)
            data = json.loads(cr_res.read())['message']['items']
            for item in data:
                cr_title = item.get('title', [''])[0]
                cr_authors = ", ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get('author', [])])
                cr_abs = item.get('abstract', '')
                cr_abs = re.sub(r'<[^>]+>', '', cr_abs)
                cr_doi = item.get('DOI', '')
                
                date_parts = item.get('published', item.get('created', {})).get('date-parts', [[datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day]])[0]
                if len(date_parts) >= 3:
                    date_str = f"{date_parts[0]}-{date_parts[1]:02d}-{date_parts[2]:02d}"
                elif len(date_parts) == 2:
                    date_str = f"{date_parts[0]}-{date_parts[1]:02d}-01"
                else:
                    date_str = f"{date_parts[0]}-01-01"
                    
                papers.append({
                    'title': cr_title, 'authors': cr_authors, 'date': date_str,
                    'source': source_name, 'link': f"https://doi.org/{cr_doi}", 'abstract_en': cr_abs
                })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
    else:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, timeout=15)
            feed = feedparser.parse(res.read())
            
            for entry in feed.entries[:5]: # Limit parsing to save time
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
                    papers.append({
                        'title': title, 'authors': authors, 'date': date_str,
                        'source': source_name, 'link': link, 'abstract_en': abstract_en
                    })
                
                elif f_type == "standard_rss":
                    # AML etc. Usually don't have abstract. Try CrossRef by Title
                    cr_title, cr_auth, cr_abs = query_crossref_by_title(title)
                    authors = cr_auth if cr_auth else "见原链接 (See link)"
                    abstract_en = cr_abs if cr_abs else "无摘要提供，请点击原文链接查看。"
                    if not cr_abs:
                        clean_summary = re.sub(r'<[^>]+>', ' ', summary)
                        abstract_en = clean_summary[:1000]
                    papers.append({
                        'title': cr_title if cr_title else title, 
                        'authors': authors, 'date': date_str,
                        'source': source_name, 'link': link, 'abstract_en': abstract_en
                    })

                elif f_type == "email_rss":
                    # Email RSS
                    content = ""
                    if 'content' in entry:
                        content = entry.content[0].value
                    else:
                        content = summary
                    
                    dois = extract_all_dois(content)[:10] # limit to 10 DOIs per email
                    if dois:
                        for doi in dois:
                            cr_title, cr_auth, cr_abs = query_crossref_by_doi(doi)
                            if cr_title:
                                papers.append({
                                    'title': cr_title,
                                    'authors': cr_auth if cr_auth else "见原链接 (See link)",
                                    'date': date_str,
                                    'source': source_name,
                                    'link': f"https://doi.org/{doi}",
                                    'abstract_en': cr_abs if cr_abs else "摘要提取失败，请点击原文链接查看。"
                                })
                    else:
                        if not title or "ToC Alert" in title or "Table of Contents" in title:
                            continue
                        clean_text = re.sub(r'<[^>]+>', ' ', content)
                        papers.append({
                            'title': title, 'authors': "Email Sender", 'date': date_str,
                            'source': source_name, 'link': link, 'abstract_en': clean_text[:2000]
                        })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            
    filtered_papers = []
    for p in papers:
        if ai_paper_filter(p['title'], p['abstract_en']):
            filtered_papers.append(p)
        else:
            print(f"Skipped (AI/Keyword filter): {p['title'][:50]}...")
    return filtered_papers

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
