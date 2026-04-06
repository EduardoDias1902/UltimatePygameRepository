import math
import random
import sys
import os
from dataclasses import dataclass

import pygame

def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v

def wrap_angle(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

@dataclass
class Player:
    x: float
    y: float
    ang: float
    hp: int = 100
    ammo: int = 50
    move_speed: float = 2.8
    rot_speed: float = 2.4

@dataclass
class Enemy:
    x: float
    y: float
    hp: int = 40
    max_hp: int = 40
    alive: bool = True
    cooldown: float = 0.0
    state: str = "idle"
    is_boss: bool = False
    scale: float = 1.0
    anim_timer: float = 0.0
    frame: int = 0
    subtype: str = "default"

@dataclass
class Particle:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    life: float

@dataclass
class HealthItem:
    x: float
    y: float
    active: bool = True
    timer: float = 0.0

@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    is_player: bool = False
    life: float = 5.0

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
        if gx >= len(self.grid[gy]):
            return "#"
        return self.grid[gy][gx]

    def is_wall(self, gx: int, gy: int) -> bool:
        return self.cell(gx, gy) != "."

    def is_blocked(self, x: float, y: float) -> bool:
        return self.is_wall(int(x), int(y))

def try_move(world: World, x: float, y: float, nx: float, ny: float, radius: float) -> tuple[float, float]:
    def blocked(px: float, py: float) -> bool:
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
    dx = x1 - x0
    dy = y1 - y0
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return True
    steps = max(1, int(dist * 12))
    for i in range(steps + 1):
        t = i / steps
        if world.is_blocked(x0 + dx * t, y0 + dy * t):
            return False
    return True

def load_gif(filepath) -> list[pygame.Surface]:
    frames = []
    try:
        from PIL import Image
        img = Image.open(filepath)
        for frame in range(getattr(img, "n_frames", 1)):
            img.seek(frame)
            rgba = img.convert("RGBA")
            data = rgba.tobytes()
            surf = pygame.image.fromstring(data, rgba.size, "RGBA")
            frames.append(surf)
    except Exception as e:
        print("PIL exception on GIF:", e)
    return frames

def generate_textures():
    img_dir = os.path.join(os.path.dirname(__file__), "images")
    wall_tex = pygame.Surface((64, 64))
    for y in range(64):
        for x in range(64):
            c = random.randint(80, 140)
            wall_tex.set_at((x, y), (c, c//2, c//3))
    for y in range(0, 64, 16):
        pygame.draw.line(wall_tex, (0,0,0), (0, y), (64, y), 2)
    for y in range(0, 64, 32):
        for x in range(0, 64, 16):
            pygame.draw.line(wall_tex, (0,0,0), (x, y), (x, y+16), 2)
        for x in range(8, 64, 16):
            pygame.draw.line(wall_tex, (0,0,0), (x, y+16), (x, y+32), 2)

    enemy_tex = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.circle(enemy_tex, (200, 30, 40), (32, 28), 24)
    pygame.draw.circle(enemy_tex, (40, 0, 0), (22, 22), 6)
    pygame.draw.circle(enemy_tex, (40, 0, 0), (42, 22), 6)
    pygame.draw.circle(enemy_tex, (255, 200, 0), (22, 22), 2)
    pygame.draw.circle(enemy_tex, (255, 200, 0), (42, 22), 2)
    pygame.draw.rect(enemy_tex, (255, 255, 255), (20, 40, 24, 8), border_radius=2)

    gif_path = os.path.join(os.path.dirname(__file__), "images", "skeleton.gif")
    tex_enemy_frames = load_gif(gif_path)
    if not tex_enemy_frames: tex_enemy_frames = [enemy_tex]

    gif_boss = os.path.join(os.path.dirname(__file__), "images", "BOSS.gif")
    tex_boss_frames = load_gif(gif_boss)
    if not tex_boss_frames: tex_boss_frames = [enemy_tex]

    gif_death = os.path.join(os.path.dirname(__file__), "images", "Death.gif")
    tex_death_frames = load_gif(gif_death)
    if not tex_death_frames: tex_death_frames = [enemy_tex]

    # Texturas de Chao e Teto Procedurais
    floor_tex = pygame.Surface((64, 64))
    ceiling_tex = pygame.Surface((64, 64))
    for y in range(64):
        for x in range(64):
            # Padrao de Chao
            cf = random.randint(40, 70)
            if x % 32 < 2 or y % 32 < 2: cf = 30
            floor_tex.set_at((x, y), (cf, cf, cf))
            # Padrao de Teto
            cc = random.randint(20, 40)
            if (x+y) % 16 < 2: cc = 50
            ceiling_tex.set_at((x, y), (cc, cc, cc+10))

    # Texturas de Selva
    wall_tex_jungle = pygame.Surface((64, 64))
    for y in range(64):
        for x in range(64):
            # Base marrom/verde para troncos e folhas
            cg = random.randint(30, 80)
            cb = random.randint(20, 50)
            wall_tex_jungle.set_at((x, y), (cb, cg, cb//2))
    # Desenhar vinhas e detalhes de madeira
    for _ in range(15):
        vx = random.randint(0, 60)
        vy = random.randint(0, 40)
        pygame.draw.rect(wall_tex_jungle, (20, 100, 20), (vx, vy, 4, 24), border_radius=2)

    floor_tex_jungle = pygame.Surface((64, 64))
    for y in range(64):
        for x in range(64):
            cg = random.randint(60, 120)
            floor_tex_jungle.set_at((x, y), (cg // 2, cg, cg // 3))
    for _ in range(40): # Grama
        gx, gy = random.randint(0, 63), random.randint(0, 63)
        pygame.draw.line(floor_tex_jungle, (20, 150, 20), (gx, gy), (gx, gy-3))

    ceiling_tex_jungle = pygame.Surface((64, 64))
    for y in range(64):
        for x in range(64):
            # Verde escuro/azul para copa
            cc = random.randint(10, 40)
            ceiling_tex_jungle.set_at((x, y), (cc, cc + 20, cc))
    for _ in range(20): # Folhas no teto
        fx, fy = random.randint(0, 63), random.randint(0, 63)
        pygame.draw.circle(ceiling_tex_jungle, (10, 60, 10), (fx, fy), random.randint(2, 5))

    gif_v2 = os.path.join(os.path.dirname(__file__), "images", "Slave nvl2.gif")
    tex_enemy_v2_frames = load_gif(gif_v2)
    if not tex_enemy_v2_frames: tex_enemy_v2_frames = [enemy_tex]

    gif_boss_v2 = os.path.join(os.path.dirname(__file__), "images", "Boss nvl2.gif")
    tex_boss_v2_frames = load_gif(gif_boss_v2)
    if not tex_boss_v2_frames: tex_boss_v2_frames = [enemy_tex]

    medkit_tex = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.rect(medkit_tex, (220, 220, 220), (16, 24, 32, 24), border_radius=4)
    pygame.draw.rect(medkit_tex, (200, 30, 30), (28, 28, 8, 16))
    pygame.draw.rect(medkit_tex, (200, 30, 30), (24, 32, 16, 8))
    pygame.draw.rect(medkit_tex, (100, 100, 100), (24, 18, 16, 6))

    def load_wep(idle_f, shoot_f):
        try:
            idle = pygame.image.load(os.path.join(img_dir, idle_f)).convert_alpha()
            shoot = pygame.image.load(os.path.join(img_dir, shoot_f)).convert_alpha()
            return idle, shoot
        except:
            s = pygame.Surface((240, 240), pygame.SRCALPHA)
            return s, s

    p_idle, p_shoot = load_wep("pistolIdle.png", "pistolShooting.png")
    s_idle, s_shoot = load_wep("ShootGunIdle.png", "ShootGunShotting.png")

    return (wall_tex, tex_enemy_frames, tex_boss_frames, tex_death_frames, medkit_tex, p_idle, p_shoot, s_idle, s_shoot, floor_tex, ceiling_tex,
            wall_tex_jungle, tex_enemy_v2_frames, tex_boss_v2_frames, floor_tex_jungle, ceiling_tex_jungle)

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Doom Pygame 2.5D")

        self.W, self.H = 960, 540
        self.screen = pygame.display.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 48, bold=True)

        self.render_scale = 2 
        self.fov = math.radians(66)
        
        (self.tex_wall_def, self.tex_enemy_def, self.tex_boss_def, self.tex_death_frames, self.tex_medkit, 
         self.p_idle, self.p_shoot, self.s_idle, self.s_shoot, self.tex_floor_def, self.tex_ceiling_def,
         self.tex_wall_jungle, self.tex_enemy_v2, self.tex_boss_v2, self.tex_floor_jungle, self.tex_ceiling_jungle) = generate_textures()
        
        self.tex_wall = self.tex_wall_def
        self.tex_enemy_frames = self.tex_enemy_def
        self.tex_boss_frames = self.tex_boss_def
        self.tex_floor = self.tex_floor_def
        self.tex_ceiling = self.tex_ceiling_def
        
        self.wep_msg_timer = 0.0

        self.maps = [
            [
                "########################",
                "#......#...............#",
                "#..##..#..##...#####...#",
                "#......#.......#.......#",
                "#..#.......#...#..###..#",
                "#..#..###..#...#.......#",
                "#..#.......#...#####...#",
                "#......#...........#...#",
                "########..##########...#",
                "#......................#",
                "#......#.......#.......#",
                "########################",
            ],
            [
                "########################",
                "#......................#",
                "#..#.#..#.#..#.#..#.#..#",
                "#......................#",
                "#..#.#..##....##..#.#..#",
                "#..#.#..#......#..#.#..#",
                "#.......#......#.......#",
                "#..#.#..##....##..#.#..#",
                "#......................#",
                "#..#.#..#.#..#.#..#.#..#",
                "#......................#",
                "########################",
            ],
            [
                "########################",
                "#......................#",
                "#.####################.#",
                "#.#..................#.#",
                "#.#.################.#.#",
                "#.#.#..............#.#.#",
                "#.#.#.############.#.#.#",
                "#.#.#................#.#",
                "#.#.##################.#",
                "#.#....................#",
                "#..####################.",
                "########################",
            ],
            [
                "########################",
                "#..........##..........#",
                "#...####...##...####...#",
                "####..##........##..####",
                "#...####........##...###",
                "#..........##..........#",
                "#..###..########..###..#",
                "#..###..########..###..#",
                "#..........##..........#",
                "####..############..####",
                "#..........##..........#",
                "########################",
            ]
        ]
        self.map_idx = 0
        self.world = World(self.maps[self.map_idx])

        self.player = Player(x=1.5, y=1.5, ang=0.0)
        self.player_radius = 0.2
        self.enemies: list[Enemy] = []
        self.particles: list[Particle] = []
        self.items: list[HealthItem] = []
        self.projectiles: list[Projectile] = []
        self._respawn_items()
        
        self.level = 0
        self.level_msg_timer = 0.0

        self.shake = 0.0
        self.weapon_t = 0.0
        self.firing = False
        self.fire_flash = 0.0
        self.hit_marker = 0.0
        self.mouse_look = True
        self.heal_flash = 0.0
        self.moving_right = False
        self.headshot_msg_timer = 0.0
        
        self.mira_x = self.W // 2
        self.mira_y = self.H // 2
        self.pitch = 0
        
        self._next_level()
        self.level_msg_timer = 0.0

        self._setup_mouse()

    def _respawn_items(self):
        self.items = []
        free_spots = []
        for gy in range(self.world.h):
            for gx in range(self.world.w):
                if not self.world.is_wall(gx, gy):
                    if math.hypot(gx+0.5 - self.player.x, gy+0.5 - self.player.y) > 2.0:
                        free_spots.append((gx + 0.5, gy + 0.5))
        if not free_spots: return
        for _ in range(4):
            spot = random.choice(free_spots)
            self.items.append(HealthItem(spot[0], spot[1]))
            
    def _get_map_colors(self):
        themes = [
            ((30, 25, 20), (20, 20, 30)),
            ((20, 50, 20), (10, 30, 10)), # Selva
            ((50, 30, 20), (30, 20, 20)),
            ((20, 10, 10), (50, 0, 0)),
        ]
        return themes[self.map_idx % len(themes)]

    def _next_level(self):
        self.level += 1
        if self.level == 4:
            self.wep_msg_timer = 3.0
            self.player.ammo += 100
        
        should_switch = False
        if self.level == 6:
            should_switch = True
        elif self.level == 16:
            should_switch = True
        elif self.level > 16 and (self.level - 1) % 5 == 0:
            should_switch = True
        
        if should_switch:
            self.map_idx = (self.map_idx + 1) % len(self.maps)
            
            # Switch textures based on map
            if self.map_idx == 1:
                self.tex_wall = self.tex_wall_jungle
                self.tex_enemy_frames = self.tex_enemy_v2
                self.tex_boss_frames = self.tex_boss_v2
                self.tex_floor = self.tex_floor_jungle
                self.tex_ceiling = self.tex_ceiling_jungle
            else:
                self.tex_wall = self.tex_wall_def
                self.tex_enemy_frames = self.tex_enemy_def
                self.tex_boss_frames = self.tex_boss_def
                self.tex_floor = self.tex_floor_def
                self.tex_ceiling = self.tex_ceiling_def

            self.world = World(self.maps[self.map_idx])
            self.player.x, self.player.y = 1.5, 1.5
            self._respawn_items()

        self.player.hp = min(150, self.player.hp + 50)
        self.player.ammo += 100
        self.enemies = []
        self.projectiles = []
        self.level_msg_timer = 3.0

        target_subtype = "v2" if self.map_idx == 1 else "default"
        
        free_spots = []
        for gy in range(self.world.h):
            for gx in range(self.world.w):
                if not self.world.is_wall(gx, gy):
                    if math.hypot(gx + 0.5 - self.player.x, gy + 0.5 - self.player.y) > 3.0:
                        free_spots.append((gx + 0.5, gy + 0.5))
        
        is_boss_lvl = False
        if self.map_idx != 1 and self.level % 5 == 0:
            is_boss_lvl = True
        elif self.map_idx == 1 and self.level == 15:
            is_boss_lvl = True

        if is_boss_lvl:
            if free_spots:
                spot = random.choice(free_spots)
                prev_lvl = max(1, self.level - 1)
                prev_num_enemies = 4 + prev_lvl * 2
                prev_hp_val = 20 + prev_lvl * 20
                hp_val = int(3 * (prev_num_enemies * prev_hp_val))
                self.enemies.append(Enemy(spot[0], spot[1], hp=hp_val, max_hp=hp_val, is_boss=True, scale=3.8, subtype=target_subtype))
        else:
            num_enemies = 4 + self.level * 2
            for _ in range(num_enemies):
                if not free_spots: break
                spot = random.choice(free_spots)
                hp_val = 20 + self.level * 20
                scale_val = 0.5 if target_subtype == "v2" else 1.0
                self.enemies.append(Enemy(spot[0], spot[1], hp=hp_val, max_hp=hp_val, subtype=target_subtype, scale=scale_val))

    def _setup_mouse(self):
        pygame.event.set_grab(self.mouse_look)
        pygame.mouse.set_visible(not self.mouse_look)
        pygame.mouse.get_rel()

    def toggle_mouse(self):
        self.mouse_look = not self.mouse_look
        self._setup_mouse()

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._next_level()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: sys.exit()
                if event.key == pygame.K_TAB: self.toggle_mouse()
                if event.key == pygame.K_r: self.player.ammo = min(200, self.player.ammo + 25)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._fire()

    def _update(self, dt: float):
        keys = pygame.key.get_pressed()

        self.level_msg_timer = max(0.0, self.level_msg_timer - dt)
        self.wep_msg_timer = max(0.0, self.wep_msg_timer - dt)
        self.headshot_msg_timer = max(0.0, self.headshot_msg_timer - dt)

        # Atualizar Projéteis
        for p in self.projectiles[:]:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.life -= dt
            if p.life <= 0 or self.world.is_blocked(p.x, p.y):
                if p in self.projectiles: self.projectiles.remove(p)
                continue
            
            if not p.is_player:
                if math.hypot(p.x - self.player.x, p.y - self.player.y) < 0.4:
                    self.player.hp -= 15
                    self.shake = min(1.0, self.shake + 0.5)
                    if p in self.projectiles: self.projectiles.remove(p)

        alive_count = sum(1 for e in self.enemies if e.state != "dying" and e.alive)
        if alive_count == 0 and self.player.hp > 0:
            self._next_level()

        if self.mouse_look:
            mx, my = pygame.mouse.get_rel()
            self.player.ang = wrap_angle(self.player.ang + mx * 0.0022)
            self.pitch = clamp(self.pitch - my * 1.5, -self.H // 2, self.H // 2)
            self.mira_x = self.W // 2
            self.mira_y = self.H // 2
        else:
            rot = (1.0 if keys[pygame.K_LEFT] else 0) - (1.0 if keys[pygame.K_RIGHT] else 0)
            self.player.ang = wrap_angle(self.player.ang + rot * self.player.rot_speed * dt)
            self.mira_x = self.W // 2
            self.mira_y = self.H // 2
            self.pitch = 0

        move = pygame.Vector2()
        fw = pygame.Vector2(math.cos(self.player.ang), math.sin(self.player.ang))
        rt = pygame.Vector2(fw.y, -fw.x)
        if keys[pygame.K_w]: move += fw
        if keys[pygame.K_s]: move -= fw
        self.moving_right = bool(keys[pygame.K_d])
        if self.moving_right: move -= rt
        if keys[pygame.K_a]: move += rt

        speed = self.player.move_speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]: speed *= 1.4

        if move.length_squared() > 0:
            move = move.normalize() * speed * dt
            self.player.x, self.player.y = try_move(self.world, self.player.x, self.player.y, self.player.x + move.x, self.player.y + move.y, self.player_radius)

        self.weapon_t += dt * (6.0 if move.length_squared() > 0 else 2.0)
        self.shake = max(0.0, self.shake - dt * 6.0)
        self.fire_flash = max(0.0, self.fire_flash - dt * 3.5)
        self.hit_marker = max(0.0, self.hit_marker - dt * 8.0)
        self.heal_flash = max(0.0, self.heal_flash - dt * 3.0)

        for p in self.particles[:]:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.z += p.vz * dt
            p.vz += 9.8 * dt
            p.life -= dt
            if p.life <= 0 or p.z > 0.5:
                self.particles.remove(p)

        px, py = self.player.x, self.player.y
        
        for it in self.items:
            if not it.active:
                it.timer -= dt
                if it.timer <= 0: it.active = True
            else:
                if math.hypot(it.x - px, it.y - py) < 0.6 and self.player.hp < 150:
                    self.player.hp = min(150, self.player.hp + 30)
                    it.active = False
                    it.timer = 20.0
                    self.heal_flash = 1.0 

        for e in self.enemies:
            if not e.alive: continue
            
            if e.state == "dying":
                e.anim_timer += dt
                if e.anim_timer > 0.015:
                    e.anim_timer = 0.0
                    e.frame += 1
                    if e.frame >= len(self.tex_death_frames):
                        e.alive = False
                continue

            e.cooldown = max(0.0, e.cooldown - dt)
            dx, dy = px - e.x, py - e.y
            dist = math.hypot(dx, dy)

            if dist < 12.0 and line_of_sight(self.world, e.x, e.y, px, py):
                e.state = "chase"
            elif dist > 15.0:
                e.state = "idle"

            if e.state == "chase" and dist > 1.2:
                e.anim_timer += dt
                if e.is_boss:
                    if e.anim_timer > 0.02:
                        e.anim_timer = 0.0
                        e.frame = (e.frame + 1) % max(1, len(self.tex_boss_frames))
                else:
                    anim_thresh = 0.06 if e.subtype == "v2" else 0.12
                    if e.anim_timer > anim_thresh:
                        e.anim_timer = 0.0
                        e.frame = (e.frame + 1) % max(1, len(self.tex_enemy_frames))

                vx, vy = dx / dist, dy / dist
                step = (1.5 if e.is_boss else 2.0) * dt
                nx, ny = e.x + vx * step, e.y + vy * step
                if not self.world.is_blocked(nx, ny):
                    e.x, e.y = nx, ny
                else: 
                    if not self.world.is_blocked(nx, e.y): e.x = nx
                    elif not self.world.is_blocked(e.x, ny): e.y = ny

            atk_dist = 8.5 if e.is_boss else 6.5
            if dist < atk_dist and e.cooldown <= 0.0 and line_of_sight(self.world, e.x, e.y, px, py):
                # Habilidade Especial Boss nlv2: Tiro de Energia
                if e.is_boss and e.subtype == "v2" and dist > 3.0:
                    e.cooldown = 1.5
                    v_dir = pygame.Vector2(px - e.x, py - e.y).normalize() * 6.5
                    self.projectiles.append(Projectile(e.x, e.y, v_dir.x, v_dir.y))
                else:
                    e.cooldown = random.uniform(0.6, 1.1) if e.is_boss else random.uniform(0.7, 1.3)
                    if random.random() < 0.55:
                        self.player.hp -= random.randint(15, 30) if e.is_boss else random.randint(2, 6)
                        self.shake = min(1.0, self.shake + (1.2 if e.is_boss else 0.6))

        if self.player.hp <= 0:
            self.player.x, self.player.y, self.player.ang = 2.5, 2.5, 0.0
            self.player.hp, self.player.ammo = 100, 50
            self.level = 0
            self._next_level()
            self.shake = self.fire_flash = 0.0

    def _fire(self):
        is_shotgun = self.level >= 4
        ammo_cost = 2 if is_shotgun else 1
        
        if self.player.ammo < ammo_cost: return
        self.player.ammo -= ammo_cost
        self.fire_flash, self.shake = 1.0, min(1.0, self.shake + (0.5 if is_shotgun else 0.3))
        
        best, best_dist = None, 1e9
        px, py, pa = self.player.x, self.player.y, self.player.ang
        
        cam_x_mira = (2 * self.mira_x / self.W - 1.0)
        ang_mira = pa + math.atan(cam_x_mira * math.tan(self.fov / 2))
        
        sy_curr = (random.random()-0.5)*8*(self.shake**2)

        best, best_dist, best_headshot = None, 1e9, False
        for e in self.enemies:
            if not e.alive or e.state == "dying": continue
            dist = math.hypot(e.x - px, e.y - py)
            if dist < 0.25: continue
            
            tolerance = 0.08 if is_shotgun else 0.05
            rel_ang = wrap_angle(math.atan2(e.y - py, e.x - px) - ang_mira)
            
            if abs(rel_ang) <= tolerance:
                size = (self.H / dist)
                hh = size * 0.7 * e.scale
                top = self.H / 2 - hh / 2 + sy_curr + self.pitch
                bottom = top + hh
                
                if top <= self.mira_y <= bottom:
                    if line_of_sight(self.world, px, py, e.x, e.y):
                        if dist < best_dist:
                            best, best_dist = e, dist
                            best_headshot = self.mira_y <= top + hh * 0.25

        if best:
            if not is_shotgun:
                dmg = random.randint(20, 30)
            else:
                lvl_bonus = (self.level - 4) * 50
                dmg = random.randint(150, 220) + lvl_bonus
            
            if best_headshot:
                dmg *= 2
                self.headshot_msg_timer = 1.0

            best.hp -= dmg
            self.hit_marker = 1.0
            p_count = 24 if best_headshot else 8
            for _ in range(p_count):
                self.particles.append(Particle(best.x, best.y, -0.2, (random.random()-0.5)*2, (random.random()-0.5)*2, -random.random()*2, 1.0))
            if best.hp <= 0:
                best.state = "dying"
                best.frame = 0
                best.anim_timer = 0.0

    def _render(self):
        bob = math.sin(self.weapon_t) * 2.5 + math.sin(self.weapon_t * 0.5) * 1.5
        sx, sy = (random.random()-0.5)*10*(self.shake**2), (random.random()-0.5)*8*(self.shake**2)
        px, py, pa = self.player.x, self.player.y, self.player.ang

        horizon = self.H // 2 + self.pitch
        floor_clr, ceil_clr = self._get_map_colors()
        pygame.draw.rect(self.screen, ceil_clr, (0, 0, self.W, horizon))
        pygame.draw.rect(self.screen, floor_clr, (0, horizon, self.W, self.H - horizon))

        res = 4 
        cos_pa, sin_pa = math.cos(pa), math.sin(pa)
        cos_pa_rt, sin_pa_rt = math.cos(pa + math.pi/2), math.sin(pa + math.pi/2)
        fov_w = math.tan(self.fov/2)

        for y in range(int(horizon), self.H, res):
            dy = max(1, y - (self.H // 2 + self.pitch))
            dist = (self.H * 0.5) / dy
            shade = max(0.1, 1.0 - dist / 11.0)
            if shade < 0.1: continue

            for x in range(0, self.W, res):
                cam_x = (2.0 * x / (self.W - 1) - 1.0) * fov_w
                world_x = px + dist * (cos_pa + cam_x * cos_pa_rt)
                world_y = py + dist * (sin_pa + cam_x * sin_pa_rt)
                
                tx, ty = int(world_x * 64) % 64, int(world_y * 64) % 64
                color = self.tex_floor.get_at((tx, ty))
                color = (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade))
                pygame.draw.rect(self.screen, color, (x, y, res, res))

        for y in range(0, int(horizon), res):
            dy = max(1, (self.H // 2 + self.pitch) - y)
            dist = (self.H * 0.5) / dy
            shade = max(0.1, 0.7 - dist / 20.0)
            if shade < 0.1: continue

            for x in range(0, self.W, res):
                cam_x = (2.0 * x / (self.W - 1) - 1.0) * fov_w
                world_x = px + dist * (cos_pa + cam_x * cos_pa_rt)
                world_y = py + dist * (sin_pa + cam_x * sin_pa_rt)
                
                tx, ty = int(world_x * 64) % 64, int(world_y * 64) % 64
                color = self.tex_ceiling.get_at((tx, ty))
                color = (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade))
                pygame.draw.rect(self.screen, color, (x, y, res, res))

        cols = self.W // self.render_scale
        zbuf = [0.0] * cols

        for col in range(cols):
            cam_x = (2 * col / max(1, cols - 1) - 1.0)
            ray_ang = pa + math.atan(cam_x * math.tan(self.fov / 2))
            dist, mx, my, side = cast_ray_dda(self.world, px, py, ray_ang, max_dist=32.0)
            wd = dist * math.cos(ray_ang - pa)
            zbuf[col] = wd
            
            wh = int(self.H / max(0.0001, wd))
            y0, x0 = (self.H - wh) // 2 + int(sy) + self.pitch, col * self.render_scale + int(sx)

            hx, hy = px + dist * math.cos(ray_ang), py + dist * math.sin(ray_ang)
            tex_x = int((hy - my if side == 0 else hx - mx) * 64) % 64
            strip = self.tex_wall.subsurface((tex_x, 0, 1, 64))
            
            shade = max(0.1, 1.0 - wd / 12.0)
            if side == 1: shade *= 0.7
            if shade < 1.0:
                overlay = pygame.Surface((1, 64))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(int((1-shade)*255))
                strip = strip.copy()
                strip.blit(overlay, (0,0))
                
            scale_strip = pygame.transform.scale(strip, (self.render_scale + 1, wh))
            self.screen.blit(scale_strip, (x0, y0))

        sprites = [(math.hypot(e.x-px, e.y-py), e.x, e.y, e) for e in self.enemies if e.alive]
        sprites += [(math.hypot(p.x-px, p.y-py), p.x, p.y, p) for p in self.particles]
        sprites += [(math.hypot(p.x-px, p.y-py), p.x, p.y, p) for p in self.projectiles]
        sprites += [(math.hypot(it.x-px, it.y-py), it.x, it.y, it) for it in self.items if it.active]
        sprites.sort(key=lambda t: -t[0])

        for dist, ex, ey, obj in sprites:
            rel = wrap_angle(math.atan2(ey - py, ex - px) - pa)
            if abs(rel) > self.fov * 0.7 or dist < 0.2: continue

            pt_x = (0.5 + rel / self.fov) * self.W + sx
            size = (self.H / dist)
            if isinstance(obj, (Enemy, HealthItem)):
                if isinstance(obj, Enemy):
                    if obj.state == "dying":
                        f_idx = min(obj.frame, max(0, len(self.tex_death_frames) - 1))
                        tex = self.tex_death_frames[f_idx]
                    elif obj.is_boss:
                        f_idx = obj.frame % max(1, len(self.tex_boss_frames))
                        tex = self.tex_boss_frames[f_idx]
                    else:
                        f_idx = obj.frame % max(1, len(self.tex_enemy_frames))
                        tex = self.tex_enemy_frames[f_idx]
                else:
                    tex = self.tex_medkit

                scale = obj.scale if isinstance(obj, Enemy) else 1.0
                hw, hh = size * 0.7 * scale, size * 0.7 * scale
                if hw < 1 or hh < 1: continue
                top, left = self.H / 2 - hh / 2 + sy + self.pitch, pt_x - hw / 2
                
                if isinstance(obj, HealthItem):
                    top += size * 0.15

                x_start, x_end = int(left), int(left + hw)
                
                if x_start >= self.W or x_end < 0: continue
                scaled_tex = pygame.transform.scale(tex, (int(hw), int(hh)))
                
                for x in range(max(0, x_start), min(self.W, x_end)):
                    ci = x // self.render_scale
                    if 0 <= ci < cols and zbuf[ci] < dist: continue
                    tex_x = min(x - x_start, int(hw) - 1)
                    strip = scaled_tex.subsurface((tex_x, 0, 1, int(hh)))
                    self.screen.blit(strip, (x, int(top)))

                if isinstance(obj, Enemy) and obj.state != "dying":
                    hp_ratio = max(0.0, obj.hp / obj.max_hp)
                    bar_w = int(hw * 0.8)
                    bar_h = max(2, int(size * 0.05))
                    bar_x = int(pt_x - bar_w / 2)
                    bar_y = int(top - bar_h - size * 0.05)
                    pygame.draw.rect(self.screen, (150, 0, 0), (bar_x, bar_y, bar_w, bar_h))
                    if obj.hp > 0:
                        pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

            elif isinstance(obj, Projectile):
                psize = max(4, int(size * 0.15))
                ptop = self.H / 2 + sy + self.pitch
                ci = int(pt_x) // self.render_scale
                if 0 <= ci < cols and dist < zbuf[ci]:
                    pygame.draw.circle(self.screen, (255, 255, 0), (int(pt_x), int(ptop)), psize)
                    pygame.draw.circle(self.screen, (255, 255, 255), (int(pt_x), int(ptop)), psize // 2)

            else: # Particle
                p = obj
                psize = max(2, int(size * 0.05))
                ptop = self.H / 2 + (p.z * size) + sy + self.pitch
                ci = int(pt_x) // self.render_scale
                if 0 <= ci < cols and dist < zbuf[ci]:
                    pygame.draw.rect(self.screen, (200, 20, 20), (pt_x, ptop, psize, psize))

        self._draw_weapon(bob, sx, sy)
        self._draw_hud()
        
        pad, s = 10, 6
        x0, y0 = self.W - self.world.w*s - pad, pad
        pygame.draw.rect(self.screen, (0,0,0), (x0-1, y0-1, self.world.w*s+2, self.world.h*s+2))
        for gy in range(self.world.h):
            for gx in range(self.world.w):
                if self.world.is_wall(gx, gy): pygame.draw.rect(self.screen, (160, 80, 80), (x0+gx*s, y0+gy*s, s, s))
        for e in self.enemies:
            if e.alive and e.state != "dying": 
                c = (255, 100, 0) if e.is_boss else (200, 40, 40)
                r = 4 if e.is_boss else 2
                pygame.draw.circle(self.screen, c, (x0+int(e.x*s), y0+int(e.y*s)), r)
        for it in self.items:
            if it.active: pygame.draw.circle(self.screen, (200, 200, 255), (x0+int(it.x*s), y0+int(it.y*s)), 2)
        px_m, py_m = x0+int(px*s), y0+int(py*s)
        pygame.draw.circle(self.screen, (220, 220, 220), (px_m, py_m), 3)
        pygame.draw.line(self.screen, (220, 220, 220), (px_m, py_m), (px_m+int(math.cos(pa)*5), py_m+int(math.sin(pa)*5)), 2)
        
        if self.level % 5 == 0 and self.level_msg_timer > 0:
            msg = self.big_font.render("BOSS LEVEL!", True, (255, 0, 0))
            self.screen.blit(msg, (self.W//2 - msg.get_width()//2, self.H//3))

        pygame.display.flip()

    def _draw_weapon(self, bob, sx, sy):
        if self.level <= 3:
            tex_idle, tex_shoot = self.p_idle, self.p_shoot
        else:
            tex_idle, tex_shoot = self.s_idle, self.s_shoot
            
        tex = tex_shoot if self.fire_flash > 0.1 else tex_idle
        
        if self.moving_right:
            tex = pygame.transform.flip(tex, True, False)
            
        orig_w, orig_h = tex.get_size()
        if orig_h == 0: orig_h = 1
        
        target_h = self.H * 0.7
        target_w = orig_w * (target_h / orig_h)
        
        bx = int(math.cos(self.weapon_t) * 15)
        by = int(bob * 10)
        
        x = (self.W - target_w) // 2 + bx + sx
        y = self.H - target_h + by + 20 + sy
        
        scaled_tex = pygame.transform.scale(tex, (int(target_w), int(target_h)))
        self.screen.blit(scaled_tex, (int(x), int(y)))

    def _draw_hud(self):
        txt = f"LEVEL {self.level} | HP {self.player.hp:3d} | MUNI {self.player.ammo:3d} | DEMONIOS {sum(1 for e in self.enemies if e.alive and e.state != 'dying')}"
        surf = self.font.render(txt, True, (255, 50, 50) if self.player.hp <= 30 else (230, 230, 230))
        self.screen.blit(surf, (20, self.H - 30))
        
        if self.level_msg_timer > 0 and self.level % 5 != 0:
            msg = self.big_font.render(f"NÍVEL {self.level}", True, (255, 215, 0))
            self.screen.blit(msg, (self.W//2 - msg.get_width()//2, self.H//4))

        if self.wep_msg_timer > 0:
            font = pygame.font.SysFont('Arial', 48, bold=True)
            msg = font.render("SHOTGUN DESBLOQUEADA!", True, (255, 255, 0))
            self.screen.blit(msg, (self.W//2 - msg.get_width()//2, self.H//2))

        if self.headshot_msg_timer > 0:
            msg = self.big_font.render("HEADSHOT!", True, (255, 0, 0))
            self.screen.blit(msg, (self.W//2 - msg.get_width()//2, self.H//4 + 50))

        if self.hit_marker > 0:
           pygame.draw.circle(self.screen, (255, 255, 255), (int(self.mira_x), int(self.mira_y)), 15, 2)
        else:
           # Mira padrão
           pygame.draw.circle(self.screen, (255, 255, 255), (int(self.mira_x), int(self.mira_y)), 2, 1)
           pygame.draw.line(self.screen, (255, 255, 255), (self.mira_x - 10, self.mira_y), (self.mira_x + 10, self.mira_y), 1)
           pygame.draw.line(self.screen, (255, 255, 255), (self.mira_x, self.mira_y - 10), (self.mira_x, self.mira_y + 10), 1)
           
        if self.player.hp <= 30:
            ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            ov.fill((120, 0, 0, int(60*(1+math.sin(pygame.time.get_ticks()*0.01)))))
            self.screen.blit(ov, (0, 0))
            
        if self.heal_flash > 0:
            ov = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            ov.fill((50, 200, 50, int(50 * self.heal_flash)))
            self.screen.blit(ov, (0, 0))

if __name__ == "__main__":
    Game().run()
