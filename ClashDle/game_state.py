import json
import random
import os

class GameState:
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        try:
            with open(os.path.join(base_dir, 'cards.json'), 'r', encoding='utf-8') as f:
                self.cards = json.load(f)
        except Exception as e:
            print(f"Failed to load cards: {e}")
            self.cards = []
            
        # target_card stores the card we need to guess
        self.target_card = None
        self.guesses = []
        self.won = False
        
    def start_game(self):
        if self.cards:
            self.target_card = random.choice(self.cards)
        self.guesses = []
        self.won = False
        
    def get_card_by_name(self, name):
        for c in self.cards:
            if c['name'].lower() == name.lower():
                return c
        return None

    def make_guess(self, card_name):
        c = self.get_card_by_name(card_name)
        if c and c not in self.guesses:
            # We insert at the beginning so the newest guess is at the top
            self.guesses.insert(0, c)
            if c['key'] == self.target_card['key']:
                self.won = True
            return True
        return False
        
    def is_guess_correct(self, card, attribute):
        """Returns comparison result for UI rendering"""
        if attribute == 'elixir' or attribute == 'arena':
            target_val = self.target_card.get(attribute, 0)
            guess_val = card.get(attribute, 0)
            if guess_val == target_val:
                return 'match'
            return 'higher' if target_val > guess_val else 'lower'
        else:
            return 'match' if card.get(attribute) == self.target_card.get(attribute) else 'wrong'
