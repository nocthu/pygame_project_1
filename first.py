import pygame
import sys
import os

# pygame.mixer.pre_init()
pygame.init()

pygame.init()

# pygame.mixer.music.load('data/song_1.mp3')
# pygame.mixer.music.play(-1)

size = width, height = 900, 600
screen = pygame.display.set_mode(size)
running = True
FPS = 30
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

d = 'down'
p_b = False
p_r = False
not_have_blue = True
not_have_red = True
ver = False
hor = False
portal_b = False
portal_r = False
level = 1
global a, n_button, n_cage
a = 'right'
n_button = 0
n_cage = 0
can_push_button = False

levels = {2: ['map2.txt', 'wall_5.png', 'wall_7.png'], 3: ['map3.txt', 'wall_6.png', 'wall_10.png'],
          4: ['map4.txt', 'wall_14.png', 'wall_15.png'], 5: ['map5.txt', 'wall_9.png', 'wall_16.png'],
          6: ['map6.txt', 'wall_11.png', 'wall_8.png']}

player = None
all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
empty_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
b_portal_group = pygame.sprite.Group()
r_portal_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
obstacles_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()

# pygame.mixer.init()
# pygame.mixer.music.load("/Users/grigorijevseev/Desktop/Super Mario Bros. medley.wav")
# pygame.mixer.music.play()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    image = image.convert_alpha()
    return image


tile_width = tile_height = 60
wall_image = pygame.transform.scale(load_image('wall_3.png'), (tile_width, tile_height))
empty_image = pygame.transform.scale(load_image('wall_2.png'), (tile_width, tile_height))
player_image = pygame.transform.scale(load_image("pl.bmp", -1), (150, 150))
portal_blue_image = {'right': pygame.transform.scale(load_image('portal_blue.png', -1), (15, 25)),
                     'left':  pygame.transform.scale(load_image('portal_blue_left.png', -1), (15, 25)),
                     'up':  pygame.transform.scale(load_image('portal_blue_up.png', -1), (25, 15)),
                     'down':  pygame.transform.scale(load_image('portal_blue_down.png', -1), (25, 15))}
portal_red_image = {'right': pygame.transform.scale(load_image('portal_red.png', -1), (15, 25)),
                    'left':  pygame.transform.scale(load_image('portal_red_left.png', -1), (15, 25)),
                    'up':  pygame.transform.scale(load_image('portal_red_up.png', -1), (25, 15)),
                    'down':  pygame.transform.scale(load_image('portal_red_down.png', -1), (25, 15))}
directions = {'right': (5, 0), 'left': (-5, 0), 'up': (0, -5), 'down': (0, 5)}
door_image = pygame.transform.scale(load_image('door.png'), (tile_width, tile_height))
obstacles = {'c': pygame.transform.scale(load_image('cage.png'), (tile_width, tile_height))}
button_image = {0: pygame.transform.scale(load_image('button_red.png', -1), (tile_width, tile_height // 2)),
                1: pygame.transform.scale(load_image('button_green.png', -1), (tile_width, tile_height // 2))}

places_tb = {}
places_fb = {}
places_tm = {}
al = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
cages = []
buttons = []


def terminate():
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Portal228", "",
                  "Проект pygame",
                  "",
                  "Нажмите любую клавишу"]

    # fon = pygame.transform.scale(load_image('logo.jpg'), (width, height))
    fon = load_image('logo.jpg')
    screen.blit(fon, (0, 100))
    font = pygame.font.Font(None, 30)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    pygame.mixer.music.load('data/fon.mp3')
    pygame.mixer.music.play(-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def end_screen():
    screen.fill(pygame.Color("black"))
    intro_text = ["GAME OVER", "",
                  "Разработчики:",
                  "Скранжевская Ксения",
                  "Евсеев Григорий"]

    fon = load_image('logo.jpg')
    screen.blit(fon, (0, 100))
    font = pygame.font.Font(None, 30)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '#'), level_map))


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.add(walls_group)
        self.image = wall_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Empty(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(empty_group, all_sprites)
        self.image = empty_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(doors_group, all_sprites)
        self.image = door_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Obstacles(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type):
        super().__init__(obstacles_group, all_sprites)
        self.image = obstacles[type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, c):
        super().__init__(button_group, all_sprites)
        self.image = button_image[c]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.n = 'right'
        self.frames = []
        self.cut_sheet(player_image, 4, 4)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)
        self.down = self.frames[:4]
        self.up = self.frames[4:8]
        self.left = self.frames[8:12]
        self.right = self.frames[12:]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def moving(self, d):
        move = 'right'
        if d == 'left':
            move = self.left
        elif d == 'right':
            move = self.right
        elif d == 'up':
            move = self.up
        elif d == 'down':
            move = self.down
        self.cur_frame = (self.cur_frame + 1) % len(move)
        self.image = move[self.cur_frame]

    def move_ver(self, x, y):
        self.rect = self.rect.move(x, y)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-x, -y)
        if pygame.sprite.spritecollideany(self, obstacles_group):
            self.rect = self.rect.move(-x, -y)
        if pygame.sprite.spritecollideany(self, button_group):
            font = pygame.font.Font(None, 50)
            num = 'Press F to use the button'
            text = font.render(num, 1, pygame.Color("red"))
            screen.blit(text, (120, 70))
        if pygame.sprite.spritecollideany(self, b_portal_group):
            mine = portal_b
            new = portal_r
            if new:
                nuy = (new.rect.y - new.rect.y % 60) - self.rect.y
                if new.direction() == 'up':
                    nuy += 20
                if new.rect.y == mine.rect.y:
                    nuy = 0
                if new.direction() == 'left' or new.direction() == 'right':
                    nuy = new.rect.y - self.rect.y

                nux = (new.rect.x - new.rect.x % 60) - self.rect.x
                if new.direction() == 'left':
                    nux += 20
                if new.rect.x == mine.rect.x:
                    nux = 0
                if new.direction() == 'up' or new.direction() == 'down':
                    nux = new.rect.x - self.rect.x
                self.rect = self.rect.move(nux, nuy)

        if pygame.sprite.spritecollideany(self, r_portal_group):
            mine = portal_r
            new = portal_b
            if new:
                nuy = (new.rect.y - new.rect.y % 60) - self.rect.y
                if new.direction() == 'up':
                    nuy += 20
                if new.rect.y == mine.rect.y:
                    nuy = 0
                if new.direction() == 'left' or new.direction() == 'right':
                    nuy = new.rect.y - self.rect.y

                nux = (new.rect.x - new.rect.x % 60) - self.rect.x
                if new.direction() == 'left':
                    nux += 20
                if new.rect.x == mine.rect.x:
                    nux = 0
                if new.direction() == 'up' or new.direction() == 'down':
                    nux = new.rect.x - self.rect.x
                self.rect = self.rect.move(nux, nuy)

    def move_hor(self, x, y):
        self.rect = self.rect.move(x, y)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-x, -y)
        if pygame.sprite.spritecollideany(self, obstacles_group):
            self.rect = self.rect.move(-x, -y)
        if pygame.sprite.spritecollideany(self, b_portal_group):
            mine = portal_b
            new = portal_r
            if new:
                nuy = (new.rect.y - new.rect.y % 60) - self.rect.y
                if new.direction() == 'up':
                    nuy += 20
                if new.rect.y == mine.rect.y:
                    nuy = 0
                if new.direction() == 'left' or new.direction() == 'right':
                    nuy = new.rect.y - self.rect.y

                nux = (new.rect.x - new.rect.x % 60) - self.rect.x
                if new.direction() == 'left':
                    nux += 20
                if new.rect.x == mine.rect.x:
                    nux = 0
                if new.direction() == 'up' or new.direction() == 'down':
                    nux = new.rect.x - self.rect.x
                self.rect = self.rect.move(nux, nuy)

        if pygame.sprite.spritecollideany(self, r_portal_group):
            mine = portal_r
            new = portal_b
            if new:
                nuy = (new.rect.y - new.rect.y % 60) - self.rect.y
                if new.direction() == 'up':
                    nuy += 20
                if new.rect.y == mine.rect.y:
                    nuy = 0
                if new.direction() == 'left' or new.direction() == 'right':
                    nuy = new.rect.y - self.rect.y

                nux = (new.rect.x - new.rect.x % 60) - self.rect.x
                if new.direction() == 'left':
                    nux += 20
                if new.rect.x == mine.rect.x:
                    nux = 0
                if new.direction() == 'up' or new.direction() == 'down':
                    nux = new.rect.x - self.rect.x
                self.rect = self.rect.move(nux, nuy)


class PortalBlue(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, d):
        super().__init__(b_portal_group)
        self.d = d
        self.image = portal_blue_image[self.d]
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.vx = directions[d][0] * 2
        self.vy = directions[d][1] * 2

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-self.vx, -self.vy)
        if pygame.sprite.spritecollideany(self, obstacles_group):
            self.rect = self.rect.move(-self.vx, -self.vy)

    def direction(self):
        return self.d

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()


class PortalRed(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, d):
        super().__init__(r_portal_group)
        self.d = d
        self.image = portal_red_image[self.d]
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.vx = directions[d][0] * 2
        self.vy = directions[d][1] * 2

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-self.vx, -self.vy)
        if pygame.sprite.spritecollideany(self, obstacles_group):
            self.rect = self.rect.move(-self.vx, -self.vy)

    def direction(self):
        return self.d

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()


def generate_level(lvl):
    new_player, new_door, x, y = None, None, None, None
    for y in range(len(lvl)):
        for x in range(len(lvl[y])):
            if lvl[y][x] == '.':
                Empty(x, y)
            elif lvl[y][x] == '#':
                Wall(x, y)
            elif lvl[y][x] == '@':
                Empty(x, y)
                new_player = Player(x, y)
            elif lvl[y][x] == '!':
                new_door = Door(x, y)
            elif lvl[y][x].isdigit():
                Empty(x, y)
                cage = Obstacles(x, y, 'c')
                cages.append(cage)
                places_tb[int(lvl[y][x])] = [x, y]

                filename = "data/lvl_'
                with open(filename, 'r') as mapFile:
                    level_map = [line.strip() for line in mapFile]
                x1, y1 = int(level_map[int(lvl[y][x])].split()[0]), int(level_map[int(lvl[y][x])].split()[1])
                places_tm[int(lvl[y][x])] = [x + x1, y + y1]
            elif lvl[y][x].isalpha():
                Empty(x, y)
                button = Button(x, y, 0)
                buttons.append(button)
                places_fb[al.index(lvl[y][x])] = [x, y, False, 0]
    return new_player, new_door, x, y


start_screen()
pygame.mixer.music.load('data/song_1.mp3')
pygame.mixer.music.play(-1)
player, door, level_x, level_y = generate_level(load_level('map.txt'))
while running:
    screen.fill(pygame.Color("white"))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ver = True
                d = 'up'
            if event.key == pygame.K_DOWN:
                ver = True
                d = 'down'
            if event.key == pygame.K_LEFT:
                hor = True
                d = 'left'
            if event.key == pygame.K_RIGHT:
                hor = True
                d = 'right'
            if event.key == pygame.K_f:
                for i in places_fb:
                    if places_fb[i][2]:
                        places_fb[i][3] = (places_fb[i][3] + 1) % 2
                        Button(places_fb[i][0], places_fb[i][1], places_fb[i][3])
                        obstacles_group = pygame.sprite.Group()
                        for j in places_tb:
                            if j != i:
                                Obstacles(places_tb[j][0], places_tb[j][1], 'c')
                        if places_fb[i][3] == 1:
                            places_tb[i], places_tm[i] = places_tm[i], places_tb[i]
                            Obstacles(places_tb[i][0], places_tb[i][1], 'c')
                        else:
                            places_tb[i], places_tm[i] = places_tm[i], places_tb[i]
                            Obstacles(places_tb[i][0], places_tb[i][1], 'c')

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                ver = False
            if event.key == pygame.K_DOWN:
                ver = False
            if event.key == pygame.K_LEFT:
                hor = False
            if event.key == pygame.K_RIGHT:
                hor = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not_have_blue:
                b_portal_group = pygame.sprite.Group()
                portal_b = PortalBlue(player.rect.x, player.rect.y, d)
                not_have_blue = False
                not_have_red = True
                p_b = True
            else:
                if not_have_red:
                    r_portal_group = pygame.sprite.Group()
                    portal_r = PortalRed(player.rect.x, player.rect.y, d)
                    not_have_red = False
                    p_r = True
                    not_have_blue = True
    if ver:
        player.move_ver(0, directions[d][1])
        player.moving(d)
    if hor:
        player.move_hor(directions[d][0], 0)
        player.moving(d)
        if player.rect.x == door.rect.x:
            level += 1
            if level == 7:
                break
            all_sprites = pygame.sprite.Group()
            walls_group = pygame.sprite.Group()
            empty_group = pygame.sprite.Group()
            player_group = pygame.sprite.Group()
            b_portal_group = pygame.sprite.Group()
            r_portal_group = pygame.sprite.Group()
            doors_group = pygame.sprite.Group()
            obstacles_group = pygame.sprite.Group()
            button_group = pygame.sprite.Group()
            button_coords = []
            coords = {}
            places_fb = {}
            places_tb = {}
            wall_image = pygame.transform.scale(load_image(levels[level][1]), (tile_width, tile_height))
            empty_image = pygame.transform.scale(load_image(levels[level][2]), (tile_width, tile_height))
            player, door, level_x, level_y = generate_level(load_level(levels[level][0]))
    if p_b:
        portal_b.update()
    if p_r:
        portal_r.update()
    clock.tick(15)
    walls_group.draw(screen)
    empty_group.draw(screen)
    doors_group.draw(screen)
    obstacles_group.draw(screen)
    button_group.draw(screen)
    b_portal_group.draw(screen)
    r_portal_group.draw(screen)
    player_group.draw(screen)
    can_push_button = False
    for i in places_fb:
        if places_fb[i][0] == player.rect.x // 60 and places_fb[i][1] == player.rect.y // 60:
            places_fb[i][2] = True
            font = pygame.font.Font(None, 50)
            num = 'Press F to use the button'
            text = font.render(num, 1, pygame.Color("green"))
            screen.blit(text, (250, 35))
        else:
            places_fb[i][2] = False
    pygame.display.flip()
end_screen()
terminate()