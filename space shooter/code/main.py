import pygame
from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('images/player.png').convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = randint(150, 400)

        #cooldown
        self.can_fire = True
        self.fire_shoot_time = 0
        self.cooldown_duration = 2000

        #mask
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_fire:
            now = pygame.time.get_ticks()
            if now - self.fire_shoot_time >= self.cooldown_duration:
                self.can_fire = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction 
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_fire:
            # print('laser fired')
            Laser((all_sprites, laser_sprites), player_laser, self.rect.midtop,)
            self.can_fire = False
            self.fire_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center= (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

    def update(self, dt):
        self.rect.x -= 50 * dt
        if self.rect.right < 0:
            self.rect.x = WINDOW_WIDTH
            self.rect.y = randint(0, WINDOW_HEIGHT)

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        # self.mask = pygame.mask.from_surface(self.image)
        # self.speed = 500

    def update(self, dt):
        self.rect.centery -= 500 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time = pygame.time.get_ticks()
        self.life_time = 2500
        self.speed = 400
        self.direction = pygame.Vector2(uniform(-0.5,0.5), 1)
        self.rotation_speed = randint(20,50)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.life_time:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, pygame.time.get_ticks() / self.rotation_speed % 360, 1)
        self.rect = self.image.get_frect(center=self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        # self.sprites = [pygame.image.load(f'images/explosion{i}.png').convert_alpha() for i in range(9)]
        # self.rect = self.image.get_frect(center=pos)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        explosion_sound.play()

    def update(self, dt):
        self.frame_index += 30 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()
        # now = pygame.time.get_ticks()
        # if now - self.last_update >= self.frame_rate:
        #     self.frame += 1
        #     if self.frame == len(self.sprites):
        #         self.kill()
        #     else:
        #         self.image = self.sprites[self.frame]
        #         self.last_update = now

def collisions():
    global running

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False
    
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.center, all_sprites)

def display_score():
    current_time_score = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time_score), True, (255,255,255))
    text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (255,255,255), text_rect.inflate(20,10).move(0,-8), 5, 10)

#general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
title_img = pygame.image.load('images/title.jpg')
pygame.display.set_caption('Space Shooter')
pygame.display.set_icon(title_img)
running = True
clock =pygame.time.Clock()

#plain surface
surf= pygame.Surface((100,100))
surf.fill(('darkgray'))
x = 100

#imports
player_laser = pygame.image.load('images/laser.png').convert_alpha()
game_stars = pygame.image.load('images/star.png').convert_alpha()
game_meteor = pygame.image.load('images/meteor.png').convert_alpha()
font = pygame.font.Font('images/Oxanium-Bold.ttf', 32)
explosion_frames = [pygame.image.load(f'images/explosion/{i}.png').convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound('audio/laser.wav')
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
explosion_sound.set_volume(0.1)
# damage_sound = pygame.mixer.Sound('audio/damage.ogg')
# damage_sound.set_volume(0.1)
game_music = pygame.mixer.Sound('audio/game_music.wav')
game_music.set_volume(0.1)
game_music.play(loops=-1)

#load sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, game_stars)
player = Player(all_sprites)

#custom events -> meteor spawn event
meteor_event = pygame.event.custom_type()
[pygame.time.set_timer(meteor_event, 500)]

while running:
    dt = clock.tick() / 1000
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(game_meteor,(x,y), (all_sprites, meteor_sprites))

    all_sprites.update(dt)
    collisions()

    #draw the display
    display_surface.fill((0,20,100))
    all_sprites.draw(display_surface)
    display_score()

    pygame.display.update()

pygame.quit()