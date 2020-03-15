
from settings import *
import pygame as pg
import random

vec = pg.math.Vector2


class Spritesheet:
    def __init__(self, filename):
        self.hero_spritesheet = pg.image.load(filename).convert()
        self.assets_spritesheet = pg.image.load(filename).convert()
        self.platform_spritesheet = pg.image.load(filename).convert()

    def get_hero_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.hero_spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width * 2, height * 2))
        return image

    def get_coin_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.assets_spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image

    def get_tile_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.assets_spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (TILESIZE, TILESIZE))
        return image

    def get_mob_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.assets_spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (TILESIZE, TILESIZE))
        return image


class Player(pg.sprite.Sprite):

    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.walking = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.jumping = False
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(300, 500)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):

        self.standing_frames = [self.game.hero_spritesheet.get_hero_image(12, 4, 22, 45)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        self.running_frames_r = [self.game.hero_spritesheet.get_hero_image(10 - 8, 159, 42, 40),
                                 self.game.hero_spritesheet.get_hero_image(55 - 8, 159, 42, 40),
                                 self.game.hero_spritesheet.get_hero_image(100 - 8, 159, 42, 40),
                                 self.game.hero_spritesheet.get_hero_image(145 - 8, 159, 42, 40),
                                 self.game.hero_spritesheet.get_hero_image(190 - 8, 159, 42, 40),
                                 self.game.hero_spritesheet.get_hero_image(235 - 8, 159, 42, 40),
                                 self.game.hero_spritesheet.get_hero_image(280 - 8, 159, 42, 40),
                                 self.game.hero_spritesheet.get_hero_image(325 - 8, 159, 42, 40)]

        self.running_frames_l = []
        for frame in self.running_frames_r:
            frame.set_colorkey(BLACK)
            self.running_frames_l.append(pg.transform.flip(frame, True, False))

        self.jumping_frames_r = [self.game.hero_spritesheet.get_hero_image(280 - 8, 4, 42, 45),
                                 self.game.hero_spritesheet.get_hero_image(325 - 8, 4, 42, 45)]
        self.jumping_frames_l = []
        for frame in self.jumping_frames_r:
            frame.set_colorkey(BLACK)
            self.jumping_frames_l.append(pg.transform.flip(frame, True, False))

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
        # μεταβλητή της τριβής
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # εξισώσεις κίνησης
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # για να μην ξεφευγει ο χαρακτήρας μας απο τα όρια
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos
    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if self.walking and not self.jumping and abs(self.vel.x) > 2:
            if now - self.last_update > 80:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.running_frames_r)
                if self.vel.x > 0:
                    self.image = self.running_frames_r[self.current_frame]
                else:
                    self.image = self.running_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.walking = False

        if self.jumping:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.jumping_frames_r)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.jumping_frames_r[self.current_frame]
                else:
                    self.image = self.jumping_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

    def jump(self):
        # προυποθεσή για να πηδήξουμε ειναι να στεκομαστε πανω σε μια πλατφόρμα
        self.rect.x += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = PLAYER_JUMP

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y, game):
        pg.sprite.Sprite.__init__(self)
        self.current_frame = 0
        self.game = game
        self.last_update = 0
        self.load_images()
        self.image = self.coin_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def update(self):
        self.animate()

    def load_images(self):
        self.coin_frames = [self.game.assets_spritesheet.get_coin_image(698, 1931, 84, 84),
                            self.game.assets_spritesheet.get_coin_image(829, 0, 66, 84),
                            self.game.assets_spritesheet.get_coin_image(897, 1574, 50, 84),
                            self.game.assets_spritesheet.get_coin_image(645, 651, 15, 84)]
        for frame in self.coin_frames:
            frame.set_colorkey(BLACK)

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 150:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.coin_frames)
            self.image = self.coin_frames[self.current_frame]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, tile_num, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.tile_num = tile_num
        self.load_images()
        self.image = self.tile_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def update(self):
        self.animate()

    def load_images(self):
        self.tile_frames = [self.game.platform_spritesheet.get_tile_image(504, 576, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(720, 432, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(576, 288, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(576, 288, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(576, 360, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(576, 360, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(288, 288, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(720, 432, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(720, 432, TILESIZE, TILESIZE)
                            ]
        self.tile_frames_fliped = []
        for frame in self.tile_frames:
            frame.set_colorkey(BLACK)
            self.tile_frames_fliped.append(pg.transform.flip(frame, True, False))
        for frame in self.tile_frames:
            frame.set_colorkey(BLACK)

    def animate(self):
        # auth h me8odos telika den xreiazotan kai poly epeidh uphrxe h eikona hdh fliped sto spritesheet
        # alla to phra xampari meta kai eipa na to afhsw etsi :P
        # an artios tote gurna thn eikona
        if (self.tile_num % 2) == 0:
            self.image = self.tile_frames_fliped[self.tile_num]
        else:
            self.image = self.tile_frames[self.tile_num]
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center


class Mob(pg.sprite.Sprite):
    def __init__(self, x, y,up, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.up = up
        self.image = pg.Surface([TILESIZE, TILESIZE])
        self.rect = self.image.get_rect()
        self.load_images()
        self.image = self.mob_frames[0]
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.x = x
        self.y = y
        self.counter = 0
        self.current_frame = 0
        self.last_update = 0

    def update(self):
        distance = 50
        speed = random.randrange(5, 10)
        if self.up == 1:
            if 0 <= self.counter <= distance:
                self.rect.x += speed
            elif distance <= self.counter <= distance * 2:
                self.rect.x -= speed
            else:
                self.counter = 0
        else:
            if 0 <= self.counter <= distance:
                self.rect.y += speed
            elif distance <= self.counter <= distance * 2:
                self.rect.y -= speed
            else:
                self.counter = 0
        self.counter += 1
        self.animate()

    def load_images(self):
        self.mob_frames = [self.game.assets_spritesheet.get_mob_image(534, 763, 142, 148),
                            self.game.assets_spritesheet.get_mob_image(464, 1122, 148, 141),
                            self.game.assets_spritesheet.get_mob_image(534, 763, 142, 148),
                            self.game.assets_spritesheet.get_mob_image(464, 1122, 148, 141)]
        for frame in self.mob_frames:
            frame.set_colorkey(BLACK)

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 100:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.mob_frames)
            self.image = self.mob_frames[self.current_frame]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center


class Bad_tiles(pg.sprite.Sprite):
    def __init__(self, x, y, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.load_images()
        self.image = self.tile_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def update(self):
        self.animate()

    def load_images(self):
        self.tile_frames = [self.game.platform_spritesheet.get_tile_image(504, 576, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(720, 432, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(576, 288, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(576, 288, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(576, 360, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(576, 360, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(288, 288, TILESIZE, TILESIZE),
                            self.game.assets_spritesheet.get_mob_image(885, 752, TILESIZE, TILESIZE),
                            self.game.platform_spritesheet.get_tile_image(720, 432, TILESIZE, TILESIZE)
                            ]
        for frame in self.tile_frames:
            frame.set_colorkey(BLACK)

    def animate(self):
        self.image = self.tile_frames[7]
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center


class Finish(pg.sprite.Sprite):
    def __init__(self, x, y, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = self.game.platform_spritesheet.get_tile_image(288,360,70,70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE





class HiddenWall(pg.sprite.Sprite):
    def __init__(self, x, y, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface([1000, 50], pg.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
