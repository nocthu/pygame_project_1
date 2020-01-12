import pygame
import sys
import os

pygame.init()
size = width, height = 750, 500
screen = pygame.display.set_mode(size)
running = True
FPS = 30
pygame.mouse.set_visible(False)
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
portals_group = pygame.sprite.Group()
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
portal_blue_image = pygame.transform.scale(load_image('portal_blue.png', -1), (tile_width // 2, tile_height // 2))
portal_red_image = pygame.transform.scale(load_image('portal_red.png', -1), (tile_width // 2, tile_height // 2))
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
    return list(map(lambda x: x.ljust(max_width, '#'), level_map))


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
    def __init__(self, pos_x, pos_y, d):
        super().__init__(portals_group)
        self.image = portal_blue_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.vx = directions[d][0]
        self.vy = directions[d][1]

    def update(self):
        if not pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(self.vx, self.vy)


class PortalRed(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, d):
        super().__init__(portals_group)
        self.image = portal_red_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.vx = directions[d][0]
        self.vy = directions[d][1]

    def update(self):
        if not pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(self.vx, self.vy)


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
portal = None
# board = Board(10, 10, 10)
d = 'right'
p_b = False
p_r = False
not_have_blue = True
not_have_red = True
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
                d = 'left'
            if event.key == pygame.K_RIGHT:
                player.update(10, 0)
                d = 'right'
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not_have_blue:
                portal_b = PortalBlue(player.rect.x, player.rect.y, d)
                not_have_blue = False
                p_b = True
            else:
                if not_have_red:
                    portal_r = PortalRed(player.rect.x, player.rect.y, d)
                    not_have_red = False
                    p_r = True


    # camera.update(player)
    # for sprite in all_sprites:
    #     camera.apply(sprite)
    if p_b:
        portal_b.update()
    if p_r:
        portal_r.update()
    walls_group.draw(screen)
    empty_group.draw(screen)
    player_group.draw(screen)
    portals_group.draw(screen)
    pygame.display.flip()
terminate()
