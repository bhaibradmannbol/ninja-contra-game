"""
Contra-style 2D Shooter Game - Full Version
Run with: python main.py
Controls: Arrow keys to move, Space to jump, Z to shoot, X for special weapon
"""

import pygame
import random
import sys
import os
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python Contra")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
DARK_GREEN = (34, 139, 34)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)

# Game settings
FPS = 60
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_STRENGTH = -15
BULLET_SPEED = 12
ENEMY_SPEED = 2
LEVEL_WIDTH = 2400  # 3 screens wide

clock = pygame.time.Clock()

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
BG_DIR = os.path.join(ASSETS_DIR, "backgrounds")
TILES_DIR = os.path.join(ASSETS_DIR, "tiles")


def load_image(name, size=None, fallback_color=BLUE):
    """Load image or create colored surface as fallback"""
    path = os.path.join(SPRITES_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        surf = pygame.Surface(size or (32, 32), pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf


def load_sound(name):
    """Load sound or return None"""
    path = os.path.join(SOUNDS_DIR, name)
    try:
        return pygame.mixer.Sound(path)
    except:
        return None


class SoundManager:
    def __init__(self):
        self.sounds = {
            'shoot': load_sound('shoot.wav'),
            'jump': load_sound('jump.wav'),
            'explosion': load_sound('explosion.wav'),
            'hit': load_sound('hit.wav'),
            'powerup': load_sound('powerup.wav'),
            'enemy_die': load_sound('enemy_die.wav'),
            'menu_select': load_sound('menu_select.wav'),
        }
        self.music_playing = False
        
    def play(self, name):
        if self.sounds.get(name):
            self.sounds[name].play()
    
    def play_music(self):
        music_path = os.path.join(SOUNDS_DIR, 'bgm.mp3')
        if os.path.exists(music_path) and not self.music_playing:
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except:
                pass


sound_manager = SoundManager()


class MainMenu:
    def __init__(self):
        self.title_font = pygame.font.Font(None, 80)
        self.menu_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.selected = 0
        self.menu_items = ['Start Game', 'Select Character', 'Quit']
        self.character_select = False
        self.selected_character = 1  # 1 or 2
        self.character_previews = self.load_character_previews()
        self.bg_offset = 0

    def load_character_previews(self):
        """Load preview images for character selection"""
        previews = {}
        for char_num in [1, 2]:
            char_dir = os.path.join(SPRITES_DIR, f'player{char_num}')
            path = os.path.join(char_dir, 'Idle__000.png')
            try:
                img = pygame.image.load(path).convert_alpha()
                previews[char_num] = pygame.transform.scale(img, (120, 120))
            except:
                surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                color = BLUE if char_num == 1 else PURPLE
                surf.fill(color)
                previews[char_num] = surf
        return previews

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if self.character_select:
                    if event.key == pygame.K_LEFT:
                        self.selected_character = 1
                        sound_manager.play('menu_select')
                    elif event.key == pygame.K_RIGHT:
                        self.selected_character = 2
                        sound_manager.play('menu_select')
                    elif event.key == pygame.K_RETURN:
                        self.character_select = False
                        sound_manager.play('menu_select')
                    elif event.key == pygame.K_ESCAPE:
                        self.character_select = False
                else:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.menu_items)
                        sound_manager.play('menu_select')
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.menu_items)
                        sound_manager.play('menu_select')
                    elif event.key == pygame.K_RETURN:
                        sound_manager.play('menu_select')
                        if self.selected == 0:  # Start Game
                            return 'start'
                        elif self.selected == 1:  # Select Character
                            self.character_select = True
                        elif self.selected == 2:  # Quit
                            return 'quit'
        return None

    def draw(self):
        # Animated background
        self.bg_offset = (self.bg_offset + 1) % 100
        for y in range(0, SCREEN_HEIGHT + 100, 100):
            for x in range(0, SCREEN_WIDTH + 100, 100):
                color = (30 + (x + y + self.bg_offset) % 20, 
                        20 + (x + y + self.bg_offset) % 15, 
                        40 + (x + y + self.bg_offset) % 25)
                pygame.draw.rect(screen, color, (x - self.bg_offset, y - self.bg_offset, 100, 100))
        
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        screen.blit(overlay, (0, 0))
        
        if self.character_select:
            self.draw_character_select()
        else:
            self.draw_main_menu()
        
        pygame.display.flip()

    def draw_main_menu(self):
        # Title
        title = self.title_font.render("NINJA CONTRA", True, RED)
        title_shadow = self.title_font.render("NINJA CONTRA", True, BLACK)
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3, 103))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Subtitle
        subtitle = self.small_font.render("Zombie Apocalypse", True, ORANGE)
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170))
        
        # Menu items
        for i, item in enumerate(self.menu_items):
            color = YELLOW if i == self.selected else WHITE
            text = self.menu_font.render(item, True, color)
            y = 280 + i * 60
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            
            # Selection indicator
            if i == self.selected:
                pygame.draw.polygon(screen, YELLOW, [
                    (SCREEN_WIDTH // 2 - text.get_width() // 2 - 30, y + 15),
                    (SCREEN_WIDTH // 2 - text.get_width() // 2 - 10, y + 5),
                    (SCREEN_WIDTH // 2 - text.get_width() // 2 - 10, y + 25)
                ])
        
        # Current character indicator
        char_text = self.small_font.render(f"Current: Ninja {self.selected_character}", True, GREEN)
        screen.blit(char_text, (SCREEN_WIDTH // 2 - char_text.get_width() // 2, 480))
        
        # Controls hint
        controls = self.small_font.render("Arrow Keys: Navigate | Enter: Select", True, GRAY)
        screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 40))

    def draw_character_select(self):
        # Title
        title = self.menu_font.render("SELECT CHARACTER", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        
        # Character boxes
        for i, char_num in enumerate([1, 2]):
            x = 200 + i * 250
            y = 200
            
            # Box
            box_color = YELLOW if char_num == self.selected_character else GRAY
            pygame.draw.rect(screen, box_color, (x - 10, y - 10, 170, 220), 3)
            
            # Character preview
            preview = self.character_previews.get(char_num)
            if preview:
                screen.blit(preview, (x + 25, y + 20))
            
            # Name
            name = self.small_font.render(f"Ninja {char_num}", True, WHITE)
            screen.blit(name, (x + 85 - name.get_width() // 2, y + 160))
        
        # Instructions
        hint = self.small_font.render("Left/Right: Select | Enter: Confirm | Esc: Back", True, GRAY)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 500))


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, rect):
        return rect.move(-self.camera.x, -self.camera.y)

    def update(self, target):
        x = target.rect.centerx - SCREEN_WIDTH // 2
        x = max(0, min(x, self.width - SCREEN_WIDTH))
        self.camera.x = x


class AnimatedSprite:
    def __init__(self, frames, frame_duration=100):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now
    
    def get_frame(self):
        return self.frames[self.current_frame]


class Player(pygame.sprite.Sprite):
    SPRITE_SIZE = (80, 80)  # Size to scale sprites to
    
    def __init__(self, x, y, character_num=1):
        super().__init__()
        self.character_num = character_num
        # Load ninja sprite animations
        self.load_animations()
        
        self.image = self.idle_frames_right[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.health = 100
        self.max_health = 100
        self.lives = 3
        self.shoot_cooldown = 0
        self.weapon = 'normal'  # normal, spread, rapid
        self.invincible = 0
        self.moving = False
        self.attacking = False
        self.attack_timer = 0
        
        # Animation state
        self.idle_anim = AnimatedSprite(self.idle_frames_right, 100)
        self.run_anim = AnimatedSprite(self.run_frames_right, 60)
        self.jump_anim = AnimatedSprite(self.jump_frames_right, 80)
        self.attack_anim = AnimatedSprite(self.attack_frames_right, 50)

    def load_animations(self):
        """Load all ninja animations"""
        char_dir = os.path.join(SPRITES_DIR, f'player{self.character_num}')
        
        # Idle animation (10 frames)
        self.idle_frames_right = []
        for i in range(10):
            img = self.load_sprite(char_dir, f'Idle__{i:03d}.png')
            self.idle_frames_right.append(img)
        self.idle_frames_left = [pygame.transform.flip(f, True, False) for f in self.idle_frames_right]
        
        # Run animation (10 frames)
        self.run_frames_right = []
        for i in range(10):
            img = self.load_sprite(char_dir, f'Run__{i:03d}.png')
            self.run_frames_right.append(img)
        self.run_frames_left = [pygame.transform.flip(f, True, False) for f in self.run_frames_right]
        
        # Jump animation (10 frames)
        self.jump_frames_right = []
        for i in range(10):
            img = self.load_sprite(char_dir, f'Jump__{i:03d}.png')
            self.jump_frames_right.append(img)
        self.jump_frames_left = [pygame.transform.flip(f, True, False) for f in self.jump_frames_right]
        
        # Attack/Throw animation (10 frames)
        self.attack_frames_right = []
        for i in range(10):
            img = self.load_sprite(char_dir, f'Throw__{i:03d}.png')
            self.attack_frames_right.append(img)
        self.attack_frames_left = [pygame.transform.flip(f, True, False) for f in self.attack_frames_right]

    def load_sprite(self, char_dir, filename):
        """Load a single sprite with fallback"""
        path = os.path.join(char_dir, filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, self.SPRITE_SIZE)
        except:
            surf = pygame.Surface(self.SPRITE_SIZE, pygame.SRCALPHA)
            color = BLUE if self.character_num == 1 else PURPLE
            surf.fill(color)
            return surf

    def update(self, platforms, level_width):
        keys = pygame.key.get_pressed()
        self.moving = False
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
            self.facing_right = False
            self.moving = True
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
            self.facing_right = True
            self.moving = True
        
        # Keep player in level bounds
        self.rect.x = max(0, min(self.rect.x, level_width - self.rect.width))
        
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
        
        # Ground collision
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True
        
        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= 1
            self.attacking = self.attack_timer > 0
        
        # Update animation based on state
        self.update_animation()
        
        # Cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1

    def update_animation(self):
        """Update current animation frame"""
        if self.attacking:
            self.attack_anim.frames = self.attack_frames_right if self.facing_right else self.attack_frames_left
            self.attack_anim.update()
            self.image = self.attack_anim.get_frame()
        elif not self.on_ground:
            self.jump_anim.frames = self.jump_frames_right if self.facing_right else self.jump_frames_left
            self.jump_anim.update()
            self.image = self.jump_anim.get_frame()
        elif self.moving:
            self.run_anim.frames = self.run_frames_right if self.facing_right else self.run_frames_left
            self.run_anim.update()
            self.image = self.run_anim.get_frame()
        else:
            self.idle_anim.frames = self.idle_frames_right if self.facing_right else self.idle_frames_left
            self.idle_anim.update()
            self.image = self.idle_anim.get_frame()

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            sound_manager.play('jump')

    def shoot(self):
        bullets = []
        cooldown = 15 if self.weapon == 'normal' else (5 if self.weapon == 'rapid' else 20)
        
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = cooldown
            self.attacking = True
            self.attack_timer = 20  # Attack animation duration
            self.attack_anim.current_frame = 0
            sound_manager.play('shoot')
            direction = 1 if self.facing_right else -1
            bullet_x = self.rect.right if self.facing_right else self.rect.left
            
            if self.weapon == 'spread':
                for angle in [-15, 0, 15]:
                    bullets.append(Bullet(bullet_x, self.rect.centery, direction, angle, self.character_num))
            else:
                bullets.append(Bullet(bullet_x, self.rect.centery, direction, 0, self.character_num))
        
        return bullets

    def take_damage(self, amount):
        if self.invincible == 0:
            self.health -= amount
            self.invincible = 60  # 1 second invincibility
            sound_manager.play('hit')
            if self.health <= 0:
                self.lives -= 1
                if self.lives > 0:
                    self.health = self.max_health
                    self.rect.x = 100
                    self.rect.y = SCREEN_HEIGHT - 150
                return self.lives <= 0
        return False

    def draw(self, surface, camera):
        draw_rect = camera.apply(self.rect)
        # Blink when invincible
        if self.invincible == 0 or self.invincible % 10 < 5:
            surface.blit(self.image, draw_rect)


class Bullet(pygame.sprite.Sprite):
    kunai_images = {}
    
    @classmethod
    def load_kunai(cls, character_num):
        if character_num not in cls.kunai_images:
            char_dir = os.path.join(SPRITES_DIR, f'player{character_num}')
            path = os.path.join(char_dir, 'Kunai.png')
            try:
                img = pygame.image.load(path).convert_alpha()
                cls.kunai_images[character_num] = pygame.transform.scale(img, (30, 10))
            except:
                cls.kunai_images[character_num] = None
    
    def __init__(self, x, y, direction, angle=0, character_num=1):
        super().__init__()
        Bullet.load_kunai(character_num)
        
        kunai = Bullet.kunai_images.get(character_num)
        if kunai:
            self.image = kunai.copy()
            if direction < 0:
                self.image = pygame.transform.flip(self.image, True, False)
            if angle != 0:
                self.image = pygame.transform.rotate(self.image, -angle * direction)
        else:
            self.image = pygame.Surface((12, 6), pygame.SRCALPHA)
            self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.angle = math.radians(angle)
        self.speed_x = BULLET_SPEED * math.cos(self.angle) * direction
        self.speed_y = BULLET_SPEED * math.sin(self.angle) * -direction
        self.x = float(x)
        self.y = float(y)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        if self.rect.right < 0 or self.rect.left > LEVEL_WIDTH or self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.kill()

    def draw(self, surface, camera):
        draw_rect = camera.apply(self.rect)
        if 0 <= draw_rect.x <= SCREEN_WIDTH:
            surface.blit(self.image, draw_rect)


class Enemy(pygame.sprite.Sprite):
    SPRITE_SIZE = (70, 70)
    
    def __init__(self, x, y, enemy_type='soldier'):
        super().__init__()
        self.enemy_type = enemy_type
        self.load_animations()
        
        if enemy_type == 'soldier':
            self.health = 2
            self.speed = ENEMY_SPEED
            self.shoot_interval = (90, 150)
        elif enemy_type == 'heavy':
            self.health = 4
            self.speed = ENEMY_SPEED * 0.6
            self.shoot_interval = (60, 100)
        elif enemy_type == 'turret':
            self.health = 5
            self.speed = 0
            self.shoot_interval = (40, 80)
        
        self.image = self.walk_frames_left[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.direction = -1
        self.shoot_timer = random.randint(*self.shoot_interval)
        self.patrol_start = x - 100
        self.patrol_end = x + 100
        self.attacking = False
        self.attack_timer = 0
        self.dying = False
        self.death_timer = 0
        
        # Animation
        self.walk_anim = AnimatedSprite(self.walk_frames_left, 80)
        self.idle_anim = AnimatedSprite(self.idle_frames_left, 100)
        self.attack_anim = AnimatedSprite(self.attack_frames_left, 60)
        self.dead_anim = AnimatedSprite(self.dead_frames_left, 80)

    def load_animations(self):
        """Load zombie animations"""
        # Randomly choose male or female zombie
        gender = random.choice(['male', 'female'])
        sprite_dir = os.path.join(SPRITES_DIR, f'enemy_{gender}')
        
        # Walk animation (10 frames)
        self.walk_frames_left = []
        for i in range(1, 11):
            img = self.load_enemy_sprite(sprite_dir, f'Walk ({i}).png')
            self.walk_frames_left.append(img)
        self.walk_frames_right = [pygame.transform.flip(f, True, False) for f in self.walk_frames_left]
        
        # Idle animation (15 frames)
        self.idle_frames_left = []
        for i in range(1, 16):
            img = self.load_enemy_sprite(sprite_dir, f'Idle ({i}).png')
            self.idle_frames_left.append(img)
        self.idle_frames_right = [pygame.transform.flip(f, True, False) for f in self.idle_frames_left]
        
        # Attack animation (8 frames)
        self.attack_frames_left = []
        for i in range(1, 9):
            img = self.load_enemy_sprite(sprite_dir, f'Attack ({i}).png')
            self.attack_frames_left.append(img)
        self.attack_frames_right = [pygame.transform.flip(f, True, False) for f in self.attack_frames_left]
        
        # Dead animation (12 frames)
        self.dead_frames_left = []
        for i in range(1, 13):
            img = self.load_enemy_sprite(sprite_dir, f'Dead ({i}).png')
            self.dead_frames_left.append(img)
        self.dead_frames_right = [pygame.transform.flip(f, True, False) for f in self.dead_frames_left]

    def load_enemy_sprite(self, sprite_dir, filename):
        """Load a single enemy sprite"""
        path = os.path.join(sprite_dir, filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, self.SPRITE_SIZE)
        except:
            surf = pygame.Surface(self.SPRITE_SIZE, pygame.SRCALPHA)
            surf.fill(RED)
            return surf

    def update(self, platforms, player_x):
        # Handle death animation
        if self.dying:
            self.dead_anim.update()
            self.image = self.dead_anim.get_frame()
            self.death_timer += 1
            if self.death_timer >= len(self.dead_frames_left) * 5:
                self.kill()
            return None
        
        if self.enemy_type != 'turret':
            # Move towards player if close, otherwise patrol
            if abs(self.rect.centerx - player_x) < 300:
                self.direction = 1 if player_x > self.rect.centerx else -1
            
            self.rect.x += self.speed * self.direction
            
            # Patrol bounds
            if self.rect.x < self.patrol_start or self.rect.x > self.patrol_end:
                self.direction *= -1
        
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Platform collision
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
        
        # Ground collision
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
        
        # Update animation
        self.update_animation()
        
        # Attack timer
        if self.attack_timer > 0:
            self.attack_timer -= 1
            self.attacking = self.attack_timer > 0
        
        # Zombies don't shoot - they're melee only
        return None

    def update_animation(self):
        """Update enemy animation"""
        if self.attacking:
            self.attack_anim.frames = self.attack_frames_right if self.direction > 0 else self.attack_frames_left
            self.attack_anim.update()
            self.image = self.attack_anim.get_frame()
        elif self.speed > 0:
            self.walk_anim.frames = self.walk_frames_right if self.direction > 0 else self.walk_frames_left
            self.walk_anim.update()
            self.image = self.walk_anim.get_frame()
        else:
            self.idle_anim.frames = self.idle_frames_right if self.direction > 0 else self.idle_frames_left
            self.idle_anim.update()
            self.image = self.idle_anim.get_frame()

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            sound_manager.play('enemy_die')
            self.dying = True
            self.dead_anim.current_frame = 0
            return False  # Don't kill immediately, play death animation
        return False

    def draw(self, surface, camera):
        draw_rect = camera.apply(self.rect)
        if -50 <= draw_rect.x <= SCREEN_WIDTH + 50:
            surface.blit(self.image, draw_rect)


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = BULLET_SPEED - 4

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > LEVEL_WIDTH:
            self.kill()

    def draw(self, surface, camera):
        draw_rect = camera.apply(self.rect)
        if 0 <= draw_rect.x <= SCREEN_WIDTH:
            pygame.draw.circle(surface, RED, draw_rect.center, 5)
            pygame.draw.circle(surface, ORANGE, draw_rect.center, 3)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        colors = {'spread': ORANGE, 'rapid': YELLOW, 'health': GREEN, 'life': RED}
        self.color = colors.get(power_type, WHITE)
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, 25, 25), border_radius=5)
        self.rect = self.image.get_rect(center=(x, y))
        self.float_offset = 0

    def update(self):
        self.float_offset += 0.1
        self.rect.y += int(math.sin(self.float_offset) * 0.5)

    def draw(self, surface, camera):
        draw_rect = camera.apply(self.rect)
        if 0 <= draw_rect.x <= SCREEN_WIDTH:
            pygame.draw.rect(surface, self.color, draw_rect, border_radius=5)
            # Letter indicator
            font = pygame.font.Font(None, 20)
            letter = self.power_type[0].upper()
            text = font.render(letter, True, BLACK)
            surface.blit(text, (draw_rect.centerx - 5, draw_rect.centery - 7))


TILES_DIR = os.path.join(ASSETS_DIR, "tiles")


class Platform(pygame.sprite.Sprite):
    # Class-level tile cache
    tile_images = {'graveyard': None, 'scifi': None}
    
    @classmethod
    def load_tiles(cls, theme='graveyard'):
        if cls.tile_images[theme] is None:
            cls.tile_images[theme] = {
                'left': None,
                'middle': None,
                'right': None,
                'single': None
            }
            
            if theme == 'graveyard':
                # Load graveyard tiles
                tile_files = {
                    'left': 'Tile (1).png',
                    'middle': 'Tile (2).png', 
                    'right': 'Tile (3).png',
                    'single': 'Tile (6).png'
                }
                tile_dir = TILES_DIR
            elif theme == 'scifi':
                # Load sci-fi tiles
                tile_files = {
                    'left': 'Tile (1).png',
                    'middle': 'Tile (2).png', 
                    'right': 'Tile (3).png',
                    'single': 'Tile (4).png'
                }
                tile_dir = os.path.join(TILES_DIR, 'scifi')
            
            for key, filename in tile_files.items():
                path = os.path.join(tile_dir, filename)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    cls.tile_images[theme][key] = pygame.transform.scale(img, (64, 64))
                except:
                    pass
    
    def __init__(self, x, y, width, height, theme='graveyard'):
        super().__init__()
        self.theme = theme
        Platform.load_tiles(theme)
        self.width = max(width, 64)
        self.height = max(height, 32)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.build_platform()

    def build_platform(self):
        """Build platform from tiles"""
        tile_size = 64
        num_tiles = max(1, self.width // tile_size)
        
        for i in range(num_tiles):
            tiles = Platform.tile_images[self.theme]
            if tiles and tiles['middle']:
                if num_tiles == 1:
                    tile = tiles['single'] or tiles['middle']
                elif i == 0:
                    tile = tiles['left'] or tiles['middle']
                elif i == num_tiles - 1:
                    tile = tiles['right'] or tiles['middle']
                else:
                    tile = tiles['middle']
                
                # Scale tile to fit height
                scaled = pygame.transform.scale(tile, (tile_size, self.height))
                self.image.blit(scaled, (i * tile_size, 0))
            else:
                # Fallback to colored rectangles
                color = BROWN if self.theme == 'graveyard' else GRAY
                pygame.draw.rect(self.image, color, (i * tile_size, 0, tile_size, self.height))

    def draw(self, surface, camera):
        draw_rect = camera.apply(self.rect)
        if -self.rect.width <= draw_rect.x <= SCREEN_WIDTH:
            surface.blit(self.image, draw_rect)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 15

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.kill()

    def draw(self, surface, camera):
        radius = int(10 + self.frame * 2)
        alpha = 255 - int(self.frame * 17)
        color = (255, max(0, 200 - self.frame * 15), 0)
        pos = camera.apply(pygame.Rect(self.x, self.y, 1, 1))
        pygame.draw.circle(surface, color, (pos.x, pos.y), radius)
        pygame.draw.circle(surface, YELLOW, (pos.x, pos.y), radius // 2)


class Background:
    def __init__(self, level_width, theme='graveyard'):
        self.level_width = level_width
        self.theme = theme
        self.has_image = False
        
        # Try to load theme-specific background
        if theme == 'graveyard':
            bg_path = os.path.join(BG_DIR, 'BG.png')
        elif theme == 'scifi':
            bg_path = os.path.join(BG_DIR, 'scifi_bg.png')
        else:
            bg_path = None
            
        if bg_path:
            try:
                self.bg_image = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.has_image = True
            except:
                self.has_image = False
        
        # Load decorative objects
        self.decorations = []
        self.load_decorations()

    def load_decorations(self):
        """Load theme-specific decorations"""
        if self.theme == 'graveyard':
            decoration_files = [
                ('Tree.png', 150, 200),
                ('TombStone (1).png', 50, 60),
                ('TombStone (2).png', 50, 70),
                ('DeadBush.png', 60, 50),
                ('Skeleton.png', 80, 60),
                ('Crate.png', 50, 50),
            ]
            sprite_dir = SPRITES_DIR
        elif self.theme == 'scifi':
            decoration_files = [
                ('Barrel (1).png', 40, 60),
                ('Barrel (2).png', 40, 60),
                ('Box.png', 50, 50),
                ('Saw.png', 60, 60),
                ('Switch (1).png', 30, 40),
                ('Switch (2).png', 30, 40),
            ]
            sprite_dir = os.path.join(SPRITES_DIR, 'scifi_objects')
        
        for filename, w, h in decoration_files:
            path = os.path.join(sprite_dir, filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (w, h))
                # Place multiple instances across the level
                for i in range(self.level_width // 400):
                    x = random.randint(i * 400, (i + 1) * 400)
                    self.decorations.append((img, x, SCREEN_HEIGHT - 50 - h, 0.7 + random.random() * 0.3))
            except:
                pass

    def draw(self, surface, camera):
        if self.has_image:
            # Parallax scrolling with theme background
            offset = int(camera.camera.x * 0.2) % SCREEN_WIDTH
            surface.blit(self.bg_image, (-offset, 0))
            surface.blit(self.bg_image, (SCREEN_WIDTH - offset, 0))
        else:
            # Procedural background based on theme
            if self.theme == 'graveyard':
                # Dark graveyard sky
                for y in range(SCREEN_HEIGHT):
                    ratio = y / SCREEN_HEIGHT
                    r = int(30 + 20 * ratio)
                    g = int(20 + 30 * ratio)
                    b = int(50 + 30 * ratio)
                    pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            elif self.theme == 'scifi':
                # Sci-fi space background
                for y in range(SCREEN_HEIGHT):
                    ratio = y / SCREEN_HEIGHT
                    r = int(10 + 30 * ratio)
                    g = int(20 + 40 * ratio)
                    b = int(60 + 50 * ratio)
                    pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
                
                # Add some stars
                for i in range(50):
                    x = (i * 137 + camera.camera.x * 0.1) % SCREEN_WIDTH
                    y = (i * 73) % (SCREEN_HEIGHT // 2)
                    pygame.draw.circle(surface, WHITE, (int(x), int(y)), 1)
        
        # Draw decorations with parallax
        for img, x, y, parallax in self.decorations:
            screen_x = x - camera.camera.x * parallax
            if -200 <= screen_x <= SCREEN_WIDTH + 200:
                surface.blit(img, (screen_x, y))


class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.width = LEVEL_WIDTH + (level_num - 1) * 400
        self.theme = 'graveyard' if level_num == 1 else 'scifi'
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.generate_level()

    def generate_level(self):
        # Platform generation based on level
        base_platforms = [
            (100, 480, 150, 20),
            (300, 400, 150, 20),
            (500, 320, 150, 20),
            (700, 400, 150, 20),
            (900, 480, 150, 20),
            (1100, 350, 150, 20),
            (1300, 280, 150, 20),
            (1500, 400, 150, 20),
            (1700, 480, 150, 20),
            (1900, 350, 150, 20),
            (2100, 280, 150, 20),
        ]
        
        for x, y, w, h in base_platforms:
            if x < self.width:
                self.platforms.add(Platform(x, y, w, h, self.theme))
        
        # Add more platforms for higher levels
        for i in range(self.level_num * 2):
            x = random.randint(200, self.width - 200)
            y = random.randint(200, 450)
            self.platforms.add(Platform(x, y, random.randint(100, 180), 20, self.theme))
        
        # Enemy generation
        enemy_count = 5 + self.level_num * 3
        for i in range(enemy_count):
            x = random.randint(400, self.width - 100)
            y = random.choice([SCREEN_HEIGHT - 90, 260, 330, 410])
            
            # Enemy type based on level
            if self.level_num >= 3 and random.random() < 0.2:
                enemy_type = 'turret'
            elif self.level_num >= 2 and random.random() < 0.3:
                enemy_type = 'heavy'
            else:
                enemy_type = 'soldier'
            
            self.enemies.add(Enemy(x, y, enemy_type))
        
        # Power-up generation
        powerup_types = ['spread', 'rapid', 'health', 'life']
        for i in range(2 + self.level_num):
            x = random.randint(300, self.width - 100)
            y = random.randint(200, 400)
            self.powerups.add(PowerUp(x, y, random.choice(powerup_types)))


class Game:
    def __init__(self, character_num=1):
        self.character_num = character_num
        self.level_num = 1
        self.level = Level(self.level_num)
        self.player = Player(100, SCREEN_HEIGHT - 150, character_num)
        self.camera = Camera(self.level.width, SCREEN_HEIGHT)
        self.background = Background(self.level.width, self.level.theme)
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.score = 0
        self.game_over = False
        self.level_complete = False
        self.paused = False
        self.return_to_menu = False
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        sound_manager.play_music()

    def next_level(self):
        self.level_num += 1
        self.level = Level(self.level_num)
        self.camera = Camera(self.level.width, SCREEN_HEIGHT)
        self.background = Background(self.level.width, self.level.theme)
        self.player.rect.x = 100
        self.player.rect.y = SCREEN_HEIGHT - 150
        self.player.weapon = 'normal'
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.explosions.empty()
        self.level_complete = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                if event.key == pygame.K_z:
                    bullets = self.player.shoot()
                    for bullet in bullets:
                        self.bullets.add(bullet)
                if event.key == pygame.K_r and self.game_over:
                    self.__init__(self.character_num)
                if event.key == pygame.K_RETURN and self.level_complete:
                    self.next_level()
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key == pygame.K_ESCAPE:
                    if self.paused or self.game_over:
                        self.return_to_menu = True
                    else:
                        self.paused = True
        return True

    def update(self):
        if self.game_over or self.paused or self.level_complete:
            return
        
        self.player.update(self.level.platforms, self.level.width)
        self.camera.update(self.player)
        
        # Update bullets
        for bullet in self.bullets:
            bullet.update()
        
        # Update enemies
        for enemy in list(self.level.enemies):
            enemy_bullet = enemy.update(self.level.platforms, self.player.rect.centerx)
            if enemy_bullet:
                self.enemy_bullets.add(enemy_bullet)
        
        # Update enemy bullets
        for bullet in self.enemy_bullets:
            bullet.update()
        
        # Update power-ups
        for powerup in self.level.powerups:
            powerup.update()
        
        # Update explosions
        for explosion in self.explosions:
            explosion.update()
        
        # Check bullet-enemy collisions
        for bullet in list(self.bullets):
            for enemy in list(self.level.enemies):
                if not enemy.dying and bullet.rect.colliderect(enemy.rect):
                    bullet.kill()
                    enemy.take_damage()
                    if enemy.dying:
                        self.explosions.add(Explosion(enemy.rect.centerx, enemy.rect.centery))
                        self.score += 100 * self.level_num
                    break
        
        # Check enemy bullet-player collisions
        for bullet in list(self.enemy_bullets):
            if bullet.rect.colliderect(self.player.rect):
                bullet.kill()
                if self.player.take_damage(20):
                    self.game_over = True
        
        # Check player-enemy collisions (melee damage)
        for enemy in self.level.enemies:
            if not enemy.dying and self.player.rect.colliderect(enemy.rect):
                if self.player.take_damage(15):  # Increased melee damage
                    self.game_over = True
        
        # Check power-up collisions
        for powerup in list(self.level.powerups):
            if self.player.rect.colliderect(powerup.rect):
                sound_manager.play('powerup')
                if powerup.power_type in ['spread', 'rapid']:
                    self.player.weapon = powerup.power_type
                elif powerup.power_type == 'health':
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif powerup.power_type == 'life':
                    self.player.lives += 1
                powerup.kill()
                self.score += 50
        
        # Check level completion (only count alive enemies)
        alive_enemies = [e for e in self.level.enemies if not e.dying]
        if len(alive_enemies) == 0:
            self.level_complete = True


    def draw(self):
        # Background
        self.background.draw(screen, self.camera)
        
        # Ground with tiles
        self.draw_ground()
        
        # Platforms
        for platform in self.level.platforms:
            platform.draw(screen, self.camera)
        
        # Power-ups
        for powerup in self.level.powerups:
            powerup.draw(screen, self.camera)
        
        # Player
        self.player.draw(screen, self.camera)
        
        # Bullets
        for bullet in self.bullets:
            bullet.draw(screen, self.camera)
        
        # Enemies
        for enemy in self.level.enemies:
            enemy.draw(screen, self.camera)
        
        # Enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(screen, self.camera)
        
        # Explosions
        for explosion in self.explosions:
            explosion.draw(screen, self.camera)
        
        # HUD
        self.draw_hud()
        
        # Game states
        if self.paused:
            self.draw_overlay("PAUSED", "Press P to continue")
        elif self.level_complete:
            self.draw_overlay(f"LEVEL {self.level_num} COMPLETE!", "Press ENTER for next level")
        elif self.game_over:
            self.draw_overlay("GAME OVER", f"Final Score: {self.score}  |  Press R to Restart")
        
        pygame.display.flip()

    def draw_ground(self):
        """Draw ground using tiles"""
        Platform.load_tiles(self.level.theme)
        ground_tile = Platform.tile_images[self.level.theme].get('middle')
        
        if ground_tile:
            tile_size = 64
            scaled_tile = pygame.transform.scale(ground_tile, (tile_size, 50))
            for x in range(0, SCREEN_WIDTH + tile_size, tile_size):
                screen.blit(scaled_tile, (x, SCREEN_HEIGHT - 50))
        else:
            # Fallback
            color = BROWN if self.level.theme == 'graveyard' else GRAY
            pygame.draw.rect(screen, color, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

    def draw_hud(self):
        # Health bar
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 204, 24))
        health_width = int(200 * (self.player.health / self.player.max_health))
        health_color = GREEN if self.player.health > 50 else (YELLOW if self.player.health > 25 else RED)
        pygame.draw.rect(screen, health_color, (12, 12, health_width, 20))
        pygame.draw.rect(screen, WHITE, (10, 10, 204, 24), 2)
        
        # Lives
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        screen.blit(lives_text, (10, 40))
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 70))
        
        # Level
        level_text = self.font.render(f"Level: {self.level_num}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 120, 10))
        
        # Weapon indicator
        weapon_text = self.font.render(f"Weapon: {self.player.weapon.upper()}", True, YELLOW)
        screen.blit(weapon_text, (SCREEN_WIDTH - 180, 40))
        
        # Enemies remaining
        enemies_text = self.font.render(f"Enemies: {len(self.level.enemies)}", True, RED)
        screen.blit(enemies_text, (SCREEN_WIDTH - 150, 70))
        
        # Controls hint
        controls = pygame.font.Font(None, 24).render(
            "Arrows: Move | Space: Jump | Z: Shoot | P: Pause", True, WHITE)
        screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 25))

    def draw_overlay(self, title, subtitle):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        title_text = self.big_font.render(title, True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 
                                 SCREEN_HEIGHT // 2 - 50))
        
        sub_text = self.font.render(subtitle, True, WHITE)
        screen.blit(sub_text, (SCREEN_WIDTH // 2 - sub_text.get_width() // 2, 
                               SCREEN_HEIGHT // 2 + 20))


def main():
    menu = MainMenu()
    game = None
    state = 'menu'  # 'menu' or 'game'
    running = True
    
    while running:
        if state == 'menu':
            result = menu.handle_events()
            if result == 'quit':
                running = False
            elif result == 'start':
                game = Game(menu.selected_character)
                state = 'game'
            menu.draw()
        
        elif state == 'game':
            running = game.handle_events()
            if game.return_to_menu:
                state = 'menu'
                game = None
            else:
                game.update()
                game.draw()
        
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
