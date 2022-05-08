import sys
import pygame


# from pygame.locals import *

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class World:
    def __init__(self, data):
        self.tile_list = []

        # load images
        grass_img = pygame.image.load('Graphics/Base pack/Tiles/grassMid.png').convert_alpha()
        grass_center_img = pygame.image.load('Graphics/Base pack/Tiles/grassCenter.png').convert_alpha()

        # draw map
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = grass_img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = grass_center_img = pygame.transform.scale(grass_center_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    spider = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    spider_group.add(spider)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 11):
            img_right = pygame.image.load(
                f'Graphics/Base pack/Player/p3_walk/PNG_RIGHT/p3_walk{num}.png').convert_alpha()
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('Graphics/Base pack/Player/ghost_dead.png').convert_alpha()
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 1

    def update(self, game_over):

        dx = 0
        dy = 0
        walk_cooldown = 2

        if game_over == 0:

            # key listening
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped:
                self.vel_y = -17
                self.jumped = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 2
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 2
                self.counter += 1
                self.direction = 1
            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index]
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # add gravity
            self.vel_y += 1
            if self.vel_y > 17:
                self.vel_y = 17
            dy += self.vel_y

            # check collision
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
            if self.vel_y != 0 and self.direction == 1:
                self.image = pygame.image.load('Graphics/Base pack/Player/p3_jump.png').convert_alpha()
            if self.vel_y != 0 and self.direction == -1:
                self.image = pygame.image.load('Graphics/Base pack/Player/p3_jump.png')
                self.image = pygame.transform.flip(self.image, True, False)

            if pygame.sprite.spritecollide(self, spider_group, False):
                game_over = -1
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            if key[pygame.K_DOWN] and self.direction == 1:
                self.image = pygame.image.load('Graphics/Base pack/Player/p3_duck.png')
                dy = dy + 12
            if key[pygame.K_DOWN] and self.direction == -1:
                self.image = pygame.image.load('Graphics/Base pack/Player/p3_duck.png')
                self.image = pygame.transform.flip(self.image, True, False)
                dy = dy + 12
            if key[pygame.K_DOWN] and key[pygame.K_SPACE]:
                dy = dy - 12

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
            if self.rect.right > screen_width:
                self.rect.right = screen_width
            if self.rect.left < 0:
                self.rect.left = 0
        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > -60:
                self.rect.y -= 5
        screen.blit(self.image, self.rect)
        return game_over


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images_left = []
        self.images_right = []
        self.index = 0
        self.counter = 1
        for num in range(1, 10):
            img_left = pygame.image.load(
                f'Graphics/Extra animations and enemies/Enemy sprites/spider_walk{num}.png').convert_alpha()
            img_right = pygame.transform.flip(img_left, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.direction = 0

    def update(self):
        walk_cooldown = 5

        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

        if self.move_direction == 1:
            self.counter += 1
            self.direction = 1
        if self.move_direction == -1:
            self.counter += 1
            self.direction = -1

        if self.counter > walk_cooldown:
            self.counter = 1
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            if self.move_direction == 1:
                self.image = self.images_right[self.index]
            if self.move_direction == -1:
                self.image = self.images_left[self.index]
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Graphics/Base pack/Tiles/liquidLavaTop_mid.png').convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# def draw_grid():
#   for line in range(0, 20):
#      pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
#     pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))


pygame.init()
screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_width))
pygame.display.set_caption('Jumper')

# clock element
clock = pygame.time.Clock()

# game variables
tile_size = 40

# Sun Image
sun_img = pygame.image.load('Graphics/Request pack/Tiles/laserYellowBurst.png').convert_alpha()
sun_img = pygame.transform.scale(sun_img, (100, 100))

# Background Image
bg_img = pygame.image.load('Graphics/Base pack/bg1.png').convert_alpha()
bg_img = pygame.transform.scale(bg_img, (800, 800))

# level
world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 6, 6, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
]

player = Player(40, screen_height - 96)

spider_group = pygame.sprite.Group()

lava_group = pygame.sprite.Group()

world = World(world_data)

game_o = 0

run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (75, 75))

    world.draw()

    if game_o == 0:
        spider_group.update()
    spider_group.draw(screen)
    lava_group.draw(screen)

    game_o = player.update(game_o)

    # draw_grid()

    pygame.display.update()
    clock.tick(60)
