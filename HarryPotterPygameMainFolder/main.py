from pygame import mixer
import pygame, sys, random, math, time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2

pygame.init()
pygame.font.init()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

thumbs_up_template = [4, 3, 2]

try:
    cap = cv2.VideoCapture(1)
except Exception as e:
    print(e)
finally:
    cap = cv2.VideoCapture(0)

desired_fps = 60
cap.set(cv2.CAP_PROP_FPS, desired_fps)

if not cap.set(cv2.CAP_PROP_FPS, desired_fps):
    print("Error: Could not set the desired frame rate.")

set_fps = cap.get(cv2.CAP_PROP_FPS)
print("Set frame rate:", set_fps)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Game Constants
GAME_FPS = 60
BACKGROUND_COLOR = (255, 255, 255)
PLAYER_SPEED = 10
ENEMY_SPEED = 10
ENEMY_SPAWN_INTERVAL = 30
ENEMY_SPAWN_DECREASE = 2
ENEMY_SPAWN_DECREASE_INTERVAL = 5000
ENEMY_START_SPAWN = 2
ENEMY_SPEED_INCREASE = 3
ENEMY_SPEED_INCREASE_INTERVAL = 10000
BULLET_SPEED = 16 * 2
BULLET_SPEED_INCREASE = 8
BULLET_SPEED_INCREASE_INTERVAL = 5000
BULLET_FIRE_DELAY = 30
BULLET_FIRE_DELAY_INCREASE = 2
BULLET_FIRE_DELAY_INCREASE_INTERVAL = 5000
MAX_BULLET_COUNT = 9999
BULLET_RELOAD_AMOUNT = 2
BULLET_AUTO_ATTACK_RADIUS = 250
OBJECTIVE_HIT_POINTS = 100
MENU_BACKGROUND_COLOR = (15, 15, 15)
MENU_TEXT_COLOR = (255, 255, 255)
MENU_FONT_SIZE = 48
ABLE_TO_ATTACK_DELAY = 10

# Create the screen
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h

# Font Variable(s)
pixel_text_large = pygame.font.Font("Minecraft.ttf", MENU_FONT_SIZE)
pixel_text_mid = pygame.font.Font("Minecraft.ttf", MENU_FONT_SIZE // 2)
pixel_text_small = pygame.font.Font("Minecraft.ttf", MENU_FONT_SIZE // 2 // 2)

# Image Variables
PLAYER_IDLE_PATH = "HarryPotterSprite/PlayerSprite/player_idle.png"
PLAYER_LEFT_PATH = "HarryPotterSprite/PlayerSprite/player_move_left.png"
PLAYER_RIGHT_PATH = "HarryPotterSprite/PlayerSprite/player_move_right.png"
PLAYER_WEAPON_PATH = "HarryPotterSprite/PlayerWeaponSprite/player_weapon.png"
PLAYER_PROJECTILE_PATH = "HarryPotterSprite/PlayerProjectileSprite/projectile_magic.png"
ENEMY_DEATH_PATH = "HarryPotterSprite/GhostSprite/ghost_death.png"
ENEMY_SPAWN_PATH = "HarryPotterSprite/GhostSprite/ghost_spawn.png"
ENEMY_MOVE_LEFT_PATH = "HarryPotterSprite/GhostSprite/ghost_move_left.png"
ENEMY_MOVE_RIGHT_PATH = "HarryPotterSprite/GhostSprite/ghost_move_right.png"
OBJECTIVE_FULL_PATH = "HarryPotterSprite/ObjectiveSprite/objective_full.png"
OBJECTIVE_HALF_PATH = "HarryPotterSprite/ObjectiveSprite/objective_half.png"
OBJECTIVE_QUARTER_PATH = "HarryPotterSprite/ObjectiveSprite/objective_quarter.png"

player_idle = pygame.image.load(PLAYER_IDLE_PATH).convert_alpha()
player_left = pygame.image.load(PLAYER_LEFT_PATH).convert_alpha()
player_right = pygame.image.load(PLAYER_RIGHT_PATH).convert_alpha()
player_weapon = pygame.image.load(PLAYER_WEAPON_PATH).convert_alpha()
player_projectile = pygame.image.load(PLAYER_PROJECTILE_PATH).convert_alpha()
enemy_death = pygame.image.load(ENEMY_DEATH_PATH).convert_alpha()
enemy_spawn = pygame.image.load(ENEMY_SPAWN_PATH).convert_alpha()
enemy_move_left = pygame.image.load(ENEMY_MOVE_LEFT_PATH).convert_alpha()
enemy_move_right = pygame.image.load(ENEMY_MOVE_RIGHT_PATH).convert_alpha()
objective_full = pygame.image.load(OBJECTIVE_FULL_PATH).convert_alpha()
objective_half = pygame.image.load(OBJECTIVE_HALF_PATH).convert_alpha()
objective_quarter = pygame.image.load(OBJECTIVE_QUARTER_PATH).convert_alpha()

health_bar_images = [pygame.image.load(f"HarryPotterSprite/UPDATED Health Bar/hp{i}.png").convert_alpha() for i in range(1, 11)]
pygame_background_image = pygame.image.load("bg2.png").convert_alpha()

# Pre-scale all necessary images once
scaled_player_idle = pygame.transform.scale(player_idle, (50, 75))
scaled_player_left = pygame.transform.scale(player_left, (50, 75))
scaled_player_right = pygame.transform.scale(player_right, (50, 75))
scaled_player_weapon = pygame.transform.scale(player_weapon, (25, 25))
scaled_player_weapon_flip = pygame.transform.flip(scaled_player_weapon, True, False)
scaled_player_projectile = pygame.transform.scale(player_projectile, (10, 10))
scaled_enemy_spawn = pygame.transform.scale(enemy_spawn, (100, 100))
scaled_enemy_death = pygame.transform.scale(enemy_death, (100, 100))
scaled_enemy_move_left = pygame.transform.scale(enemy_move_left, (100, 100))
scaled_enemy_move_right = pygame.transform.scale(enemy_move_right, (100, 100))
scaled_objective_full = pygame.transform.scale(objective_full, (50, 50))
scaled_objective_half = pygame.transform.scale(objective_half, (50, 50))
scaled_objective_quarter = pygame.transform.scale(objective_quarter, (50, 50))
scaled_health_bars = [pygame.transform.scale(image, (screen_width // 2 // 2, 480 // 2 // 2 // 2)) for image in health_bar_images]

# Sound Effects Variables
pygame_background_music = pygame.mixer.Sound("HarryPotterSFX/pygame_background_music.mp3")
pygame_gameover_background_music = pygame.mixer.Sound("HarryPotterSFX/pygame_background_gameover.mp3")
player_movement_sfx = pygame.mixer.Sound("HarryPotterSFX/player_movement.mp3")
player_attack_sfx = pygame.mixer.Sound("HarryPotterSFX/player_attack_sfx.mp3")
enemy_spawn_sfx = pygame.mixer.Sound("HarryPotterSFX/enemy_spawn_sfx.mp3")
enemy_death_sfx = pygame.mixer.Sound("HarryPotterSFX/enemy_death_sfx.mp3")

# Menu Class
class Menu:
    def __init__(self, player):
        self.font = pixel_text_mid
        self.red_box = pygame.Rect(0, 0, 200, 50)
        self.red_box.center = (screen_width // 2, screen_height // 2 + 225)
        self.player = player

    def draw(self, screen):
        screen.fill(MENU_BACKGROUND_COLOR)
        harry_text = self.font.render("HARRY POTTER", True, MENU_TEXT_COLOR)
        and_text = self.font.render("AND THE", True, MENU_TEXT_COLOR)
        stone_text = self.font.render("SORCERER STONE", True, MENU_TEXT_COLOR)
        play_text = self.font.render("> PLAY <", True, MENU_TEXT_COLOR)
        harry_text_rect = harry_text.get_rect(center=(screen_width // 2, screen_height // 2))
        and_text_rect = and_text.get_rect(center=(screen_width // 2, screen_height // 2))
        stone_text_rect = stone_text.get_rect(center=(screen_width // 2, screen_height // 2))
        red_box_center = self.red_box.center
        play_text_rect = play_text.get_rect(center=red_box_center)
        screen.blit(harry_text, (harry_text_rect[0], harry_text_rect[1] - 300))
        screen.blit(and_text, (and_text_rect[0], and_text_rect[1] - 300 + MENU_FONT_SIZE))
        screen.blit(stone_text, (stone_text_rect[0], stone_text_rect[1] - 300 + MENU_FONT_SIZE * 2))
        screen.blit(play_text, play_text_rect.topleft)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.red_box.collidepoint(event.pos):
                    return "PLAY"
        if self.player.rect.colliderect(self.red_box):
            return "PLAY"
        else:
            return None

# Gameover Menu
class GameOverMenu:
    def __init__(self, player):
        self.font = pixel_text_mid
        self.font_text = pixel_text_small
        self.red_box = pygame.Rect(0, 0, 200, 50)
        self.red_box.center = (screen_width // 2, screen_height // 2 - 150)
        self.player = player

    def draw(self, screen):
        screen.fill(MENU_BACKGROUND_COLOR)
        replay_text = self.font.render("> REPLAY <", True, MENU_TEXT_COLOR)
        game_over_text = self.font.render("GAME OVER!", True, MENU_TEXT_COLOR)
        player_score_text = self.font.render(f"Your Score: {player.score}", True, MENU_TEXT_COLOR)
        developers_text = self.font_text.render("Developers:", True, MENU_TEXT_COLOR)
        supervisor = self.font_text.render("De La Cruz, Joseph Andrean - LEAD DEVELOPER", True, MENU_TEXT_COLOR)
        back_game_dev_0 = self.font_text.render("Allado, Christian Jay - PROJECT MANAGER", True, MENU_TEXT_COLOR)
        back_game_dev_1 = self.font_text.render("Pahilga, Ian Troy - DEVELOPER", True, MENU_TEXT_COLOR)
        game_dev = self.font_text.render("Gesulgon, Shon Mikhael - CORE DEVELOPER", True, MENU_TEXT_COLOR)
        creative_text = self.font_text.render("Creatives:", True, MENU_TEXT_COLOR)
        sprite_img = self.font_text.render("Chua, Markuly - SPRITE DESIGN", True, MENU_TEXT_COLOR)
        background_img = self.font_text.render("Gepes, Alexandra Cristina - BACKGROUND DESIGN", True, MENU_TEXT_COLOR)
        game_sfx = self.font_text.render("Leetian, Diego Paul - SFX DESIGN", True, MENU_TEXT_COLOR)
        gdsc_text = self.font.render("Google Developer Student Clubs", True, MENU_TEXT_COLOR)
        usa_text = self.font_text.render("University of San Agustin", True, MENU_TEXT_COLOR)
        replay_text_rect = replay_text.get_rect(center=self.red_box.center)
        game_over_text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
        player_score_text_rect = player_score_text.get_rect(center=(screen_width // 2, screen_height // 2))
        developers_text_rect = developers_text.get_rect(topleft=(50, 50))
        supervisor_rect = supervisor.get_rect(topleft=(50, 50))
        back_game_dev_0_rect = back_game_dev_0.get_rect(topleft=(50, 50))
        back_game_dev_1_rect = back_game_dev_1.get_rect(topleft=(50, 50))
        game_dev_rect = game_dev.get_rect(topleft=(50, 50))
        creative_text_rect = creative_text.get_rect(topleft=(50, 50))
        sprite_img_rect = sprite_img.get_rect(topleft=(50, 50))
        background_img_rect = background_img.get_rect(topleft=(50, 50))
        game_sfx_rect = game_sfx.get_rect(topleft=(50, 50))
        gdsc_text_rect = gdsc_text.get_rect(bottomleft=(50, screen_height - 50))
        usa_text_rect = usa_text.get_rect(bottomleft=(50, screen_height - 50))

        screen.blit(replay_text, replay_text_rect.topleft)
        screen.blit(game_over_text, (game_over_text_rect[0], game_over_text_rect[1] + 250))
        screen.blit(player_score_text, (player_score_text_rect[0], player_score_text_rect[1] + 150))
        screen.blit(developers_text, (developers_text_rect[0], developers_text_rect[1]))
        screen.blit(supervisor, (supervisor_rect[0], supervisor_rect[1] + MENU_FONT_SIZE))
        screen.blit(back_game_dev_0, (back_game_dev_0_rect[0], back_game_dev_0_rect[1] + MENU_FONT_SIZE * 2))
        screen.blit(back_game_dev_1, (back_game_dev_1_rect[0], back_game_dev_1_rect[1] + MENU_FONT_SIZE * 3))
        screen.blit(game_dev, (game_dev_rect[0], game_dev_rect[1] + MENU_FONT_SIZE * 4))
        screen.blit(creative_text, (creative_text_rect[0], creative_text_rect[1] + MENU_FONT_SIZE * 7))
        screen.blit(sprite_img, (sprite_img_rect[0], sprite_img_rect[1] + MENU_FONT_SIZE * 8))
        screen.blit(background_img, (background_img_rect[0], background_img_rect[1] + MENU_FONT_SIZE * 9))
        screen.blit(game_sfx, (game_sfx_rect[0], game_sfx_rect[1] + MENU_FONT_SIZE * 10))
        screen.blit(gdsc_text, (gdsc_text_rect[0], gdsc_text_rect[1] - MENU_FONT_SIZE))
        screen.blit(usa_text, (usa_text_rect[0], usa_text_rect[1]))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.red_box.collidepoint(event.pos):
                    return "REPLAY"
        if self.player.rect.colliderect(self.red_box):
            return "REPLAY"
        else:
            return None

# Player Class
class Player:
    def __init__(self):
        self.image_idle = scaled_player_idle
        self.image_left = scaled_player_left
        self.image_right = scaled_player_right
        self.image = scaled_player_idle
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.score = 0
        self.bullet_count = MAX_BULLET_COUNT
        self.bullet_fire_delay = 0
        self.gun = Weapon()

    def comvis(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def move(self, cv_x, cv_y):
        min_x = 0
        max_x = screen_width - 50
        min_y = 100
        max_y = screen_height - 75
        new_x = self.rect.x + cv_x
        new_y = self.rect.y + cv_y
        new_x = max(min_x, min(max_x, new_x))
        new_y = max(min_y, min(max_y, new_y))
        self.rect.x = new_x
        self.rect.y = new_y
        screen_width_mid = screen_width // 2
        if self.rect.centerx < screen_width_mid:
            self.image = self.image_left
        elif self.rect.centerx > screen_width_mid:
            self.image = self.image_right
        else:
            self.image = self.image_idle
        self.gun.rect.center = (self.rect.centerx, self.rect.centery)

    def auto_attack(self, enemies_group):
        for enemy in enemies_group:
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance <= BULLET_AUTO_ATTACK_RADIUS:
                if self.bullet_fire_delay == 0 and self.bullet_count > 0:
                    bullet = Bullet(self.rect.centerx - 5, self.rect.centery - 5, enemy.rect.centerx, enemy.rect.centery)
                    bullets.add(bullet)
                    self.bullet_fire_delay = BULLET_FIRE_DELAY
                    self.bullet_count -= 1
                    player_attack_sfx.play()

    def update(self, cv_x, cv_y):
        self.move(cv_x, cv_y)
        if self.bullet_fire_delay > 0:
            self.bullet_fire_delay -= 1

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.gun.draw(screen)

# Weapon Class
class Weapon:
    def __init__(self):
        self.original_player_weapon_flip = scaled_player_weapon_flip
        self.original_player_weapon = scaled_player_weapon
        self.image = self.original_player_weapon_flip
        self.rect = self.image.get_rect()

    def move(self, cv_x, cv_y):
        min_x = 0
        max_x = screen_width - 50
        min_y = 0
        max_y = screen_height - 75
        new_x = self.rect.x + cv_x
        new_y = self.rect.y + cv_y
        new_x = max(min_x, min(max_x, new_x))
        new_y = max(min_y, min(max_y, new_y))
        self.rect.x = new_x
        self.rect.y = new_y
        screen_width_mid = screen_width // 2
        if self.rect.centerx < screen_width_mid:
            self.image = self.original_player_weapon_flip
        elif self.rect.centerx > screen_width_mid:
            self.image = self.original_player_weapon
        else:
            self.image = self.original_player_weapon_flip

    def update(self, cv_x, cv_y):
        self.move(cv_x, cv_y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Objective Class
class Objective:
    def __init__(self):
        self.ruby = scaled_objective_full
        self.ruby2 = scaled_objective_half
        self.ruby3 = scaled_objective_quarter
        self.rect = pygame.Rect(screen_width // 2 - 33, screen_height // 2 - 33, 50, 50)
        self.bRect = pygame.Rect(screen_width // 2 - 485 / 2, 10, screen_width // 2, 50)
        self.bar_1, self.bar_2, self.bar_3, self.bar_4, self.bar_5, self.bar_6, self.bar_7, self.bar_8, self.bar_9, self.bar_10 = scaled_health_bars
        self.bar_image = self.bar_10
        self.health = OBJECTIVE_HIT_POINTS
        self.Brect = self.bar_image.get_rect(midtop=(screen_width // 2, 10))

    def update(self):
        health_mapping = {
            100: (self.bar_10, self.ruby),
            90: (self.bar_9, None),
            80: (self.bar_8, None),
            70: (self.bar_7, None),
            60: (self.bar_6, None),
            50: (self.bar_5, self.ruby2),
            40: (self.bar_4, None),
            30: (self.bar_3, None),
            20: (self.bar_2, self.ruby3),
            10: (self.bar_1, None),
        }
        for health_value, (bar, image) in health_mapping.items():
            if self.health >= health_value:
                self.bar_image = bar
                if image:
                    self.image = image
                return
        self.bar_image = self.bar_1
        self.image = self.ruby3

    def draw(self, screen):
        screen.blit(self.bar_image, self.Brect)
        screen.blit(self.image, self.rect)

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.spawn_image = scaled_enemy_spawn
        self.death_image = scaled_enemy_death
        self.walk_left_image = scaled_enemy_move_left
        self.walk_right_image = scaled_enemy_move_right
        self.image = self.spawn_image
        
        spawn_quadrant = random.randint(1, 4)
        if spawn_quadrant == 1: # NW
            spawn_x = random.randint(0, screen_width // 2 - (10 * 5))
            spawn_y = random.randint(0, screen_height // 2 - (10 * 5))
        elif spawn_quadrant == 2: # NE
            spawn_x = random.randint(screen_width // 2 + (10 * 5), screen_width)
            spawn_y = random.randint(0, screen_height // 2 + (10 * 5))
        elif spawn_quadrant == 3: #SW
            spawn_x = random.randint(0, screen_width // 2 - (10 * 5))
            spawn_y = random.randint(screen_height // 2 + (10 * 5), screen_height)
        else: #SE
            spawn_x = random.randint(screen_width // 2 + (10 * 5), screen_width)
            spawn_y = random.randint(screen_height // 2 + (10 * 5), screen_height)

        self.rect = pygame.Rect(spawn_x, spawn_y, 75, 75)
        self.is_alive = True
        self.disappear_timer = 0
        self.start_spawn_timer = ENEMY_START_SPAWN
        self.can_move = False
        self.spawn_sound_played = False

    def move_towards_objective(self, objective):
        if self.can_move:
            dx = objective.rect.x - self.rect.x
            dy = objective.rect.y - self.rect.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                self.rect.x += ENEMY_SPEED * dx / distance
                self.rect.y += ENEMY_SPEED * dy / distance

    def take_damage(self):
        self.is_alive = False
        self.image = self.death_image
        self.disappear_timer = 100

    def update(self, objective):
        if self.is_alive:
            if self.start_spawn_timer > 0:
                self.start_spawn_timer -= 1
                if self.start_spawn_timer <= 0:
                    self.can_move = True
                    if not self.spawn_sound_played:
                        enemy_spawn_sfx.play()
                        self.spawn_sound_played = True
            if self.can_move:
                self.move_towards_objective(objective)
                if self.rect.x < screen_width // 2:
                    self.image = self.walk_right_image
                else:
                    self.image = self.walk_left_image
        elif self.disappear_timer > 0:
            self.disappear_timer -= 1
            if self.disappear_timer <= 0:
                self.kill() # This automatically removes the sprite from all groups

# Projectile Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = scaled_player_projectile
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.target_x = target_x
        self.target_y = target_y
        self.angle = math.atan2(target_y - y, target_x - x)

    def update(self):
        self.rect.x += BULLET_SPEED * math.cos(self.angle)
        self.rect.y += BULLET_SPEED * math.sin(self.angle)
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# Game Timer Class
class Timer:
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False

    def start(self):
        self.start_time = time.time()
        self.running = True

    def stop(self):
        self.elapsed_time += time.time() - self.start_time
        self.running = False

    def reset(self):
        self.elapsed_time = 0
        self.running = False
        self.start_time = time.time() # Reset start_time to avoid large initial elapsed time on restart

    def update(self):
        if self.running:
            current_time = time.time()
            self.elapsed_time = current_time - self.start_time

    def draw(self, screen):
        if self.running:
            minutes = int(self.elapsed_time // 60)
            seconds = int(self.elapsed_time % 60)
            time_text = f"Time: {minutes:02d}:{seconds:02d}"
            text_surface = pixel_text_large.render(time_text, True, (255, 255, 255))
            screen.blit(text_surface, (50, screen_height - 75))

def reset_game():
    global ENEMY_SPEED, ENEMY_SPAWN_INTERVAL, ENEMY_SPAWN_DECREASE
    global BULLET_FIRE_DELAY, BULLET_FIRE_DELAY_INCREASE
    global BULLET_SPEED, BULLET_SPEED_INCREASE
    global ABLE_TO_ATTACK_DELAY
    
    player.score = 0
    player.bullet_count = MAX_BULLET_COUNT
    player.bullet_fire_delay = 0
    objective.health = OBJECTIVE_HIT_POINTS
    
    ENEMY_SPEED = 10
    ENEMY_SPAWN_INTERVAL = 30
    ENEMY_SPAWN_DECREASE = 2
    
    BULLET_FIRE_DELAY_INCREASE = 2
    BULLET_FIRE_DELAY = 30
    
    BULLET_SPEED = 16 * 2
    BULLET_SPEED_INCREASE = 8
    
    ABLE_TO_ATTACK_DELAY = 10
    
    enemies.empty()
    bullets.empty()
    game_timer.reset()

# Create instances
player = Player()
objective = Objective()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
menu = Menu(player)
game_over_menu = GameOverMenu(player)

clock = pygame.time.Clock()
frame_count = 0
game_timer = Timer()
start_time = pygame.time.get_ticks()
is_attack = False
running = True
game_running = False
game_over = False

pygame_background_music.play(-1)

while cap.isOpened() and running:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    cv_x = 0
    cv_y = 0

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
            x_sum = sum(landmark.x for landmark in landmarks.landmark)
            y_sum = sum(landmark.y for landmark in landmarks.landmark)
            num_landmarks = len(landmarks.landmark)
            cv_x = x_sum / num_landmarks
            cv_y = y_sum / num_landmarks
            player.comvis(cv_x * screen_width, cv_y * screen_height)

    cv2.imshow("Camera Preview", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    if not game_over and not game_running:
        menu_choice = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                game_over = True
                pygame_background_music.stop()
                pygame_gameover_background_music.play(-1)
        
        menu_choice = menu.handle_events()
        
        player.update(cv_x, cv_y)
        menu.draw(screen)
        player.draw(screen)
        pygame.display.update()
        
        if menu_choice == "PLAY":
            game_running = True
            game_over = False
            is_attack = True
            game_timer.start()

    elif game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame_background_music.stop()
                pygame_gameover_background_music.play(-1)
                game_running = False
                game_over = True

        game_timer.update()
        player.update(cv_x, cv_y)
        
        if frame_count % ENEMY_SPAWN_INTERVAL == 0:
            enemies.add(Enemy())

        enemies.update(objective)
        bullets.update()
        player.auto_attack(enemies)

        if ABLE_TO_ATTACK_DELAY > 0:
            ABLE_TO_ATTACK_DELAY -= 1
        else:
            if pygame.mouse.get_pressed()[0] and player.bullet_count > 0 and player.bullet_fire_delay == 0:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y)
                bullets.add(bullet)
                player.bullet_fire_delay = BULLET_FIRE_DELAY
                player.bullet_count -= 1
                player_attack_sfx.play()

        if player.bullet_fire_delay > 0:
            player.bullet_fire_delay -= 1

        collisions = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for bullet, hit_enemies in collisions.items():
            for enemy in hit_enemies:
                player.score += 1
                player.bullet_count += BULLET_RELOAD_AMOUNT
                enemy_death_sfx.play()
                
        for enemy in enemies:
            if enemy.rect.colliderect(objective.rect):
                objective.health -= 10
                enemy.take_damage()
                enemy_death_sfx.play()
                enemy.kill()

        if player.bullet_count > MAX_BULLET_COUNT:
            player.bullet_count = MAX_BULLET_COUNT

        if player.score > 400:
            ENEMY_SPEED = 35
            BULLET_FIRE_DELAY = 3
            ENEMY_SPAWN_INTERVAL = 3
        elif player.score > 300:
            ENEMY_SPEED = 30
            BULLET_FIRE_DELAY = 5
            ENEMY_SPAWN_INTERVAL = 5
        elif player.score > 200:
            ENEMY_SPEED = 25
            BULLET_FIRE_DELAY = 10
            ENEMY_SPAWN_INTERVAL = 10
        elif player.score > 100:
            ENEMY_SPEED = 20
            BULLET_FIRE_DELAY = 15
            ENEMY_SPAWN_INTERVAL = 15
        elif player.score > 90:
            ENEMY_SPAWN_INTERVAL = 16
        elif player.score > 80:
            ENEMY_SPAWN_INTERVAL = 17
        elif player.score > 70:
            ENEMY_SPAWN_INTERVAL = 18
        elif player.score > 60:
            ENEMY_SPAWN_INTERVAL = 19
        elif player.score > 50:
            ENEMY_SPEED = 15
            BULLET_FIRE_DELAY = 20
            ENEMY_SPAWN_INTERVAL = 20
        elif player.score > 40:
            ENEMY_SPAWN_INTERVAL = 22
        elif player.score > 30:
            ENEMY_SPAWN_INTERVAL = 24
        elif player.score > 20:
            ENEMY_SPAWN_INTERVAL = 26
        elif player.score > 10:
            ENEMY_SPAWN_INTERVAL = 28
        else:
            ENEMY_SPEED = 10
            BULLET_FIRE_DELAY = 30
            ENEMY_SPAWN_INTERVAL = 30
        
        objective.update()
        if objective.health <= 0 or player.bullet_count == 0:
            game_running = False
            game_over = True
            pygame_background_music.stop()
            pygame_gameover_background_music.play(-1)
        
        pygame_background_image_scale = pygame.transform.scale(pygame_background_image, (screen_width, screen_height))
        screen.blit(pygame_background_image_scale, (0, 0))

        enemies.draw(screen)
        objective.draw(screen)
        player.draw(screen)
        game_timer.draw(screen)
        bullets.draw(screen)
            
        score_text = pixel_text_large.render(f"Score: {player.score}", True, (255, 255, 255))
        screen.blit(score_text, (screen_width // 2 - 100, screen_height - 100))
        frame_count += 1
        
    elif game_over:
        game_over_choice = None
        game_over_choice = game_over_menu.handle_events()
        
        player.update(cv_x, cv_y)
        game_over_menu.draw(screen)
        player.draw(screen)
        pygame.display.update()
            
        if game_over_choice == "REPLAY":
            reset_game()
            game_running = True
            game_over = False
            pygame_gameover_background_music.stop()
            pygame_background_music.play(-1)

    pygame.display.update()
    clock.tick(GAME_FPS)

pygame.quit()
sys.exit()