

import pygame as pg
import random
from settings import *
from sprites import *
from os import path
import parallax
import threading


class Game:
    def __init__(self):
        # initialize 
        pg.init()
        pg.mixer.init()
        self.score = 0
        self.health = HEALTH
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()
        self.scroll_world = True
        self.speed = 0
        self.mob_hit = True


    def load_data(self):
        # fortosh ton dedwmenwn
        self.dir = path.dirname(__file__)
        self.map_data = []
        img_dir = path.join(self.dir, 'img')
        with open(path.join(self.dir, HIGH_SCORE_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        with open(path.join(self.dir, MAP_FILE), 'rt') as f:
            for line in f:
                self.map_data.append(line)

        # fortosh spritesheet
        self.hero_spritesheet = Spritesheet(path.join(img_dir, HERO_SPRITESHEET))
        self.assets_spritesheet = Spritesheet(path.join(img_dir, ASSET_SPRITESHEET))
        self.platform_spritesheet = Spritesheet(path.join(img_dir, PLATFORM_SPRITESHEET))
        self.bg = parallax.ParallaxSurface((WIDTH, HEIGHT))
        self.bg.add('p_1.png', 13, (WIDTH, HEIGHT))
        self.bg.add('p_2.png', 4, (WIDTH, HEIGHT))
        self.bg.add('p_3.png', 3, (WIDTH, HEIGHT))
        self.bg.add('p_4.png', 2, (WIDTH, HEIGHT))
        self.bg.add('p_5.png', 1, (WIDTH, HEIGHT))




        # fortosh hxou
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jump33.wav'))
        self.coin_sound = pg.mixer.Sound(path.join(self.snd_dir, 'coin33.wav'))
        self.hit_sound = pg.mixer.Sound(path.join(self.snd_dir, 'hit33.wav'))




    def new(self):
        # start a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.coins = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bad_tiles = pg.sprite.Group()
        self.finish = pg.sprite.Group()
        self.hwalls = pg.sprite.Group()
        self.all_sprites.add(self.player)
        self.image_pos_x = -200
        PLATFORM_LIST_1 = []
        COIN_LIST = []
        MOB_LIST = []
        BAD_TILES_LIST = []
        FINISH = []
        HIDDENWALL_LIST = []
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                #aplo tile
                if tile =='1':
                    values1 = [col, row - 25, 0]
                    PLATFORM_LIST_1.append(values1)
                #nomizma
                if tile =='2':
                    values2 = [col, row - 25]
                    COIN_LIST.append(values2)
                #platforma
                if tile =='3':
                    values3 = [col, row - 25, 2]
                    PLATFORM_LIST_1.append(values3)
                #platforma-de3ia
                if tile =='4':
                    values3 = [col, row - 25, 4]
                    PLATFORM_LIST_1.append(values3)
                #platforma-aristera
                if tile =='5':
                    values3 = [col, row - 25, 5]
                    PLATFORM_LIST_1.append(values3)
                #velaki
                if tile =='6':
                    values3 = [col, row - 25, 6]
                    PLATFORM_LIST_1.append(values3)
                #agka8i
                if tile =='7':
                    values3 = [col, row - 25]
                    BAD_TILES_LIST.append(values3)
                #adeio
                if tile =='8':
                    values3 = [col, row - 25, 2]
                    MOB_LIST.append(values3)
                #ex8ros
                if tile =='9':
                    values3 = [col, row - 25, 1]
                    MOB_LIST.append(values3)

                #telos
                if tile == 'F':
                    values3 = [col, row - 25]
                    FINISH.append(values3)

                if tile == 'H':
                    values3 = [col, row - 25]
                    HIDDENWALL_LIST.append(values3)

        for flag in FINISH:
            f = Finish(*flag, self)
            self.all_sprites.add(f)
            self.finish.add(f)

        for plat in PLATFORM_LIST_1:
            p = Platform(*plat, self)
            self.all_sprites.add(p)
            self.platforms.add(p)

        for mob in MOB_LIST:
            m = Mob(*mob, self)
            self.all_sprites.add(m)
            self.mobs.add(m)

        for tile in BAD_TILES_LIST:
            b = Bad_tiles(*tile, self)
            self.all_sprites.add(b)
            self.bad_tiles.add(b)

        for coin in COIN_LIST:
            c = Coin(*coin, self)
            self.all_sprites.add(c)
            self.coins.add(c)

        for hwall in HIDDENWALL_LIST:
            h = HiddenWall(*hwall, self)
            self.all_sprites.add(h)
            self.hwalls.add(h)
        pg.mixer.music.load(path.join(self.snd_dir, 'Juhani Junkala [Retro Game Music Pack] Level 3.ogg'))
        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # ο παίχτης πρεπει να καθεται πανω στην πλατφορμα μονο οταν πεφτει προς αυτην
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.y < lowest.rect.bottom:
                    self.player.pos.y = lowest.rect.top
                    self.player.vel.y = 0
                    self.player.jumping = False

        if self.health <= 0:
            self.playing = False

        hits_coin = pg.sprite.spritecollide(self.player, self.coins, self.coins)
        if hits_coin:
            self.score += 30
            self.coin_sound.play()
        # εχθρός

        mob_hit = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hit and self.mob_hit:
            self.mob_hit = False
            t = threading.Timer(5.0, self.mob_should_hit)
            t.start()
            self.health -= 1
            self.hit_sound.play()
            if self.player.vel.x > 0:
                self.player.vel.x = -20
            else:
                self.player.vel.x = 30
            print(self.health)

        tiles_hit = pg.sprite.spritecollide(self.player, self.platforms, False)
        if tiles_hit and self.player.vel.y < 0:
            self.player.pos.y = tiles_hit[0].rect.bottom - (tiles_hit[0].rect.bottom - self.player.rect.bottom)
            self.player.vel.y = 0
            print(self.player.rect.right, tiles_hit[0].rect.left)
        if tiles_hit and self.player.rect.right == tiles_hit[0].rect.left:
            print(self.player.rect.right, tiles_hit[0].rect.left)
            self.player.pos.x = tiles_hit[0].rect.left - (tiles_hit[0].rect.left - self.player.rect.left)
            self.player.vel.y = 0

        bad_tiles_hit = pg.sprite.spritecollide(self.player, self.bad_tiles, False)
        if bad_tiles_hit:
            self.health -= 1
            self.hit_sound.play()
            if self.player.vel.x > 0:
                self.player.vel.x = -10
                self.player.vel.y = -10
            else:
                self.player.vel.x = 10
                self.player.vel.y = -10

        finish_hit = pg.sprite.spritecollide(self.player, self.finish, False)
        if finish_hit:
            self.health = 0

        hwall_hit = pg.sprite.spritecollide(self.player, self.hwalls, False)
        if hwall_hit:
             self.health = 0



        # αν ο παιχτης φτασει σε ενα σημειο στην πιστα
        # τοτε οι πλατφορμες θα κινηθουν
        # προς τα αριστερα
        # το ιδιο και αντιστροφα
        # και πανω κατω
        if self.scroll_world:
            if self.player.rect.right >= WIDTH / 2:
                self.player.pos.x -= max(abs(self.player.vel.x), 2)
                for plat in self.platforms:
                    plat.rect.x -= max(abs(self.player.vel.x), 2)
                for coin in self.coins:
                    coin.rect.x -= max(abs(self.player.vel.x), 2)
                for mob in self.mobs:
                    mob.rect.x -= max(abs(self.player.vel.x), 2)
                for tile in self.bad_tiles:
                    tile.rect.x -= max(abs(self.player.vel.x), 2)
                for flag in self.finish:
                    flag.rect.x -= max(abs(self.player.vel.x), 2)
                for hwall in self.hwalls:
                    hwall.rect.x -= max(abs(self.player.vel.x), 2)

                self.bg.scroll(self.player.vel.x, 'horizontal')

            if self.player.rect.right <= WIDTH / 2:
                self.player.pos.x += max(abs(self.player.vel.x), 2)
                for plat in self.platforms:
                    plat.rect.x += max(abs(self.player.vel.x), 2)
                for coin in self.coins:
                    coin.rect.x += max(abs(self.player.vel.x), 2)
                for mob in self.mobs:
                    mob.rect.x += max(abs(self.player.vel.x), 2)
                for tile in self.bad_tiles:
                    tile.rect.x += max(abs(self.player.vel.x), 2)
                for flag in self.finish:
                    flag.rect.x += max(abs(self.player.vel.x), 2)
                for hwall in self.hwalls:
                    hwall.rect.x += max(abs(self.player.vel.x), 2)

                self.bg.scroll(self.player.vel.x, 'horizontal')

            if self.player.rect.top <= 350:
                self.player.pos.y += abs(self.player.vel.y)
                for plat in self.platforms:
                    plat.rect.y += abs(self.player.vel.y)
                for coin in self.coins:
                    coin.rect.y += abs(self.player.vel.y)
                for mob in self.mobs:
                    mob.rect.y += abs(self.player.vel.y)
                for tile in self.bad_tiles:
                    tile.rect.y += abs(self.player.vel.y)
                for flag in self.finish:
                    flag.rect.y += abs(self.player.vel.y)
                for hwall in self.hwalls:
                    hwall.rect.y += abs(self.player.vel.y)

            if self.player.rect.bottom >= HEIGHT -250 :
                self.player.pos.y -= max(abs(self.player.vel.y), 5)
                for plat in self.platforms:
                    plat.rect.y -= max(abs(self.player.vel.y), 5)
                for coin in self.coins:
                    coin.rect.y -= max(abs(self.player.vel.y), 5)
                for mob in self.mobs:
                    mob.rect.y -= max(abs(self.player.vel.y), 5)
                for tile in self.bad_tiles:
                    tile.rect.y -= max(abs(self.player.vel.y), 5)
                for flag in self.finish:
                    flag.rect.y -= max(abs(self.player.vel.y), 5)
                for hwall in self.hwalls:
                    hwall.rect.y -= max(abs(self.player.vel.y), 5)


    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def mob_should_hit(self):
        self.mob_hit = True
        # check gia ta 5 deuterolepta cooldown meta to hit



    def draw(self):
        # Game Loop - draw
        self.bg.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 30, WHITE, WIDTH - 30, 20)
        self.draw_text("HEALTH: " + str(self.health), 30, WHITE, 80, 20)
        # flip display teleuteo
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_start_screen(self):
        self.bg.draw(self.screen)
        self.bg.scroll(100, 'horizontal')
        # arxikh othonh
        pg.mixer.music.load(path.join(self.snd_dir, 'Juhani Junkala [Retro Game Music Pack] Title Screen.ogg'))
        pg.mixer.music.play(loops=-1)

        self.draw_text(TITLE, 60, BLACK, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Κινούμαστε με τα βελάκια και πηδάμε με το spacebar", 20, BLACK, WIDTH / 2, 200)
        self.draw_text("Πατήστε ενα κουμπί για να ξεκινήσετε", 20, BLACK, WIDTH / 2, 150)
        self.draw_text("High score:" + str(self.highscore), 20, BLACK, WIDTH / 2, 100)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'Juhani Junkala [Retro Game Music Pack] Ending.ogg'))
        pg.mixer.music.play(loops=-1)


        self.screen.fill(RED)
        self.draw_text("GAME OVER", 60, BLACK, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Τελικό σκορ:"+str(self.score), 20, BLACK, WIDTH / 2, 200)
        self.draw_text("Πατήστε ενα κουμπί για να συνεχίσετε", 20, BLACK, WIDTH / 2, 150)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("Νέο HIGHSCORE :"+ (str(self.score)), 20, BLACK, WIDTH / 2, 100)
            with open(path.join(self.dir, HIGH_SCORE_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High score:" + str(self.highscore), 20, BLACK, WIDTH / 2, 50)
        pg.display.flip()
        self.__init__()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)


    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
