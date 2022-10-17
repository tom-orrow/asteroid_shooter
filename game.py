from cgitb import text
from dis import dis
import sys
from turtle import window_width
import pygame
from random import randint, uniform


def laser_update(laser_list, speed=300):
    for rect in laser_list:
        rect.bottom -= round(speed * dt)
        if rect.y < 0:
            laser_list.remove(rect)


def meteor_update(meteors_list, speed=300):
    for meteor in meteors_list:
        rect, direction = meteor
        rect.center += direction * round(speed * dt)
        if rect.top > WINDOW_HEIGHT:
            meteors_list.remove(meteor)


def display_score():
    score_text = f"Score: {pygame.time.get_ticks() // 1000}"
    text_surf = font.render(score_text, True, "White")
    text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(
        display_surface, "white", text_rect.inflate(30, 30), width=8, border_radius=5
    )


def laser_time(can_shoot, duration=500):
    if not can_shoot:
        current_time = pygame.time.get_ticks()
        if current_time - shoot_time > duration:
            can_shoot = True
    return can_shoot


# game init
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
VOLUME = 0.1
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Asteroid shooter")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

# import ship
ship_surf = pygame.image.load("graphics/ship.png").convert_alpha()
ship_rect = ship_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

# import bg
bg_surf = pygame.image.load("graphics/background.png").convert()

# import laser
laser_surf = pygame.image.load("graphics/laser.png").convert_alpha()
laser_list = []

# laser timer
can_shoot = True
shoot_time = None

# import text
font = pygame.font.Font("graphics/subatomic.ttf", 50)

# import meteor
meteor_surf = pygame.image.load("graphics/meteor.png").convert_alpha()
meteors_list = []

# meteor_time
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 500)


# import sound
laser_sound = pygame.mixer.Sound("sounds/laser.ogg")
laser_sound.set_volume(VOLUME)

explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
explosion_sound.set_volume(VOLUME)

background_music = pygame.mixer.Sound("sounds/music.wav")
background_music.set_volume(VOLUME)
background_music.play(loops=-1)

while True:
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and can_shoot:
            # laser
            laser_rect = laser_surf.get_rect(midbottom=ship_rect.midtop)
            laser_list.append(laser_rect)

            # timer
            can_shoot = False
            shoot_time = pygame.time.get_ticks()

            # play laser sound
            laser_sound.play()

        if event.type == meteor_timer:
            # random position
            x_pos = randint(-100, WINDOW_WIDTH + 100)
            y_pos = randint(-100, -50)

            # creating a rect
            meteor_rect = meteor_surf.get_rect(midbottom=(x_pos, y_pos))

            # create a random direction
            direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)

            meteors_list.append((meteor_rect, direction))

    # framerate limit
    dt = clock.tick(120) / 1000

    # mouse input
    ship_rect.center = pygame.mouse.get_pos()

    # update
    laser_update(laser_list)
    meteor_update(meteors_list)
    can_shoot = laser_time(can_shoot)

    # meteor collision
    for rect, _ in meteors_list:
        if ship_rect.colliderect(rect):
            pygame.quit()
            sys.exit()

    # laser meteor collisions
    for meteor in meteors_list:
        meteor_rect, _ = meteor
        for laser_rect in laser_list:
            if laser_rect.colliderect(meteor_rect):
                meteors_list.remove(meteor)
                laser_list.remove(laser_rect)
                explosion_sound.play()

    # drawing
    display_surface.fill("black")
    display_surface.blit(bg_surf, (0, 0))
    display_score()

    for rect in laser_list:
        display_surface.blit(laser_surf, rect)

    for rect, _ in meteors_list:
        display_surface.blit(meteor_surf, rect)

    display_surface.blit(ship_surf, ship_rect)

    # draw final frame
    pygame.display.update()
