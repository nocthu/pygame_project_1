import pygame
import sys
import os

pygame.init()
size = width, height = 750, 500
screen = pygame.display.set_mode(size)
running = True
FPS = 30
clock = pygame.time.Clock()
# have_red = False
# have_blue = False
# portals = {'blue': False, 'red': False}
# portal_blue = None
# portal_red = None
player = None
all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
empty_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
# player = AnimatedSprite(load_image("dino.png"), 8, 2, 50, 50)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_width = tile_height = 50
wall_image = pygame.transform.scale(load_image('wall_1.png'), (tile_width, tile_height))
empty_image = pygame.transform.scale(load_image('wall_2.png'), (tile_width, tile_height))
player_image = load_image('mario.png', -1)
portal_blue_image = pygame.transform.scale(load_image('portal_blue.png', -1), (tile_width, tile_height))
portal_red_image = pygame.transform.scale(load_image('portal_red.png', -1), (tile_width, tile_height))
directions = {0: 0, 'right': (10, 0), 'left': (-10, 0), 'up': (0, -10), 'down': (0, 10)}


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["PORTAL", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

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
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)

    def get_cell(self, mouse_pos):
        self.p1 = (mouse_pos[0] - self.left) // self.cell_size
        self.p2 = (mouse_pos[1] - self.top) // self.cell_size
        if self.p1 < 0 or self.p1 >= self.width or self.p2 < 0 or self.p2 >= self.height:
            return None
        return self.p1, self.p2

    def on_click(self, cell_coords):
        pass

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color("white"),
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top,
                                  self.cell_size, self.cell_size), 1)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        self.add(walls_group)
        self.image = wall_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Empty(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(empty_group, all_sprites)
        self.image = empty_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)

    def update(self, x, y):
        self.rect = self.rect.move(x, y)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-x, -y)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class PortalBlue(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        # self.image = portal_blue_image
        # self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.radius = 5
        self.image = pygame.Surface((2 * 5, 2 * 5), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("red"), (5, 5), 5)
        self.rect = pygame.Rect(pos_x, pos_y, 2 * 5, 2 * 5)

    def update(self, d):
        vx = directions[d][0]
        vy = directions[d][1]
        if not pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(vx, vy)


class PortalRed(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = portal_red_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self, d):
        vx = directions[d][0]
        vy = directions[d][1]
        if not pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(vx, vy)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Empty('empty', x, y)
            elif level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '@':
                Empty('empty', x, y)
                new_player = Player(x, y)
                # new_player = AnimatedSprite(load_image("dino.png"), 8, 2, x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


start_screen()
camera = Camera()
player, level_x, level_y = generate_level(load_level('map.txt'))
# board = Board(10, 10, 10)
while running:
    screen.fill(pygame.Color("white"))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.update(0, -10)
            if event.key == pygame.K_DOWN:
                player.update(0, 10)
            if event.key == pygame.K_LEFT:
                player.update(-10, 0)
            if event.key == pygame.K_RIGHT:
                player.update(10, 0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            PortalBlue(event.pos[0], event.pos[1])
    #         if portals['blue']:
    #             portals['red'] = True
    #             color = 'red'
    #             x, y = event.pos[0], event.pos[1]
    #             # drawing('red', event.pos[0], event.pos[1])
    #         else:
    #             portals['blue'] = True
    #             color = 'blue'
    #             x, y = event.pos[0], event.pos[1]
    #             # drawing('blue', event.pos[0], event.pos[1])
    # if portals['blue']:
    #     pygame.draw.circle(screen, pygame.Color('blue'), (x, y), 5)
    #     x += 10 * clock.tick() // 1000
    #     y += 0 * clock.tick() // 1000
    # elif portals['red']:
    #     pygame.draw.circle(screen, pygame.Color('red'), (x, y), 5)
    #     x += 10 * clock.tick() // 1000
    #     y += 0 * clock.tick() // 1000
    #     portals['blue'] = False
    #     portals['red'] = False

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    walls_group.draw(screen)
    empty_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
terminate()
