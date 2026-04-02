import pygame
import time

def test():
    pygame.init()
    screen = pygame.Surface((960, 540))
    texture = pygame.Surface((64, 64))
    texture.fill((200, 0, 0))
    pygame.draw.rect(texture, (0, 0, 0), (0, 0, 64, 64), 2)
    
    start = time.time()
    for _ in range(60):
        for col in range(960 // 2):
            tex_x = col % 64
            strip = texture.subsurface((tex_x, 0, 1, 64))
            scaled = pygame.transform.scale(strip, (2, 300))
            screen.blit(scaled, (col * 2, 100))
    dur = time.time() - start
    print(f"Time for 60 frames: {dur:.3f}s (FPS: {60/dur:.1f})")

if __name__ == '__main__':
    test()
