import pygame
import sys

# Configurações de Tela
WIDTH, HEIGHT = 1000, 600
FPS = 60
# Plataforma centralizada (ajustada para os personagens não sumirem)
GROUND_Y = 450 

# Cores
GRAY = (30, 30, 30)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
WHITE = (255, 255, 255)
BLUE = (50, 50, 150)

class Fighter:
    def __init__(self, x, flip, name):
        self.name = name
        self.flip = flip
        # Definimos um tamanho fixo para TODOS os sprites para evitar bugs de altura
        self.width, self.height = 180, 180 
        self.rect = pygame.Rect(x, GROUND_Y - self.height, self.width, self.height)
        
        self.vel_y = 0
        self.health = 100
        
        # Estados
        self.is_jumping = False
        self.is_crouching = False
        self.is_attacking = False
        self.is_blocking = False
        self.is_moving = False 
        self.attack_type = 0 
        self.attack_cooldown = 0

        # Carregamento com Redimensionamento Fixo
        self.sprites = {}
        actions = ["parado", "pulo", "soco", "chute", "agachado", "defendendo", "corre"]
        
        for action in actions:
            try:
                img = pygame.image.load(f"{name}{action}.png").convert_alpha()
                # Força todas as imagens a terem o mesmo tamanho exato
                self.sprites[action] = pygame.transform.scale(img, (self.width, self.height))
            except:
                # Se faltar imagem, cria um bloco colorido para não travar o jogo
                surf = pygame.Surface((self.width, self.height))
                surf.fill(RED if "personagem1" in name else BLUE)
                self.sprites[action] = surf
                print(f"Aviso: Imagem {name}{action}.png não encontrada.")

    def move(self, target):
        SPEED = 7
        GRAVITY = 1.2
        dx = 0
        dy = 0
        
        key = pygame.key.get_pressed()
        self.is_blocking = False
        self.is_crouching = False
        self.is_moving = False

        # --- CONTROLES P1 (WASD + Q/E) ---
        if self.name == "personagem1":
            if not self.is_attacking:
                if key[pygame.K_a]: 
                    dx = -SPEED
                    self.is_moving = True
                if key[pygame.K_d]: 
                    dx = SPEED
                    self.is_moving = True
                if key[pygame.K_w] and not self.is_jumping:
                    self.vel_y = -25
                    self.is_jumping = True
                if key[pygame.K_s]: 
                    self.is_crouching = True
                if key[pygame.K_LSHIFT]: 
                    self.is_blocking = True
                
                if key[pygame.K_e] and self.attack_cooldown == 0: self.attack(target, 1) # Soco
                if key[pygame.K_q] and self.attack_cooldown == 0: self.attack(target, 2) # Chute

        # --- CONTROLES P2 (Setas + P/O) ---
        else:
            if not self.is_attacking:
                if key[pygame.K_LEFT]: 
                    dx = -SPEED
                    self.is_moving = True
                if key[pygame.K_RIGHT]: 
                    dx = SPEED
                    self.is_moving = True
                if key[pygame.K_UP] and not self.is_jumping:
                    self.vel_y = -25
                    self.is_jumping = True
                if key[pygame.K_DOWN]: 
                    self.is_crouching = True
                if key[pygame.K_k]: # Exemplo para bloqueio no P2
                    self.is_blocking = True
                
                # Novos controles P2 solicitados
                if key[pygame.K_p] and self.attack_cooldown == 0: self.attack(target, 1) # P = Soco
                if key[pygame.K_o] and self.attack_cooldown == 0: self.attack(target, 2) # O = Chute

        # Gravidade
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Colisão com o Chão Centralizado
        if self.rect.bottom + dy > GROUND_Y:
            self.rect.bottom = GROUND_Y
            dy = 0
            self.is_jumping = False

        # Limites da Tela (Impedir de sair)
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > WIDTH: dx = WIDTH - self.rect.right

        self.rect.x += dx
        self.rect.y += dy
        
        # Auto-face (olhar um para o outro)
        self.flip = self.rect.centerx > target.rect.centerx
            
        if self.attack_cooldown > 0: self.attack_cooldown -= 1

    def attack(self, target, type):
        self.is_attacking = True
        self.attack_type = type
        self.attack_cooldown = 20
        
        # Hitbox de ataque
        reach = 90
        side = -1 if self.flip else 1
        hit_box = pygame.Rect(self.rect.centerx, self.rect.y, reach * side, self.rect.height)
        
        if hit_box.colliderect(target.rect):
            damage = 10
            if target.is_blocking: damage = 2
            if type == 1 and target.is_crouching: damage = 0 
            if type == 2 and target.is_jumping: damage = 0   
            target.health -= damage

    def draw(self, surface):
        # Lógica de seleção de sprite
        img_key = "parado"
        if self.is_attacking:
            img_key = "soco" if self.attack_type == 1 else "chute"
        elif self.is_blocking: img_key = "defendendo"
        elif self.is_jumping: img_key = "pulo"
        elif self.is_crouching: img_key = "agachado"
        elif self.is_moving: img_key = "corre"
        
        image = self.sprites[img_key]
        image = pygame.transform.flip(image, self.flip, False)
        surface.blit(image, (self.rect.x, self.rect.y))
        
        if self.attack_cooldown < 12: self.is_attacking = False

def draw_hud(surface, p1, p2):
    # Barras de Vida
    pygame.draw.rect(surface, RED, (50, 40, 350, 25))
    pygame.draw.rect(surface, GREEN, (50, 40, 3.5 * p1.health, 25))
    pygame.draw.rect(surface, RED, (600, 40, 350, 25))
    pygame.draw.rect(surface, GREEN, (600, 40, 3.5 * p2.health, 25))

# Inicialização
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Street Fighter Pygame")
clock = pygame.time.Clock()

p1 = Fighter(200, False, "personagem1")
p2 = Fighter(700, True, "personagem2")

while True:
    screen.fill(GRAY)
    # Chão Centralizado
    pygame.draw.rect(screen, WHITE, (0, GROUND_Y, WIDTH, 5)) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    p1.move(p2)
    p2.move(p1)
    p1.draw(screen)
    p2.draw(screen)
    draw_hud(screen, p1, p2)

    if p1.health <= 0 or p2.health <= 0:
        print("Fim da Luta!")
        pygame.quit()
        sys.exit()

    pygame.display.update()
    clock.tick(FPS)
