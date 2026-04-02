import json
import os

remove_keys = [
    "super-witch",
    "super-lava-hound",
    "super-magic-archer",
    "santa-hog-rider",
    "super-ice-golem",
    "super-archers",
    "terry",
    "super-mini-pekka",
    "raging-prince",
    "party-rocket",
    "party-hut"
]

def clean_cards():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, 'cards.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)
        
    filtered = []
    for c in cards:
        if c['key'] in remove_keys:
            continue
            
        # Fix names with parentheses like "Bola de Neve Gigante (Bola de Neve)"
        if "(" in c['name'] and ")" in c['name']:
            c['name'] = c['name'].split(" (")[0]
            
        filtered.append(c)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=4)
        
    print(f"Limpou e filtrou cartas. Sobraram {len(filtered)} cartas legítimas.")

if __name__ == "__main__":
    clean_cards()
