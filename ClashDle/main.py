import pygame
import sys
from game_state import GameState
from ui_components import Button, SearchBar, draw_guess_row, BG_COLOR, TEXT_COLOR, get_card_image

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ClashDle Pygame - Matched Clone")

# Try to load a nice font, fallback to default font
try:
    font_title = pygame.font.SysFont("Verdana", 54, bold=True)
    font_large = pygame.font.SysFont("Verdana", 32)
    font_small = pygame.font.SysFont("Verdana", 16)
except:
    font_title = pygame.font.Font(None, 64)
    font_large = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)

game_state = GameState()

# UI Assets
btn_classic = Button(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 60, "Modo Clássico", font_large)
btn_artwork = Button(WIDTH//2 - 150, HEIGHT//2 + 30, 300, 60, "Modo Arte", font_large)
btn_menu = Button(20, 20, 100, 40, "Menu", font_small)
btn_reset = Button(WIDTH - 290, 20, 100, 40, "Resetar", font_small)
btn_reveal = Button(WIDTH - 180, 20, 160, 40, "Ver Resposta", font_small)

search_bar = SearchBar(WIDTH//2 - 200, 150, 400, 40, font_small, game_state)

def draw_classic_headers(y_pos):
    col_width = 110
    headers = ["Nome", "Raridade", "Elixir", "Tipo", "Arena"]
    x = WIDTH//2 - 310
    curr_x = x + 70
    for h in headers:
        txt = font_small.render(h, True, (148, 163, 184))
        screen.blit(txt, (curr_x + (col_width - 5 - txt.get_width())//2, y_pos))
        curr_x += col_width

def main():
    clock = pygame.time.Clock()
    state = "MENU"
    revealed = False
    
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if state == "MENU":
                if btn_classic.handle_event(event):
                    state = "CLASSIC"
                    game_state.start_game()
                    revealed = False
                if btn_artwork.handle_event(event):
                    state = "ARTWORK"
                    game_state.start_game()
                    revealed = False
            else:
                if btn_menu.handle_event(event):
                    state = "MENU"
                if btn_reset.handle_event(event):
                    game_state.start_game()
                    revealed = False
                if btn_reveal.handle_event(event):
                    revealed = True
                search_bar.handle_event(event)

        screen.fill(BG_COLOR)
        
        if state == "MENU":
            title = font_title.render("ClashDle", True, TEXT_COLOR)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 150))
            btn_classic.draw(screen)
            btn_artwork.draw(screen)
            
        elif state == "CLASSIC":
            btn_menu.draw(screen)
            btn_reset.draw(screen)
            btn_reveal.draw(screen)
            title = font_large.render("Modo Clássico", True, TEXT_COLOR)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
            
            search_bar.rect.y = 100
            
            draw_classic_headers(160)
            
            y_offset = 190
            for guess in game_state.guesses[:6]:
                draw_guess_row(screen, font_small, game_state, guess, WIDTH//2 - 310, y_offset)
                y_offset += 85
                
            if game_state.won:
                win_txt = font_large.render("Você Acertou!", True, (34, 197, 94))
                screen.blit(win_txt, (WIDTH//2 - win_txt.get_width()//2, 100))
            elif revealed:
                ans_txt = font_large.render(f"Resposta: {game_state.target_card['name']}", True, (239, 68, 68))
                screen.blit(ans_txt, (WIDTH//2 - ans_txt.get_width()//2, 100))
            else:
                search_bar.draw(screen)
                
        elif state == "ARTWORK":
            btn_menu.draw(screen)
            btn_reset.draw(screen)
            btn_reveal.draw(screen)
            title = font_large.render("Modo Arte", True, TEXT_COLOR)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
            
            # Draw target artwork (pixelated) if not won
            if game_state.target_card:
                card_img = get_card_image(game_state.target_card['key'], (150, 180))
                if not game_state.won and not revealed:
                    guesses_made = len(game_state.guesses)
                    # Começa extremamente pixelado e revela progressivamente mais rápido
                    pixelate_factor = max(1, 35 - (guesses_made * 6))
                    if pixelate_factor > 1:
                        w = max(1, 150 // pixelate_factor)
                        h = max(1, 180 // pixelate_factor)
                        tiny_img = pygame.transform.scale(card_img, (w, h))
                        card_img = pygame.transform.scale(tiny_img, (150, 180))
                
                screen.blit(card_img, (WIDTH//2 - 75, 70))
            
            search_bar.rect.y = 270
            
            y_offset = 320
            # Show fewer rows due to space
            for guess in game_state.guesses[:5]: 
                draw_guess_row(screen, font_small, game_state, guess, WIDTH//2 - 310, y_offset)
                y_offset += 85
                
            if game_state.won:
                win_txt = font_large.render("Você Acertou!", True, (34, 197, 94))
                screen.blit(win_txt, (WIDTH//2 - win_txt.get_width()//2, 270))
            elif revealed:
                ans_txt = font_large.render(f"Resposta: {game_state.target_card['name']}", True, (239, 68, 68))
                screen.blit(ans_txt, (WIDTH//2 - ans_txt.get_width()//2, 270))
            else:
                search_bar.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
