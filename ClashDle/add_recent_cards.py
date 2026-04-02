import json
import os
import urllib.request

new_cards = [
    {
        "key": "void",
        "name": "Vazio",
        "elixir": 3,
        "rarity": "Epic",
        "type": "Spell",
        "arena": 15
    },
    {
        "key": "suspicious-bush",
        "name": "Arbusto Suspeito",
        "elixir": 2,
        "rarity": "Rare",
        "type": "Troop",
        "arena": 13
    },
    {
        "key": "goblin-curse",
        "name": "Maldição Goblin",
        "elixir": 2,
        "rarity": "Epic",
        "type": "Spell",
        "arena": 9
    },
    {
        "key": "goblin-machine",
        "name": "Máquina Goblin",
        "elixir": 5,
        "rarity": "Legendary",
        "type": "Troop",
        "arena": 9
    },
    {
        "key": "goblin-demolisher",
        "name": "Demolidor Goblin",
        "elixir": 4,
        "rarity": "Rare",
        "type": "Troop",
        "arena": 9
    },
    {
        "key": "little-prince",
        "name": "Pequeno Príncipe",
        "elixir": 3,
        "rarity": "Champion",
        "type": "Troop",
        "arena": 11
    }
]

def add_missing_cards():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, 'cards.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)
        
    existing_keys = {c['key'] for c in cards}
    
    for nc in new_cards:
        if nc['key'] not in existing_keys:
            cards.append(nc)
            
            # Tentar baixar a imagem da Royale API, mesmo que possa não existir ainda
            img_url = f"https://royaleapi.github.io/cr-api-assets/cards/{nc['key']}.png"
            img_path = os.path.join(base_dir, f"assets/cards/{nc['key']}.png")
            try:
                urllib.request.urlretrieve(img_url, img_path)
                print(f"Baixou imagem para: {nc['name']}")
            except:
                print(f"Imagem não encontrada na API para: {nc['name']} (usará placeholder)")
            
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=4)
        
    print("Atualizado com as cartas novas que não existiam na base pública do RoyaleAPI!")

if __name__ == '__main__':
    add_missing_cards()
