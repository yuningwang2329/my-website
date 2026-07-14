import json
import os
import datetime

def generate_activity():
    activity = {}
    
    # 1. Parse fluids.json
    try:
        with open('fluids.json', 'r', encoding='utf-8') as f:
            fluids_data = json.load(f)
            
        for p in fluids_data:
            date = p.get('date')
            if date:
                if date not in activity:
                    activity[date] = {'papers': 0, 'notes': 0, 'details': {'papers': [], 'notes': []}}
                activity[date]['papers'] += 1
                activity[date]['details']['papers'].append(p.get('title', 'Unknown Paper'))
    except FileNotFoundError:
        print("fluids.json not found.")

    # 2. Parse notes directory
    notes_dir = 'notes'
    if os.path.exists(notes_dir):
        for filename in os.listdir(notes_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(notes_dir, filename)
                mtime = os.path.getmtime(filepath)
                date = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                
                # Get title from h1
                title = filename.replace('.md', '')
                try:
                    with open(filepath, 'r', encoding='utf-8') as nf:
                        for line in nf:
                            if line.startswith('# '):
                                title = line[2:].strip()
                                break
                except:
                    pass
                
                if date not in activity:
                    activity[date] = {'papers': 0, 'notes': 0, 'details': {'papers': [], 'notes': []}}
                activity[date]['notes'] += 1
                activity[date]['details']['notes'].append(title)

    # 3. Write to activity.json
    with open('activity.json', 'w', encoding='utf-8') as f:
        json.dump(activity, f, ensure_ascii=False, indent=2)
    
    print(f"Generated activity.json with {len(activity)} active days.")

if __name__ == '__main__':
    generate_activity()
