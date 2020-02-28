import pygame
import sys
import os

pygame.init()
size = width, height = 1200, 600
screen = pygame.display.set_mode(size)
running = True
FPS = 30
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

d = 'down'
not_have_blue = True
not_have_red = True
ver = False
hor = False
portal_b = False
portal_r = False
level = 1
f = pygame.Color("green")

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
coin_group = pygame.sprite.Group()

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
sound1 = pygame.mixer.Sound("data/shoot_1.wav")
sound2 = pygame.mixer.Sound("data/coin_1.wav")
coin_image = pygame.transform.scale(load_image('coin.png'), (20, 20))
places_tb = {}
places_fb = {}
places_tm = {}
coin_coords = []
coin_count = 0
al = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
cages = []
buttons = []
soundtrack = {1: 'data/m_2.mp3', 2: 'data/m_3.mp3', 3: 'data/m_4.mp3',
              4: 'data/m_5.mp3', 5: 'data/m_6.mp3', 6: 'data/m_7.mp3'}
no_music = True


def terminate():
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Portal228", "",
                  "",
                  "",
                  "Нажмите любую клавишу"]
    fon = load_image('logo.jpg')
    screen.blit(fon, (225, 100))
    font = pygame.font.Font(None, 70)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 450
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.mixer.music.load('data/m_1.mp3')
    pygame.mixer.music.play(-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(win):
    screen.fill(pygame.Color("black"))
    if win == 0:
        intro_text = ["GAME OVER", "",
                      "Разработчики:",
                      "Скранжевская Ксения",
                      "Евсеев Григорий"]
    else:
        intro_text = ["YOU WIN", "",
                      "Разработчики:",
                      "Скранжевская Ксения",
                      "Евсеев Григорий"]
    fon = load_image('logo.jpg')
    screen.blit(fon, (225, 100))
    font = pygame.font.Font(None, 70)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 450
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        pygame.mixer.music.load('data/m_8.mp3')
        pygame.mixer.music.play(-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
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


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(coin_group, all_sprites)
        self.image = coin_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 20, tile_height * pos_y + 20)


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
        if self.rect.x < 0 or self.rect.x + 30 > 1200 or self.rect.y < 0 or self.rect.y + 35 > 600:
            self.rect = self.rect.move(-x, -y)
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
        if self.rect.x < 0 or self.rect.x + 30 > 1200 or self.rect.y < 0 or self.rect.y + 35 > 600:
            self.rect = self.rect.move(-x, -y)
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
        if self.rect.x < 0 or self.rect.x > 1200 or self.rect.y < 0 or self.rect.y + 15 > 600:
            self.rect = self.rect.move(-self.vx, -self.vy)
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
        if self.rect.x < 0 or self.rect.x > 1200 or self.rect.y < 0 or self.rect.y + 15 > 600:
            self.rect = self.rect.move(-self.vx, -self.vy)
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
            elif lvl[y][x] == '/':
                Empty(x, y)
                Coin(x, y)
                coin_coords.append([x, y, False])
            elif lvl[y][x].isdigit():
                Empty(x, y)
                cage = Obstacles(x, y, 'c')
                cages.append(cage)
                places_tb[int(lvl[y][x])] = [x, y]
                filename = "data/lvl_" + str(level) + ".txt"
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


def music(l):
    pygame.mixer.music.set_volume(0.75)
    pygame.mixer.music.load(soundtrack[l])
    pygame.mixer.music.play(-1)

start_screen()
player, door, level_x, level_y = generate_level(load_level('map.txt'))
while running:
    if no_music:
        music(level)
        no_music = False
    screen.fill(pygame.Color("white"))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end_screen(0)
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
            if event.key == pygame.K_e:
                for i in coin_coords:
                    if i[2]:
                        coin_count += 1
                        sound2.play()
                        del coin_coords[coin_coords.index(i)]
                        coin_group = pygame.sprite.Group()
                        for j in coin_coords:
                            Coin(j[0], j[1])
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
            sound1.play()
            if not_have_blue:
                b_portal_group = pygame.sprite.Group()
                portal_b = PortalBlue(player.rect.x, player.rect.y, d)
                not_have_blue = False
                not_have_red = True
            else:
                if not_have_red:
                    r_portal_group = pygame.sprite.Group()
                    portal_r = PortalRed(player.rect.x, player.rect.y, d)
                    not_have_red = False
                    not_have_blue = True
    if ver:
        player.move_ver(0, directions[d][1])
        player.moving(d)
    if hor:
        player.move_hor(directions[d][0], 0)
        player.moving(d)
        if player.rect.x // 60 == door.rect.x // 60 and player.rect.y // 60 == door.rect.y // 60:
            if coin_count == level:
                level += 1
                if level == 7:
                    end_screen(1)
                    break
                no_music = True
                all_sprites = pygame.sprite.Group()
                walls_group = pygame.sprite.Group()
                empty_group = pygame.sprite.Group()
                player_group = pygame.sprite.Group()
                b_portal_group = pygame.sprite.Group()
                r_portal_group = pygame.sprite.Group()
                doors_group = pygame.sprite.Group()
                obstacles_group = pygame.sprite.Group()
                button_group = pygame.sprite.Group()
                coin_group = pygame.sprite.Group()
                portal_r = None
                portal_b = None
                button_coords = []
                coords = {}
                places_fb = {}
                places_tb = {}
                coin_coords = []
                coin_count = 0
                wall_image = pygame.transform.scale(load_image(levels[level][1]), (tile_width, tile_height))
                empty_image = pygame.transform.scale(load_image(levels[level][2]), (tile_width, tile_height))
                player, door, level_x, level_y = generate_level(load_level(levels[level][0]))
    if portal_b:
        portal_b.update()
    if portal_r:
        portal_r.update()
    if level == 1 or level == 3 or level == 6:
        f = pygame.Color("green")
    elif level == 2 or level == 4 or level == 5:
        f = pygame.Color("red")
    clock.tick(15)
    walls_group.draw(screen)
    empty_group.draw(screen)
    doors_group.draw(screen)
    coin_group.draw(screen)
    obstacles_group.draw(screen)
    button_group.draw(screen)
    b_portal_group.draw(screen)
    r_portal_group.draw(screen)
    player_group.draw(screen)
    can_push_button = False
    for i in coin_coords:
        if player.rect.x // 60 == i[0] and player.rect.y // 60 == i[1]:
            i[2] = True
            font = pygame.font.Font(None, 50)
            num = 'Press E to collect the coin'
            text = font.render(num, 1, f)
            screen.blit(text, (390, 30))
    for i in places_fb:
        if places_fb[i][0] == player.rect.x // 60 and places_fb[i][1] == player.rect.y // 60:
            places_fb[i][2] = True
            font = pygame.font.Font(None, 50)
            num = 'Press F to use the button'
            text = font.render(num, 1, f)
            screen.blit(text, (390, 30))
        else:
            places_fb[i][2] = False
    pygame.display.flip()
terminate()
