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
        self.rect = pygame.Rect(x, GROUND_Y, 100, 150) 
        self.vel_y = 0
        self.health = 100
        
        # Estados
        self.is_jumping = False
        self.is_crouching = False
        self.is_attacking = False
        self.is_blocking = False
        self.is_moving = False # Agora apenas indica se está andando
        self.attack_type = 0 
        self.attack_cooldown = 0

        # Carregamento de Sprites
        try:
            self.sprites = {
                "idle": pygame.image.load(f"{name}parado.png").convert_alpha(),
                "jump": pygame.image.load(f"{name}pulo.png").convert_alpha(),
                "punch": pygame.image.load(f"{name}soco.png").convert_alpha(),
                "kick": pygame.image.load(f"{name}chute.png").convert_alpha(),
                "crouch": pygame.image.load(f"{name}agachado.png").convert_alpha(),
                "block": pygame.image.load(f"{name}defendendo.png").convert_alpha(),
                "move": pygame.image.load(f"{name}corre.png").convert_alpha(), # Sprite de andar
            }
        except pygame.error as e:
            print(f"Erro ao carregar sprites: {e}")
            pygame.quit()
            sys.exit()

    def move(self, target):
        SPEED = 7 # Velocidade fixa de caminhada
        GRAVITY = 1.2
        dx = 0
        dy = 0
        
        key = pygame.key.get_pressed()
        self.is_blocking = False
        self.is_crouching = False
        self.is_moving = False

        # --- CONTROLES PERSONAGEM 1 (WASD + Q/E) ---
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
                if key[pygame.K_SPACE]: 
                    self.is_blocking = True
                
                # Ataques
                if key[pygame.K_e] and self.attack_cooldown == 0:
                    self.attack(target, 1) # Soco
                if key[pygame.K_q] and self.attack_cooldown == 0:
                    self.attack(target, 2) # Chute

        # --- CONTROLES PERSONAGEM 2 (SETAS + 1/2) ---
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
                if key[pygame.K_KP0]: 
                    self.is_blocking = True
                
                if key[pygame.K_KP1] and self.attack_cooldown == 0:
                    self.attack(target, 1)
                if key[pygame.K_KP2] and self.attack_cooldown == 0:
                    self.attack(target, 2)

        # Gravidade e Chão
        self.vel_y += GRAVITY
        dy += self.vel_y
        if self.rect.bottom + dy > HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            dy = 0
            self.is_jumping = False

        # Limites da tela
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > WIDTH: dx = WIDTH - self.rect.right

        self.rect.x += dx
        self.rect.y += dy
        
        # Sempre olhar para o oponente
        self.flip = self.rect.centerx > target.rect.centerx
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self, target, type):
        self.is_attacking = True
        self.attack_type = type
        self.attack_cooldown = 20
        
        side = -1 if self.flip else 1
        hit_box = pygame.Rect(self.rect.centerx, self.rect.y, 100 * side, self.rect.height)
        
        if hit_box.colliderect(target.rect):
            damage = 10
            if target.is_blocking: damage = 2
            if type == 1 and target.is_crouching: damage = 0 # Soco erra agachado
            if type == 2 and target.is_jumping: damage = 0   # Chute erra pulo
            target.health -= damage

    def draw(self, surface):
        img_key = "idle"
        
        if self.is_attacking:
            img_key = "punch" if self.attack_type == 1 else "kick"
        elif self.is_blocking: 
            img_key = "block"
        elif self.is_jumping: 
            img_key = "jump"
        elif self.is_crouching: 
            img_key = "crouch"
        elif self.is_moving: # Mostra sprite "corre" ao andar
            img_key = "move"
        
        image = self.sprites[img_key]
        image = pygame.transform.flip(image, self.flip, False)
        surface.blit(image, (self.rect.x, self.rect.y))
        
        if self.attack_cooldown < 10:
            self.is_attacking = False

def draw_hud(surface, p1, p2):
    pygame.draw.rect(surface, RED, (50, 40, 400, 30))
    pygame.draw.rect(surface, GREEN, (50, 40, 4 * p1.health, 30))
    pygame.draw.rect(surface, RED, (550, 40, 400, 30))
    pygame.draw.rect(surface, GREEN, (550, 40, 4 * p2.health, 30))

# Loop Principal
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Luta 2D")
clock = pygame.time.Clock()

p1 = Fighter(200, False, "personagem1")
p2 = Fighter(700, True, "personagem2")

while True:
    screen.fill(GRAY)
    pygame.draw.line(screen, WHITE, (0, HEIGHT-50), (WIDTH, HEIGHT-50), 2)
    
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
        pygame.quit()
        sys.exit()

    pygame.display.update()
    clock.tick(FPS)