import math
import random
import sys
from dataclasses import dataclass

import pygame


# Um "Doom-like" em Pygame (raycasting 2.5D).
# Não replica o DOOM original (assets/licenças/código), mas entrega mecânicas parecidas.


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def wrap_angle(a: float) -> float:
    a = (a + math.pi) % (2 * math.pi) - math.pi
    return a


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


@dataclass
class Player:
    x: float
    y: float
    ang: float
    hp: int = 100
    ammo: int = 50

    move_speed: float = 3.0
    rot_speed: float = 2.4


@dataclass
class Enemy:
    x: float
    y: float
    hp: int = 40
    alive: bool = True
    cooldown: float = 0.0
    state: str = "idle"  # idle/chase


class World:
    def __init__(self, grid: list[str]) -> None:
        self.grid = grid
        self.h = len(grid)
        self.w = len(grid[0]) if self.h else 0

    def in_bounds(self, gx: int, gy: int) -> bool:
        return 0 <= gx < self.w and 0 <= gy < self.h

    def cell(self, gx: int, gy: int) -> str:
        if not self.in_bounds(gx, gy):
            return "#"
        return self.grid[gy][gx]

    def is_wall(self, gx: int, gy: int) -> bool:
        return self.cell(gx, gy) == "#"

    def is_blocked(self, x: float, y: float) -> bool:
        return self.is_wall(int(x), int(y))


def try_move(world: World, x: float, y: float, nx: float, ny: float, radius: float) -> tuple[float, float]:
    # Colisão simples em círculo vs grid (separa eixos)
    def blocked(px: float, py: float) -> bool:
        # amostra 4 pontos do círculo
        for ox, oy in ((-radius, 0), (radius, 0), (0, -radius), (0, radius)):
            if world.is_blocked(px + ox, py + oy):
                return True
        return False

    tx, ty = x, y
    if not blocked(nx, ty):
        tx = nx
    if not blocked(tx, ny):
        ty = ny
    return tx, ty


def cast_ray_dda(world: World, ox: float, oy: float, ang: float, max_dist: float = 30.0) -> tuple[float, int, int, int]:
    # DDA clássico: retorna distância, célula atingida, e "side" (0 x-step, 1 y-step)
    dx = math.cos(ang)
    dy = math.sin(ang)

    map_x = int(ox)
    map_y = int(oy)

    delta_dist_x = abs(1.0 / dx) if dx != 0 else 1e30
    delta_dist_y = abs(1.0 / dy) if dy != 0 else 1e30

    if dx < 0:
        step_x = -1
        side_dist_x = (ox - map_x) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (map_x + 1.0 - ox) * delta_dist_x

    if dy < 0:
        step_y = -1
        side_dist_y = (oy - map_y) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (map_y + 1.0 - oy) * delta_dist_y

    side = 0
    for _ in range(int(max_dist * 4) + 1):
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1

        if world.is_wall(map_x, map_y):
            if side == 0:
                perp = (map_x - ox + (1 - step_x) / 2) / (dx if dx != 0 else 1e-9)
            else:
                perp = (map_y - oy + (1 - step_y) / 2) / (dy if dy != 0 else 1e-9)
            return max(0.0001, perp), map_x, map_y, side

    return max_dist, map_x, map_y, side


def line_of_sight(world: World, x0: float, y0: float, x1: float, y1: float) -> bool:
    # Ray march simples (passo pequeno)
    dx = x1 - x0
    dy = y1 - y0
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return True
    steps = int(dist * 12)
    for i in range(steps + 1):
        t = i / steps
        x = x0 + dx * t
        y = y0 + dy * t
        if world.is_blocked(x, y):
            return False
    return True


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Doom-like (Pygame)")

        self.W, self.H = 960, 540
        self.screen = pygame.display.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)

        self.render_scale = 1  # aumente para 2 em PCs lentos (reduz colunas)
        self.fov = math.radians(66)

        self.world = World(
            [
                "################",
                "#......#.......#",
                "#..##..#..##...#",
                "#......#.......#",
                "#..#.......#...#",
                "#..#..###..#...#",
                "#..#.......#...#",
                "#......#.......#",
                "#..##..#..##...#",
                "#......#.......#",
                "#......#.......#",
                "################",
            ]
        )

        self.player = Player(x=2.5, y=2.5, ang=0.0)
        self.player_radius = 0.18

        self.enemies: list[Enemy] = [
            Enemy(10.5, 2.5, hp=50),
            Enemy(12.5, 8.5, hp=60),
            Enemy(6.5, 9.5, hp=40),
        ]

        self.shake = 0.0
        self.weapon_t = 0.0
        self.firing = False
        self.fire_flash = 0.0
        self.hit_marker = 0.0

        self.mouse_look = True
        self._setup_mouse()

    def _setup_mouse(self) -> None:
        pygame.event.set_grab(self.mouse_look)
        pygame.mouse.set_visible(not self.mouse_look)
        pygame.mouse.get_rel()

    def toggle_mouse(self) -> None:
        self.mouse_look = not self.mouse_look
        self._setup_mouse()

    def run(self) -> None:
        while True:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_TAB:
                    self.toggle_mouse()
                if event.key == pygame.K_r:
                    # recarrega "clip" simples
                    self.player.ammo = min(200, self.player.ammo + 25)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._fire()

    def _update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        if self.mouse_look:
            mx, _ = pygame.mouse.get_rel()
            self.player.ang = wrap_angle(self.player.ang + (-mx) * 0.0022)
        else:
            rot = 0.0
            if keys[pygame.K_LEFT]:
                rot += 1.0
            if keys[pygame.K_RIGHT]:
                rot -= 1.0
            self.player.ang = wrap_angle(self.player.ang + rot * self.player.rot_speed * dt)

        move = pygame.Vector2(0, 0)
        forward = pygame.Vector2(math.cos(self.player.ang), math.sin(self.player.ang))
        right = pygame.Vector2(forward.y, -forward.x)
        if keys[pygame.K_w]:
            move += forward
        if keys[pygame.K_s]:
            move -= forward
        if keys[pygame.K_d]:
            move += right
        if keys[pygame.K_a]:
            move -= right

        speed = self.player.move_speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed *= 1.35

        if move.length_squared() > 0:
            move = move.normalize() * speed * dt
            nx = self.player.x + move.x
            ny = self.player.y + move.y
            self.player.x, self.player.y = try_move(
                self.world, self.player.x, self.player.y, nx, ny, self.player_radius
            )

        # timers
        self.weapon_t += dt * (6.0 if move.length_squared() > 0 else 2.0)
        self.shake = max(0.0, self.shake - dt * 6.0)
        self.fire_flash = max(0.0, self.fire_flash - dt * 10.0)
        self.hit_marker = max(0.0, self.hit_marker - dt * 8.0)

        # inimigos
        for e in self.enemies:
            if not e.alive:
                continue
            e.cooldown = max(0.0, e.cooldown - dt)

            dx = self.player.x - e.x
            dy = self.player.y - e.y
            dist = math.hypot(dx, dy)

            if dist < 9.5 and line_of_sight(self.world, e.x, e.y, self.player.x, self.player.y):
                e.state = "chase"
            elif dist > 12.0:
                e.state = "idle"

            if e.state == "chase":
                # anda em direção ao player
                if dist > 1.2:
                    vx = dx / (dist + 1e-6)
                    vy = dy / (dist + 1e-6)
                    step = 1.6 * dt
                    nx = e.x + vx * step
                    ny = e.y + vy * step
                    if not self.world.is_blocked(nx, ny):
                        e.x, e.y = nx, ny

                # atira se perto e com cooldown
                if dist < 6.5 and e.cooldown <= 0.0:
                    e.cooldown = random.uniform(0.7, 1.3)
                    if random.random() < 0.55:
                        self.player.hp = max(0, self.player.hp - random.randint(3, 8))
                        self.shake = min(1.0, self.shake + 0.55)

        if self.player.hp <= 0:
            self._respawn()

    def _respawn(self) -> None:
        self.player.x, self.player.y, self.player.ang = 2.5, 2.5, 0.0
        self.player.hp = 100
        self.player.ammo = 50
        for i, e in enumerate(self.enemies):
            e.alive = True
            e.hp = 40 + i * 10
            e.cooldown = 0.0
            e.state = "idle"
        self.shake = 0.0
        self.fire_flash = 0.0
        self.hit_marker = 0.0

    def _fire(self) -> None:
        if self.player.ammo <= 0:
            self.shake = min(1.0, self.shake + 0.15)
            return

        self.player.ammo -= 1
        self.fire_flash = 1.0
        self.shake = min(1.0, self.shake + 0.35)

        # hitscan: pega inimigo mais próximo dentro de um cone pequeno
        best = None
        best_dist = 1e9
        cone = math.radians(2.6)

        px, py = self.player.x, self.player.y
        for e in self.enemies:
            if not e.alive:
                continue
            dx = e.x - px
            dy = e.y - py
            dist = math.hypot(dx, dy)
            if dist < 0.25:
                continue
            ang_to = math.atan2(dy, dx)
            da = abs(wrap_angle(ang_to - self.player.ang))
            if da <= cone and dist < best_dist:
                if line_of_sight(self.world, px, py, e.x, e.y):
                    best = e
                    best_dist = dist

        if best is not None:
            dmg = random.randint(12, 22)
            best.hp -= dmg
            self.hit_marker = 1.0
            if best.hp <= 0:
                best.alive = False

    def _render(self) -> None:
        self.screen.fill((0, 0, 0))

        # "camera bob" e shake
        bob = math.sin(self.weapon_t) * 2.5 + math.sin(self.weapon_t * 0.5) * 1.5
        shake_x = (random.random() - 0.5) * 10.0 * (self.shake**2)
        shake_y = (random.random() - 0.5) * 8.0 * (self.shake**2)

        # chão / teto
        ceil = (25, 15, 20)
        floor = (25, 22, 10)
        self.screen.fill(ceil, pygame.Rect(0, 0, self.W, self.H // 2))
        self.screen.fill(floor, pygame.Rect(0, self.H // 2, self.W, self.H // 2))

        # raycast paredes
        num_cols = self.W // self.render_scale
        col_w = self.render_scale
        px, py, pa = self.player.x, self.player.y, self.player.ang

        zbuf = [0.0] * num_cols
        for col in range(num_cols):
            cam_x = (2 * col / max(1, num_cols - 1) - 1.0)
            ray_ang = pa + math.atan(cam_x * math.tan(self.fov / 2))

            dist, _, _, side = cast_ray_dda(self.world, px, py, ray_ang, max_dist=32.0)
            dist *= math.cos(ray_ang - pa)  # remove fish-eye
            dist = max(0.0001, dist)
            zbuf[col] = dist

            wall_h = int(self.H / dist)
            y0 = (self.H - wall_h) // 2 + int(shake_y)
            x0 = col * col_w + int(shake_x)

            # cor de parede por distância + lado
            shade = clamp(1.0 - dist / 16.0, 0.08, 1.0)
            base = (170, 60, 55) if side == 0 else (140, 45, 45)
            color = (int(base[0] * shade), int(base[1] * shade), int(base[2] * shade))
            pygame.draw.rect(self.screen, color, pygame.Rect(x0, y0, col_w + 1, wall_h))

        # sprites (inimigos)
        sprites: list[tuple[float, Enemy]] = []
        for e in self.enemies:
            if not e.alive:
                continue
            dx = e.x - px
            dy = e.y - py
            dist = math.hypot(dx, dy)
            sprites.append((dist, e))
        sprites.sort(key=lambda t: -t[0])  # desenha longe -> perto

        for dist, e in sprites:
            ang_to = math.atan2(e.y - py, e.x - px)
            rel = wrap_angle(ang_to - pa)
            if abs(rel) > self.fov * 0.62:
                continue

            # projeta no plano da tela
            sx = (0.5 + (rel / self.fov)) * self.W + shake_x
            if dist < 0.2:
                continue

            size = (self.H / dist) * 0.85
            top = (self.H / 2 - size / 2) + shake_y
            left = sx - size / 2

            # desenha em "fatias" respeitando z-buffer
            x_start = int(left)
            x_end = int(left + size)
            if x_end < 0 or x_start >= self.W:
                continue

            # aparência do inimigo
            # corpo
            body_col = (60, 190, 70)
            if e.hp < 20:
                body_col = (210, 180, 40)

            for x in range(max(0, x_start), min(self.W, x_end)):
                col_idx = int(x / col_w)
                if 0 <= col_idx < num_cols and dist >= zbuf[col_idx]:
                    continue
                # variação pra dar "textura"
                t = (x - x_start) / max(1.0, (x_end - x_start))
                dark = 0.85 + 0.15 * math.sin(t * math.tau * 3)
                c = (int(body_col[0] * dark), int(body_col[1] * dark), int(body_col[2] * dark))
                pygame.draw.line(self.screen, c, (x, int(top)), (x, int(top + size)))

            # barra de vida pequena
            bx = int(sx - 18)
            by = int(top - 10)
            hpw = int(36 * clamp(e.hp / 60.0, 0.0, 1.0))
            pygame.draw.rect(self.screen, (40, 10, 10), pygame.Rect(bx, by, 36, 5))
            pygame.draw.rect(self.screen, (220, 40, 40), pygame.Rect(bx, by, hpw, 5))

        # crosshair + hit marker
        cx, cy = self.W // 2 + int(shake_x * 0.25), self.H // 2 + int(shake_y * 0.25)
        pygame.draw.line(self.screen, (220, 220, 220), (cx - 8, cy), (cx - 2, cy), 2)
        pygame.draw.line(self.screen, (220, 220, 220), (cx + 2, cy), (cx + 8, cy), 2)
        pygame.draw.line(self.screen, (220, 220, 220), (cx, cy - 8), (cx, cy - 2), 2)
        pygame.draw.line(self.screen, (220, 220, 220), (cx, cy + 2), (cx, cy + 8), 2)
        if self.hit_marker > 0:
            a = int(255 * self.hit_marker)
            pygame.draw.line(self.screen, (255, 255, 255, a), (cx - 14, cy - 14), (cx - 6, cy - 6), 3)
            pygame.draw.line(self.screen, (255, 255, 255, a), (cx + 14, cy - 14), (cx + 6, cy - 6), 3)
            pygame.draw.line(self.screen, (255, 255, 255, a), (cx - 14, cy + 14), (cx - 6, cy + 6), 3)
            pygame.draw.line(self.screen, (255, 255, 255, a), (cx + 14, cy + 14), (cx + 6, cy + 6), 3)

        # arma (overlay)
        self._draw_weapon(bob=bob, shake_x=shake_x, shake_y=shake_y)

        # HUD
        self._draw_hud()

        # minimapa
        self._draw_minimap()

        pygame.display.flip()

    def _draw_weapon(self, bob: float, shake_x: float, shake_y: float) -> None:
        w, h = 240, 170
        x = self.W // 2 - w // 2 + int(bob * 2) + int(shake_x * 0.4)
        y = self.H - h + int(abs(bob) * 2) + int(shake_y * 0.4)

        # base
        pygame.draw.rect(self.screen, (25, 25, 25), pygame.Rect(x, y, w, h), border_radius=10)
        pygame.draw.rect(self.screen, (80, 70, 70), pygame.Rect(x + 20, y + 40, w - 40, h - 60), border_radius=8)
        pygame.draw.rect(self.screen, (130, 120, 120), pygame.Rect(x + 35, y + 55, w - 70, h - 95), border_radius=6)
        # cano
        pygame.draw.rect(self.screen, (45, 45, 45), pygame.Rect(x + w // 2 - 20, y + 20, 40, 35), border_radius=6)
        pygame.draw.rect(self.screen, (15, 15, 15), pygame.Rect(x + w // 2 - 10, y + 18, 20, 20), border_radius=6)

        if self.fire_flash > 0:
            a = self.fire_flash
            fx = x + w // 2
            fy = y + 20
            r = int(45 * a)
            col = (255, int(220 * a), int(110 * a))
            pygame.draw.circle(self.screen, col, (fx, fy), r)

    def _draw_hud(self) -> None:
        hp = self.player.hp
        ammo = self.player.ammo
        alive = sum(1 for e in self.enemies if e.alive)

        txt = f"HP {hp:3d}   AMMO {ammo:3d}   ENEMIES {alive}"
        surf = self.font.render(txt, True, (230, 230, 230))
        bg = pygame.Surface((surf.get_width() + 14, surf.get_height() + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        self.screen.blit(bg, (12, self.H - 12 - bg.get_height()))
        self.screen.blit(surf, (19, self.H - 7 - surf.get_height()))

        hint = "WASD move | Mouse look (TAB) | Click shoot | SHIFT run | R +25 ammo | ESC sair"
        hs = pygame.font.SysFont("consolas", 14).render(hint, True, (190, 190, 190))
        self.screen.blit(hs, (12, 10))

        if hp <= 30:
            v = int(120 * (1 + math.sin(pygame.time.get_ticks() * 0.01)) / 2)
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((120, 0, 0, v))
            self.screen.blit(overlay, (0, 0))

    def _draw_minimap(self) -> None:
        scale = 8
        pad = 10
        mw = self.world.w * scale
        mh = self.world.h * scale
        x0 = self.W - mw - pad
        y0 = pad
        bg = pygame.Surface((mw + 2, mh + 2), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        self.screen.blit(bg, (x0 - 1, y0 - 1))

        for gy in range(self.world.h):
            for gx in range(self.world.w):
                if self.world.is_wall(gx, gy):
                    pygame.draw.rect(
                        self.screen,
                        (160, 80, 80),
                        pygame.Rect(x0 + gx * scale, y0 + gy * scale, scale, scale),
                    )

        # inimigos
        for e in self.enemies:
            if not e.alive:
                continue
            ex = x0 + int(e.x * scale)
            ey = y0 + int(e.y * scale)
            pygame.draw.circle(self.screen, (60, 200, 80), (ex, ey), 2)

        # player
        px = x0 + int(self.player.x * scale)
        py = y0 + int(self.player.y * scale)
        pygame.draw.circle(self.screen, (220, 220, 220), (px, py), 3)
        dx = int(math.cos(self.player.ang) * 6)
        dy = int(math.sin(self.player.ang) * 6)
        pygame.draw.line(self.screen, (220, 220, 220), (px, py), (px + dx, py + dy), 2)


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()

