import sys
import pygame
import random


class Ship(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # image
        self.image = pygame.image.load("graphics/ship.png").convert_alpha()
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.mask = pygame.mask.from_surface(self.image)

        # sound
        self.laser_sound = pygame.mixer.Sound("sounds/laser.ogg")
        self.laser_sound.set_volume(VOLUME)

        self.can_shoot = True
        self.shoot_time = None

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > 500:
                self.can_shoot = True

    def input_position(self):
        self.rect.center = pygame.mouse.get_pos()

    def laser_shoot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            Laser(self.rect.midtop, laser_group)
            self.laser_sound.play()

    def update(self):
        self.laser_timer()
        self.input_position()
        self.laser_shoot()
        self.meteor_collision()

    def meteor_collision(self):
        if pygame.sprite.spritecollide(
            self, meteor_group, True, pygame.sprite.collide_mask
        ):
            pygame.quit()
            sys.exit()


class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        # image
        self.image = pygame.image.load("graphics/laser.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)

        # sound
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
        self.explosion_sound.set_volume(VOLUME)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = 600

    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = round(self.pos.x), round(self.pos.y)
        self.meteor_collision()

        if self.rect.bottom < 0:
            self.kill()

    def meteor_collision(self):
        if pygame.sprite.spritecollide(
            self, meteor_group, True, pygame.sprite.collide_mask
        ):
            self.kill()
            self.explosion_sound.play()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        # scaling
        meteor_surface = pygame.image.load("graphics/meteor.png").convert_alpha()
        meteor_size = pygame.math.Vector2(meteor_surface.get_size()) * random.uniform(
            0.5, 1.5
        )
        self.scaled_surface = pygame.transform.scale(meteor_surface, meteor_size)
        self.image = self.scaled_surface
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(random.uniform(-0.5, 0.5), 1)
        self.speed = random.randint(400, 600)

        # rotation
        self.rotation = 0
        self.rotating_speed = random.randint(20, 50)

    def rotate(self):
        self.rotation += self.rotating_speed * dt
        self.image = pygame.transform.rotozoom(self.scaled_surface, self.rotation, 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = round(self.pos.x), round(self.pos.y)
        self.rotate()

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


class Score:
    def __init__(self):
        self.font = pygame.font.Font("graphics/subatomic.ttf", 50)

    def display(self):
        score_text = f"Score: {pygame.time.get_ticks() // 1000}"
        text_surf = self.font.render(score_text, True, "White")
        text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(
            display_surface,
            "white",
            text_rect.inflate(30, 30),
            width=8,
            border_radius=5,
        )


# basic setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
VOLUME = 0.1
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Asteroid shooter")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

# backgroud
bg_surf = pygame.image.load("graphics/background.png").convert()
background_music = pygame.mixer.Sound("sounds/music.wav")
background_music.set_volume(VOLUME)
background_music.play(loops=-1)

# sprite groups
spaceship_group = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

# sprite creation
ship = Ship(spaceship_group)

# meteor_timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 400)

# score
score = Score()

# game loop
while True:
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == meteor_timer:
            meteor_x_pos = random.randint(-100, WINDOW_WIDTH + 100)
            meteor_y_pos = random.randint(-150, -50)
            Meteor((meteor_x_pos, meteor_y_pos), groups=meteor_group)

    # framerate limit
    dt = clock.tick(120) / 1000

    # background
    display_surface.blit(bg_surf, (0, 0))

    # update
    spaceship_group.update()
    laser_group.update()
    meteor_group.update()

    # score
    score.display()

    # graphics
    spaceship_group.draw(display_surface)
    laser_group.draw(display_surface)
    meteor_group.draw(display_surface)

    # draw final frame
    pygame.display.update()
