import os
import json
import re
import time
import urllib.request

JSON_FILE = 'fluids.json'
MD_DIR = 'fluids'

LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")

def extract_abstract_from_md(filename):
    """Extract English abstract from a markdown file as fallback."""
    filepath = os.path.join(MD_DIR, filename)
    if not os.path.exists(filepath):
        return ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'## 英文摘要\s*\n+(.*)', content, re.DOTALL)
        if match:
            abstract = match.group(1).strip()
            if abstract and '无摘要提供' not in abstract:
                return abstract
    except Exception:
        pass
    return ""

def ai_paper_filter(title, abstract):
    if not LLM_API_KEY:
        print("No LLM_API_KEY found, skipping filter.")
        return True
        
    try:
        url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }
        system_prompt = """You are a strict expert in fluid dynamics and PDEs. Classify whether this paper belongs to fluid mechanics or closely related mathematical analysis.

ACCEPT: Navier-Stokes, Euler equations (fluid), Boltzmann (kinetic theory of gases), MHD, Boussinesq, water waves, KdV, Camassa-Holm, thin-film equations, boundary layers, vortex dynamics, compressible/incompressible flow, fluid-structure interaction, dispersive PDEs motivated by fluids, operator theory in hydrodynamic stability (e.g. Dongyi Wei's work).

REJECT: algebraic geometry blow-ups, quantum information Schrödinger, general relativity (Einstein/FLRW), number theory, Riemannian geometry, biofilm/ecology/epidemiology models, elastic wave propagation, stochastic gradient descent, machine learning, Calabi-Yau, SIR models, K-theory, groupoid homology.

Answer ONLY 'YES' or 'NO'."""
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
        print(f"AI Filter Error: {e}")
        return True # On error, keep it

def main():
    if not os.path.exists(JSON_FILE):
        print("No fluids.json found.")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    if not LLM_API_KEY:
        print("Error: LLM_API_KEY is not set. Cannot run sweep.")
        return

    print(f"Starting sweep of {len(papers)} papers...")
    kept_papers = []
    removed_count = 0

    for i, p in enumerate(papers):
        title = p.get('title', '')
        abstract = p.get('abstract_en', '') or ''
        
        # Fallback: extract abstract from markdown file if not in JSON
        if not abstract or '无摘要提供' in abstract:
            filename = p.get('filename', '')
            if filename:
                abstract = extract_abstract_from_md(filename)
        
        print(f"[{i+1}/{len(papers)}] Checking: {title[:60]}...")
        
        if ai_paper_filter(title, abstract):
            kept_papers.append(p)
        else:
            removed_count += 1
            print(f"  -> 🚫 REJECTED. Removing.")
            filename = p.get('filename')
            if filename:
                filepath = os.path.join(MD_DIR, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)

    if removed_count > 0:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(kept_papers, f, ensure_ascii=False, indent=4)
        print(f"✅ Sweep complete. Removed {removed_count} unrelated papers.")
    else:
        print("ℹ️ Sweep complete. All papers were deemed relevant!")

if __name__ == "__main__":
    main()
