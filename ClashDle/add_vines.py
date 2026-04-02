import json
import os
import urllib.request

vines_card = {
    "key": "vines",
    "name": "Vinhas",
    "elixir": 3,
    "rarity": "Epic",
    "type": "Spell",
    "arena": 8
}

def add_vines():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, 'cards.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)
        
    existing_keys = {c['key'] for c in cards}
    
    if vines_card['key'] not in existing_keys:
        cards.append(vines_card)
        
        # Tentar baixar a imagem 
        img_url = f"https://royaleapi.github.io/cr-api-assets/cards/vines.png"
        img_path = os.path.join(base_dir, f"assets/cards/vines.png")
        try:
            urllib.request.urlretrieve(img_url, img_path)
            print("Baixou imagem para: Vinhas")
        except:
            print("Imagem não encontrada na API para: Vinhas (usará placeholder)")
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cards, f, ensure_ascii=False, indent=4)
            
        print("Carta Vinhas adicionada com sucesso!")
    else:
        print("Carta Vinhas já existe.")

if __name__ == '__main__':
    add_vines()
