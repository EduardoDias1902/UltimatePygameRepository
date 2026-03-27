import pygame
import requests
import random
import unicodedata

# Configurações Iniciais
pygame.init()
WIDTH, HEIGHT = 500, 750 # Aumentei um pouco a altura para o botão
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Termo Clone - Com Reiniciar")

# Cores
COLOR_BG = (18, 18, 19)
COLOR_GRID = (58, 58, 60)
COLOR_CORRECT = (83, 141, 78)
COLOR_PRESENT = (181, 159, 59)
COLOR_ABSENT = (58, 58, 60)
COLOR_TEXT = (255, 255, 255)
COLOR_BTN = (129, 131, 132)

# Fontes
FONT_MAIN = pygame.font.SysFont("Arial", 40, bold=True)
FONT_MSG = pygame.font.SysFont("Arial", 22, bold=True)
FONT_BTN = pygame.font.SysFont("Arial", 20, bold=True)

def buscar_palavra_portugues():
    try:
        url = "https://www.ime.usp.br/~pf/dicios/br-sem-acentos.txt"
        response = requests.get(url, timeout=3)
        palavras = [p.strip().upper() for p in response.text.split() if len(p.strip()) == 5]
        return random.choice(palavras)
    except:
        return random.choice(["TERMO", "SAGAZ", "NOBRE", "MUNDO", "PLENA", "VIVER"])

# --- Variáveis Globais de Estado ---
palavra_secreta = ""
tentativas = []
cores_tentativas = []
tentativa_atual = 0
letra_atual = 0
jogo_finalizado = False
mensagem = ""

def reiniciar_jogo():
    global palavra_secreta, tentativas, cores_tentativas, tentativa_atual, letra_atual, jogo_finalizado, mensagem
    palavra_secreta = buscar_palavra_portugues()
    tentativas = [["" for _ in range(5)] for _ in range(6)]
    cores_tentativas = [[COLOR_GRID for _ in range(5)] for _ in range(6)]
    tentativa_atual = 0
    letra_atual = 0
    jogo_finalizado = False
    mensagem = ""

# Inicializa o primeiro jogo
reiniciar_jogo()

def verificar_palavra():
    global tentativa_atual, jogo_finalizado, mensagem
    palavra_digitada = "".join(tentativas[tentativa_atual])
    
    if len(palavra_digitada) < 5: return

    temp_secreta = list(palavra_secreta)
    resultado_cores = [COLOR_ABSENT] * 5

    for i in range(5):
        if palavra_digitada[i] == palavra_secreta[i]:
            resultado_cores[i] = COLOR_CORRECT
            temp_secreta[i] = None

    for i in range(5):
        if resultado_cores[i] == COLOR_CORRECT: continue
        if palavra_digitada[i] in temp_secreta:
            resultado_cores[i] = COLOR_PRESENT
            temp_secreta[temp_secreta.index(palavra_digitada[i])] = None

    cores_tentativas[tentativa_atual] = resultado_cores

    if palavra_digitada == palavra_secreta:
        mensagem = "PARABÉNS! VOCÊ ACERTOU!"
        jogo_finalizado = True
    elif tentativa_atual == 5:
        mensagem = f"FIM DE JOGO! ERA: {palavra_secreta}"
        jogo_finalizado = True
    
    tentativa_atual += 1

def desenhar():
    SCREEN.fill(COLOR_BG)
    
    # Grid
    for r in range(6):
        for c in range(5):
            rect = pygame.Rect(90 + c * 65, 50 + r * 75, 60, 70)
            if r < tentativa_atual:
                pygame.draw.rect(SCREEN, cores_tentativas[r][c], rect, border_radius=4)
            else:
                pygame.draw.rect(SCREEN, (50, 50, 50), rect, 2, border_radius=4)
            
            texto = FONT_MAIN.render(tentativas[r][c], True, COLOR_TEXT)
            text_rect = texto.get_rect(center=rect.center)
            SCREEN.blit(texto, text_rect)

    # Mensagem de Feedback
    if mensagem:
        txt_surf = FONT_MSG.render(mensagem, True, COLOR_TEXT)
        SCREEN.blit(txt_surf, (WIDTH//2 - txt_surf.get_width()//2, 580))

    # Botão de Reiniciar (sempre visível ou apenas no fim, aqui deixei sempre disponível)
    btn_rect = pygame.Rect(WIDTH//2 - 60, 640, 120, 40)
    pygame.draw.rect(SCREEN, COLOR_BTN, btn_rect, border_radius=10)
    txt_btn = FONT_BTN.render("REINICIAR", True, COLOR_TEXT)
    SCREEN.blit(txt_btn, (btn_rect.centerx - txt_btn.get_width()//2, btn_rect.centery - txt_btn.get_height()//2))

    pygame.display.flip()
    return btn_rect # Retorna o retângulo para detecção de clique

# Loop Principal
running = True
while running:
    btn_rect_pos = desenhar()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_rect_pos.collidepoint(event.pos):
                reiniciar_jogo()

        if event.type == pygame.KEYDOWN and not jogo_finalizado:
            if event.key == pygame.K_BACKSPACE:
                if letra_atual > 0:
                    letra_atual -= 1
                    tentativas[tentativa_atual][letra_atual] = ""
            
            elif event.key == pygame.K_RETURN:
                if letra_atual == 5:
                    verificar_palavra()
                    letra_atual = 0
            
            else:
                if letra_atual < 5 and event.unicode.isalpha():
                    tentativas[tentativa_atual][letra_atual] = event.unicode.upper()
                    letra_atual += 1

pygame.quit()