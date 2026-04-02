import pygame
import os

# Constants and Colors
BG_COLOR = (15, 23, 42)
BOX_BG = (30, 41, 59)
TEXT_COLOR = (248, 250, 252)
GREEN_MATCH = (34, 197, 94)
RED_WRONG = (239, 68, 68)
HOVER_COLOR = (51, 65, 85)

class Button:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.hovered = False

    def draw(self, screen):
        color = HOVER_COLOR if self.hovered else BOX_BG
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 116, 139), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                return True
        return False

class SearchBar:
    def __init__(self, x, y, w, h, font, game_state):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.game_state = game_state
        self.text = ''
        self.active = False
        self.suggestions = []
        self.selected_suggestion = 0
        
    def _update_suggestions(self):
        if not self.text:
            self.suggestions = []
            return
        # Find matches ignoring case and not already guessed
        guessed_names = [c['name'].lower() for c in self.game_state.guesses]
        matches = [c for c in self.game_state.cards 
                   if self.text.lower() in c['name'].lower() and c['name'].lower() not in guessed_names]
        self.suggestions = matches[:5]
        self.selected_suggestion = 0

    def draw(self, screen):
        color = HOVER_COLOR if self.active else BOX_BG
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (148, 163, 184), self.rect, 2, border_radius=5)
        
        txt_surface = self.font.render(self.text + ('|' if self.active else ''), True, TEXT_COLOR)
        screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + (self.rect.h - txt_surface.get_height()) // 2))
        
        # Draw suggestions
        if self.active and self.suggestions:
            sugg_y = self.rect.bottom
            for i, sugg_card in enumerate(self.suggestions):
                sugg_rect = pygame.Rect(self.rect.x, sugg_y, self.rect.w, 40)
                bg_color = (71, 85, 105) if i == self.selected_suggestion else BOX_BG
                pygame.draw.rect(screen, bg_color, sugg_rect)
                pygame.draw.rect(screen, (100, 116, 139), sugg_rect, 1)
                
                # Draw small image
                img = get_card_image(sugg_card['key'], (25, 30))
                screen.blit(img, (sugg_rect.x + 5, sugg_rect.y + 5))
                
                sugg_surf = self.font.render(sugg_card['name'], True, TEXT_COLOR)
                screen.blit(sugg_surf, (sugg_rect.x + 40, sugg_rect.y + (40 - sugg_surf.get_height()) // 2))
                sugg_y += 40

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
                
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.suggestions:
                    guess = self.suggestions[self.selected_suggestion]['name']
                    res = self.game_state.make_guess(guess)
                    if res:
                        self.text = ''
                        self._update_suggestions()
                        return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self._update_suggestions()
            elif event.key == pygame.K_DOWN:
                self.selected_suggestion = min(self.selected_suggestion + 1, len(self.suggestions) - 1)
            elif event.key == pygame.K_UP:
                self.selected_suggestion = max(self.selected_suggestion - 1, 0)
            elif event.unicode.isprintable():
                self.text += event.unicode
                self._update_suggestions()
        return False

image_cache = {}

def get_card_image(key, size=(60, 72)):
    cache_key = f"{key}_{size[0]}x{size[1]}"
    if cache_key not in image_cache:
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, f"assets/cards/{key}.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            image_cache[cache_key] = pygame.transform.smoothscale(img, size)
        else:
            surf = pygame.Surface(size)
            surf.fill((100,100,100))
            image_cache[cache_key] = surf
    return image_cache[cache_key]

def draw_guess_row(screen, font, game_state, guess_card, x, y):
    col_width = 110
    h = 80
    bg_color = BOX_BG
    
    img = get_card_image(guess_card['key'])
    screen.blit(img, (x, y + 4))
    
    # Header format: Image | Name | Rarity | Elixir | Type | Arena
    attrs = [
        ('name', guess_card['name']),
        ('rarity', guess_card['rarity']),
        ('elixir', str(guess_card['elixir'])),
        ('type', guess_card['type']),
        ('arena', str(guess_card['arena']))
    ]
    
    TRANSLATIONS = {
        'Common': 'Comum',
        'Rare': 'Raro',
        'Epic': 'Épico',
        'Legendary': 'Lendário',
        'Champion': 'Campeão',
        'Troop': 'Tropa',
        'Spell': 'Feitiço',
        'Building': 'Construção'
    }

    curr_x = x + 70
    for attr, val in attrs:
        display_val = TRANSLATIONS.get(val, val)
        box_rect = pygame.Rect(curr_x, y, col_width - 5, h)
        if attr == 'name':
            pygame.draw.rect(screen, bg_color, box_rect)
        else:
            match = game_state.is_guess_correct(guess_card, attr)
            if match == 'match':
                pygame.draw.rect(screen, GREEN_MATCH, box_rect)
            else:
                pygame.draw.rect(screen, RED_WRONG, box_rect)
            
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 1)
        
        # Fit text into box
        txt_surf = font.render(display_val, True, TEXT_COLOR)
        # scale down if too wide
        if txt_surf.get_width() > box_rect.width - 10:
            scale_factor = (box_rect.width - 10) / txt_surf.get_width()
            txt_surf = pygame.transform.smoothscale(txt_surf, (box_rect.width - 10, int(txt_surf.get_height() * scale_factor)))
            
        txt_rect = txt_surf.get_rect(center=box_rect.center)
        screen.blit(txt_surf, txt_rect)
        
        # Up/Down Arrows
        if attr in ('elixir', 'arena'):
            match = game_state.is_guess_correct(guess_card, attr)
            if match == 'higher':
                pygame.draw.polygon(screen, TEXT_COLOR, [
                    (box_rect.centerx, box_rect.top + 5),
                    (box_rect.centerx - 10, box_rect.top + 15),
                    (box_rect.centerx + 10, box_rect.top + 15)
                ])
            elif match == 'lower':
                pygame.draw.polygon(screen, TEXT_COLOR, [
                    (box_rect.centerx, box_rect.bottom - 5),
                    (box_rect.centerx - 10, box_rect.bottom - 15),
                    (box_rect.centerx + 10, box_rect.bottom - 15)
                ])

        curr_x += col_width
