import random
import pygame
from settings import *

# Initialize Pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


def draw_text(surf, text, desired_font, size, x, y):
    font = pygame.font.Font(desired_font, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def spawn_mob(quantity):
    while quantity > 0:
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)
        quantity += -1


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    fill = (pct/100) * SHIELD_BAR_LENGTH
    outline_rect = pygame.Rect(x, y, SHIELD_BAR_LENGTH, SHIELD_BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, SHIELD_BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


class Player(pygame.sprite.Sprite):
    # Sprite for the Player
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 28))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        # Timeout for powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > GUN_POWERUP_TIME:
            self.power -= 1
            gun_powerdown_sound.play()
            self.power_time = pygame.time.get_ticks()

        # Unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = 5
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            if self.power == 1:
                self.last_shot = now
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power >= 2:
                self.last_shot = now
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        # Hide player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_og = random.choice(meteor_img)
        self.image_og.set_colorkey(BLACK)
        self.image = self.image_og.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = self.rot + self.rot_speed % 360
            new_image = pygame.transform.rotate(self.image_og, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)
        if self.rect.right > WIDTH:
            self.speedx = random.randrange(-3, 0)
        if self.rect.left < 0:
            self.speedx = random.randrange(0, 3)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun"])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the bottom of the screen
        if self.rect.top > HEIGHT:
            self.kill()


def show_go_screen():
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    draw_text(screen, TITLE, title_font, 36, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Left and right arrow keys to move,", normal_font, 18, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "space to shoot", normal_font, 18, WIDTH / 2, HEIGHT / 2 + 30)
    draw_text(screen, "Press any key to start", normal_font, 14, WIDTH / 2, HEIGHT * 3 / 4 + 5)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
            elif e.type == pygame.KEYUP:
                waiting = False


# class PlayerDamage(pygame.sprite.Sprite):
    # def __init__(self, center):
        # pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.transform.scale(player_damage_anim[0], (50, 28))
        # self.rect = self.image.get_rect()
        # self.rect.center = center
        # self.frame = 0
        # self.last_update = pygame.time.get_ticks()
        # self.frame_rate = 50

    # def update(self):
        # now = pygame.time.get_ticks()
        # if now - self.last_update > self.frame_rate:
            # self.frame += 1
            # if self.frame == len(player_damage_anim):
                # self.kill()
            # else:
                # center = self.rect.center
                # self.image = player_damage_anim[self.frame]
                # self.rect = self.image.get_rect()
                # self.rect.center = center


# Load all game graphics
background = pygame.transform.scale(pygame.image.load(path.join(Backgrounds_dir, "darkPurple[expanded].png")).convert(),
                                    (WIDTH, HEIGHT))
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(PNG_dir, "playerShip1_orange.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(Lasers_dir, "laserGreen12.png")).convert()
meteor_img = []
meteor_img_list = ["meteorBrown_big1.png", "meteorBrown_big2.png", "meteorBrown_med1.png", "meteorBrown_med3.png",
                   "meteorBrown_small1.png", "meteorBrown_small2.png", "meteorBrown_tiny1.png"]
for img in meteor_img_list:
    meteor_img.append(pygame.image.load(path.join(Meteors_dir, img)).convert())
explosion_anim = {"large": [], "small": [], "player": []}
for i in range(9):
    filename = "regularExplosion0{}.png".format(i)
    img = pygame.image.load(path.join(Explosions_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_large = pygame.transform.scale(img, (100, 100))
    explosion_anim["large"].append(img_large)
    img_small = pygame.transform.scale(img, (32, 32))
    explosion_anim["small"].append(img_small)
    filename = "sonicExplosion0{}.png".format(i)
    explosion_anim["player"].append(img)
powerup_images = {"shield": pygame.image.load(path.join(Powerups_dir, "shield_gold.png")).convert(),
                  "gun": pygame.image.load(path.join(Powerups_dir, "bolt_gold.png")).convert()}
# player_damage_anim = []
# for i in range(1, 4):
#    filename = "playerShip1_damage{}.png".format(i)
#    img = pygame.image.load(path.join(Player_damage_dir, filename)).convert()
#    img.set_colorkey(BLACK)
#    player_damage_anim.append(pygame.transform.scale(img, (50, 50)))

# Load all game sounds
pygame.mixer.music.load(path.join(Bonus_dir, "space walk.ogg"))
explosion_sounds = []
for explosion_sound in ["Explosion1.wav", "Explosion2.wav", "Explosion3.wav", "Explosion4.wav"]:
    explosion_sounds.append(pygame.mixer.Sound(path.join(Bonus_dir, explosion_sound)))
    for sound in explosion_sounds:
        sound.set_volume(0.3)
shoot_sound = pygame.mixer.Sound(path.join(Bonus_dir, "sfx_laser2.ogg"))
shoot_sound.set_volume(0.7)
player_death_sound = pygame.mixer.Sound(path.join(Bonus_dir, "rumble1.ogg"))
shield_powerup_sound = pygame.mixer.Sound(path.join(Bonus_dir, "sfx_shieldUp.ogg"))
gun_powerup_sound = pygame.mixer.Sound(path.join(Bonus_dir, "sfx_zap.ogg"))
gun_powerdown_sound = pygame.mixer.Sound(path.join(Bonus_dir, "sfx_twoTone.ogg"))

# Define all game fonts
normal_font = path.join(Bonus_dir, "kenvector_future_thin.ttf")
title_font = path.join(Bonus_dir, "kenvector_future.ttf")

pygame.mixer.music.play(loops=-1)

# Game loop
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        # Create sprite groups
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            spawn_mob(1)

        score = 0
    # Keep loop running at the right speed
    clock.tick(FPS)

    # Process input (events)
    for event in pygame.event.get():
        # Check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()

    # Check if bullet hits mob
    bullet_hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for bullet_hit in bullet_hits:
        score += 60 - bullet_hit.radius
        random.choice(explosion_sounds).play()
        expl = Explosion(bullet_hit.rect.center, "large")
        all_sprites.add(expl)
        if random.random() > 0.97:
            pow_up = Pow(bullet_hit.rect.center)
            all_sprites.add(pow_up)
            powerups.add(pow_up)
        spawn_mob(1)
    # Check if player hits powerup
    gained_power_ups = pygame.sprite.spritecollide(player, powerups, True)
    for gained_power_up in gained_power_ups:
        if gained_power_up.type == "shield":
            shield_powerup_sound.play()
            player.shield = 100
        if gained_power_up.type == "gun":
            gun_powerup_sound.play()
            player.power += 2

    # check if mob hits player
    player_hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for player_hit in player_hits:
        player.shield -= player_hit.radius * 2
        expl = Explosion(player_hit.rect.center, "small")
        all_sprites.add(expl)
        # pldam = PlayerDamage(player.rect.center)
        # all_sprites.add(pldam)
        spawn_mob(1)
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, "player")
            all_sprites.add(death_explosion)
            player_death_sound.play()
            player.hide()
            player.lives -= 1
            player.shield = 100

    # If player died and the explosion has finished playing
    if player.lives == 0 and not death_explosion.alive() and not player_death_sound.play():
        game_over = True

    # Draw/render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), normal_font, 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    pygame.display.flip()

pygame.quit()
