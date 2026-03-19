import pygame
import random
import sys

# Inicialização
pygame.init()

# Configurações da Tela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Esquiva Estável - Posições Aleatórias")

# --- CONFIGURAÇÕES DE TAMANHO ---
LARGURA_BASE = 110  
ALTURA_BASE = 150
TAM_AGACHADO = (LARGURA_BASE, int(ALTURA_BASE * 0.6)) 
TAM_OBSTACULO = (60, 60)
Y_CHAO = ALTURA - 20 

# Cores
CORES_BASICAS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (128, 0, 128), (255, 165, 0)]

# Fonte
fonte = pygame.font.SysFont("Arial", 35, True)

def carregar_e_escalar(nome_arquivo, tamanho, cor_reserva):
    try:
        img = pygame.image.load(nome_arquivo).convert_alpha()
        return pygame.transform.scale(img, tamanho)
    except:
        surf = pygame.Surface(tamanho)
        surf.fill(cor_reserva)
        return surf

# Imagens Jogador
img_parado = carregar_e_escalar("parado.png", (LARGURA_BASE, ALTURA_BASE), (200, 200, 200))
img_correndo = carregar_e_escalar("correndo.png", (int(LARGURA_BASE * 1.1), int(ALTURA_BASE * 1.1)), (180, 180, 180))
img_pulando = carregar_e_escalar("pulando.png", (LARGURA_BASE, ALTURA_BASE), (220, 220, 220))
img_agachado = carregar_e_escalar("agachado.png", TAM_AGACHADO, (100, 100, 100))

# Variáveis Jogador
player_x = LARGURA // 2
player_y = Y_CHAO - ALTURA_BASE
player_vel_y = 0
esta_pulando = False
esta_agachado = False
olhando_esquerda = False
gravidade =1
forca_pulo = -22
velocidade_andando = 10

# Inimigos
inimigos = []
velocidade_inimigo = 7.0
spawn_timer = 0
# Intervalo de spawn (em frames) - agora vamos variar isso
proximo_spawn = 90 

score = 0
ultimo_checkpoint = 0

clock = pygame.time.Clock()
rodando = True

while rodando:
    tela.fill((240, 240, 240))
    pygame.draw.line(tela, (0, 0, 0), (0, Y_CHAO), (LARGURA, Y_CHAO), 2)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    if score > 0 and score % 3 == 0 and score != ultimo_checkpoint:
        velocidade_inimigo *= 1.02
        ultimo_checkpoint = score

    keys = pygame.key.get_pressed()
    
    # Lógica de Agachar
    if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not esta_pulando:
        esta_agachado = True
        altura_atual = TAM_AGACHADO[1]
    else:
        esta_agachado = False
        altura_atual = ALTURA_BASE

    # Movimentação
    vel_atual = velocidade_andando * 0.5 if esta_agachado else velocidade_andando
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= vel_atual
        olhando_esquerda = True
    if keys[pygame.K_RIGHT] and player_x < LARGURA - LARGURA_BASE:
        player_x += vel_atual
        olhando_esquerda = False
    
    # Pulo
    if not esta_pulando and not esta_agachado:
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            player_vel_y = forca_pulo
            esta_pulando = True
    
    # Física
    player_y += player_vel_y
    player_vel_y += gravidade
    if player_y + altura_atual >= Y_CHAO:
        player_y = Y_CHAO - altura_atual
        esta_pulando = False
        player_vel_y = 0

    # --- NOVO GERADOR ALEATÓRIO DE OBSTÁCULOS ---
    spawn_timer += 1.0
    if spawn_timer >= proximo_spawn:
        # Altura totalmente aleatória entre o chão e o topo do pulo
        y_aleatorio = random.randint(Y_CHAO - 260, Y_CHAO - 60)
        
        rect_ini = pygame.Rect(LARGURA, y_aleatorio, TAM_OBSTACULO[0], TAM_OBSTACULO[1])
        cor_ini = random.choice(CORES_BASICAS)
        inimigos.append([rect_ini, cor_ini])
        
        # Reseta o timer e define um tempo aleatório para o próximo bloco
        spawn_timer = 0
        proximo_spawn = random.randint(60, 130) 

    # Atualizar e Desenhar Obstáculos
    for obj in inimigos[:]:
        rect, cor = obj
        rect.x -= velocidade_inimigo
        pygame.draw.rect(tela, cor, rect)
        pygame.draw.rect(tela, (0, 0, 0), rect, 2)

        if rect.x < -TAM_OBSTACULO[0]:
            inimigos.remove(obj)
            score += 1
        
        # Colisão
        p_rect = pygame.Rect(player_x, player_y, LARGURA_BASE, altura_atual)
        if p_rect.colliderect(rect):
            print(f"Game Over! Pontos: {score}")
            rodando = False

    # Desenho do Jogador
    if esta_pulando:
        img_final = img_pulando
    elif esta_agachado:
        img_final = img_agachado
    elif (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
        img_final = img_correndo
    else:
        img_final = img_parado
    
    if olhando_esquerda:
        img_final = pygame.transform.flip(img_final, True, False)

    draw_x, draw_y = player_x, player_y
    if not esta_pulando and not esta_agachado and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
        draw_x -= (img_correndo.get_width() - LARGURA_BASE) // 2
        draw_y -= (img_correndo.get_height() - ALTURA_BASE)

    tela.blit(img_final, (draw_x, draw_y))

    # HUD
    texto = fonte.render(f"Score: {score}  Vel: {velocidade_inimigo:.1f}", True, (0, 0, 0))
    tela.blit(texto, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
