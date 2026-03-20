import pygame
import sys

# Configurações de Tela e FPS
WIDTH, HEIGHT = 1000, 500
FPS = 60
GROUND_Y = 350

# Cores
GRAY = (40, 40, 40)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

class Fighter:
    def __init__(self, x, flip, name):
        self.name = name
        self.flip = flip
        # Tamanho padrão do lutador (pode ser ajustado conforme seus sprites)
        self.rect = pygame.Rect(x, GROUND_Y, 100, 150) 
        self.vel_y = 0
        self.health = 100
        
        # Estados de Movimento e Ação
        self.is_jumping = False
        self.is_crouching = False
        self.is_attacking = False
        self.is_blocking = False
        self.is_running = False # NOVO ESTADO
        self.attack_type = 0 # 1 para Soco, 2 para Chute
        self.attack_cooldown = 0

        # Carregamento Dinâmico (Busca exatamente o nome que você pediu + 'corre')
        try:
            self.sprites = {
                "idle": pygame.image.load(f"{name}parado.png").convert_alpha(),
                "jump": pygame.image.load(f"{name}pulo.png").convert_alpha(),
                "punch": pygame.image.load(f"{name}soco.png").convert_alpha(),
                "kick": pygame.image.load(f"{name}chute.png").convert_alpha(),
                "crouch": pygame.image.load(f"{name}agachado.png").convert_alpha(),
                "block": pygame.image.load(f"{name}defendendo.png").convert_alpha(),
                "run": pygame.image.load(f"{name}corre.png").convert_alpha(), # NOVO SPRITE
            }
        except pygame.error as e:
            print(f"Erro ao carregar sprites do {name}: {e}")
            print("Verifique se os nomes dos arquivos estão corretos (incluindo o novo 'corre.png').")
            pygame.quit()
            sys.exit()

    def move(self, target):
        WALK_SPEED = 7
        RUN_SPEED = 14 # Velocidade dobrada
        GRAVITY = 1.2
        dx = 0
        dy = 0
        
        key = pygame.key.get_pressed()
        self.is_blocking = False
        self.is_crouching = False
        self.is_running = False

        # --- CONTROLES PERSONAGEM 1 (WASD + Q/E + L-Shift para Correr) ---
        if self.name == "personagem1":
            if not self.is_attacking:
                # Verifica se está segurando L-Shift para correr
                running_mod = key[pygame.K_LSHIFT]
                current_speed = RUN_SPEED if running_mod else WALK_SPEED
                
                if key[pygame.K_a]: 
                    dx = -current_speed
                    if running_mod and not self.is_jumping: self.is_running = True
                if key[pygame.K_d]: 
                    dx = current_speed
                    if running_mod and not self.is_jumping: self.is_running = True
                    
                if key[pygame.K_w] and not self.is_jumping:
                    self.vel_y = -25
                    self.is_jumping = True
                if key[pygame.K_s]: 
                    self.is_crouching = True
                    
                # Bloqueio agora no CAPSLOCK ou Espace para libertar o Shift
                if key[pygame.K_SPACE]:
                    self.is_blocking = True
                
                # Ataques
                if key[pygame.K_e] and self.attack_cooldown == 0: # E = SOCO
                    self.attack(target, 1)
                if key[pygame.K_q] and self.attack_cooldown == 0: # Q = CHUTE
                    self.attack(target, 2)

        # --- CONTROLES PERSONAGEM 2 (SETAS + NUMPAD + R-Ctrl para Correr) ---
        else:
            if not self.is_attacking:
                # Verifica se está segurando R-Ctrl para correr
                running_mod = key[pygame.K_RCTRL]
                current_speed = RUN_SPEED if running_mod else WALK_SPEED
                
                if key[pygame.K_LEFT]: 
                    dx = -current_speed
                    if running_mod and not self.is_jumping: self.is_running = True
                if key[pygame.K_RIGHT]: 
                    dx = current_speed
                    if running_mod and not self.is_jumping: self.is_running = True
                    
                if key[pygame.K_UP] and not self.is_jumping:
                    self.vel_y = -25
                    self.is_jumping = True
                if key[pygame.K_DOWN]: 
                    self.is_crouching = True
                    
                if key[pygame.K_KP0]: # Bloqueio no 0 do Numpad
                    self.is_blocking = True
                
                # Ataques do P2 (Numpad 1 e 2)
                if key[pygame.K_KP1] and self.attack_cooldown == 0: # 1 = SOCO
                    self.attack(target, 1)
                if key[pygame.K_KP2] and self.attack_cooldown == 0: # 2 = CHUTE
                    self.attack(target, 2)

        # Aplicar Gravidade
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Limitar ao chão
        if self.rect.bottom + dy > HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            dy = 0
            self.is_jumping = False

        # Impedir que os personagens saiam da tela
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > WIDTH: dx = WIDTH - self.rect.right

        # Atualizar posição
        self.rect.x += dx
        self.rect.y += dy
        
        # Garante que os personagens sempre se olhem
        if self.rect.centerx < target.rect.centerx:
            self.flip = False
        else:
            self.flip = True
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self, target, type):
        self.is_attacking = True
        self.attack_type = type
        self.attack_cooldown = 25
        
        # Área de impacto (hitbox ativa)
        # Se estiver correndo, o alcance aumenta um pouco devido ao impulso
        reach = 130 if self.is_running else 100
        
        side = -1 if self.flip else 1
        hit_box = pygame.Rect(self.rect.centerx, self.rect.y, reach * side, self.rect.height)
        
        # pygame.draw.rect(screen, WHITE, hit_box) # Descomente para ver a hitbox

        if hit_box.colliderect(target.rect):
            damage = 10
            if self.is_running: damage = 15 # Dano extra se acertar correndo
            if target.is_blocking: damage = 2
            
            # Lógica de desvio:
            if type == 1 and target.is_crouching: damage = 0 # Soco erra agachado
            if type == 2 and target.is_jumping: damage = 0   # Chute erra pulador
            
            target.health -= damage

    def draw(self, surface):
        # Escolher sprite baseado no estado (Prioridade: Ataque > Bloqueio > Pulo > Agachado > Corrida > Parado)
        img_key = "idle"
        
        if self.is_attacking:
            img_key = "punch" if self.attack_type == 1 else "kick"
        elif self.is_blocking: 
            img_key = "block"
        elif self.is_jumping: 
            img_key = "jump"
        elif self.is_crouching: 
            img_key = "crouch"
        elif self.is_running: # NOVA PRIORIDADE DE SPRITE
            img_key = "run"
        
        image = self.sprites[img_key]
        image = pygame.transform.flip(image, self.flip, False)
        surface.blit(image, (self.rect.x, self.rect.y))
        
        # Fim da animação de ataque (simplificado)
        if self.attack_cooldown < 15:
            self.is_attacking = False

def draw_hud(surface, p1, p2):
    # Barra P1
    pygame.draw.rect(surface, RED, (50, 40, 400, 30))
    pygame.draw.rect(surface, GREEN, (50, 40, 4 * p1.health, 30))
    # Barra P2
    pygame.draw.rect(surface, RED, (550, 40, 400, 30))
    pygame.draw.rect(surface, GREEN, (550, 40, 4 * p2.health, 30))

# --- LOOP PRINCIPAL ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Street Fighter Pygame com Corrida")
clock = pygame.time.Clock()

# Criando as instâncias com nomes diferentes
p1 = Fighter(200, False, "personagem1")
p2 = Fighter(700, True, "personagem2")

while True:
    screen.fill(GRAY)
    pygame.draw.line(screen, WHITE, (0, HEIGHT-50), (WIDTH, HEIGHT-50), 2) # Chão
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Passa o outro personagem como alvo para colisão e auto-facing
    p1.move(p2)
    p2.move(p1)

    p1.draw(screen)
    p2.draw(screen)
    draw_hud(screen, p1, p2)

    if p1.health <= 0 or p2.health <= 0:
        # Lógica simples de fim de jogo no console
        winner = "P2" if p1.health <= 0 else "P1"
        print(f"K.O.! {winner} Venceu!")
        pygame.quit()
        sys.exit()

    pygame.display.update()
    clock.tick(FPS)
