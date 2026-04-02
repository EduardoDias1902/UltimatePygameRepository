import os
import json
import urllib.request

DATA_URL = "https://royaleapi.github.io/cr-api-data/json/cards.json"
ASSET_URL_TEMPLATE = "https://royaleapi.github.io/cr-api-assets/cards/{}.png"

def main():
    print("Downloading cards data...")
    try:
        response = urllib.request.urlopen(DATA_URL)
        data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    # Filter out tower troops and evolved cards for the standard guess list if preferred
    # But for now, let's keep it simple: filter only cards that have the 'id' field, and are not just sub-spells.
    # Actually, RoyaleAPI cards.json mostly contains playable cards. Evolved cards have 'is_evolved': True
    valid_cards = [c for c in data if not c.get('is_evolved', False)]
    
    # Check if assets dir exists
    os.makedirs('assets/cards', exist_ok=True)
    
    # Save the local copy of the list
    local_data = []
    
    for card in valid_cards:
        key = card.get('key')
        name = card.get('name')
        if not key or not name:
            continue
            
        elixir = card.get('elixir', 0)
        rarity = card.get('rarity', 'Common')
        ctype = card.get('type', 'Troop')
        arena = card.get('arena', 0)
        
        local_data.append({
            'key': key,
            'name': name,
            'elixir': elixir,
            'rarity': rarity,
            'type': ctype,
            'arena': arena
        })
        
        # Download image
        img_path = f"assets/cards/{key}.png"
        img_url = ASSET_URL_TEMPLATE.format(key)
        
        if not os.path.exists(img_path):
            print(f"Downloading image for {name} ({key})...")
            try:
                urllib.request.urlretrieve(img_url, img_path)
            except Exception as e:
                print(f"Failed to download image for {key}: {e}")
                
    with open('cards.json', 'w', encoding='utf-8') as f:
        json.dump(local_data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully processed {len(local_data)} cards!")

if __name__ == "__main__":
    main()
