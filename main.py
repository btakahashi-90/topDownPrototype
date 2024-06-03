import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
import hud
from random import uniform
vec = pg.math.Vector2  

class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100) # can be removed to prevent repeated movement steps
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        self.map_folder = path.join(game_folder, 'maps')
        music_folder = path.join(game_folder, 'music')
        sound_folder = path.join(game_folder, 'snd')

        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMAGE)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        #self.mob_img = pg.image.load(path.join(img_folder, MOB_IMAGE)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['xl'] = pg.transform.scale(self.bullet_images['lg'], (32, 32))
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))
        self.bullet_images['os'] = pg.transform.scale(self.bullet_images['lg'], (256, 256))
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMGS:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMGS[item])).convert_alpha()
        self.mob_data = {}
        for mob in MOB:
            self.mob_data[mob] = MOB[mob]
            self.mob_data[mob]["img"] = self.mob_img = pg.image.load(path.join(img_folder, self.mob_data[mob]["img"])).convert_alpha()
        # Lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()
        # Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(sound_folder, EFFECTS_SOUNDS[type]))
            if type == 'level_start':
                self.effects_sounds[type].set_volume(0.05)
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS_GUN:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS_GUN[weapon]:
                s = pg.mixer.Sound(path.join(sound_folder, snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(sound_folder, snd))
            s.set_volume(0.05)
            self.zombie_moan_sounds.append(s)
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(sound_folder, snd)))
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(path.join(sound_folder, snd)))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'bigMap.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.player_startx, self.player_starty = 0, 0
        self.spawn_area = {} #["mob-name"] = [minx, miny, maxx, maxy]
        # We'll want to change this to a loop over all mobs to start the dictionary LATER
        self.spawn_area["zombie"] = [] # this will be a list of lists, holding all possible spawn area ranges
        for tile_object in self.map.tmxdata.objects:
            object_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == "player":
                self.player = Player(self, object_center.x, object_center.y)
                self.player_startx = object_center.x
                self.player_starty = object_center.y
            if tile_object.name == "zombie":
                Mob(self, object_center.x, object_center.y)
            if tile_object.name == "zombieSpawn":
                self.spawn_area["zombie"].append([tile_object.x, tile_object.y, tile_object.x + tile_object.width, tile_object.y + tile_object.height])
            if tile_object.name == "wall" and tile_object.visible:
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name in ["health", "shotgun"]:
                Item(self, object_center, tile_object.name)
        # Spawn mobs? or at least try to...
        # should be offset from EDGES by hit_box size
        # should be offset from PLAYER by min spawn distance <- to be used when dynamic spawning is put in place
        for i in range(self.mob_data["zombie"]["max"]):
            # Pick a spawn location
            spawn_area = choice(self.spawn_area["zombie"])
            # calculate viable ranges
            spawn_xmin, spawn_ymin, spawn_xmax, spawn_ymax = spawn_area[0]+self.mob_data["zombie"]["hit_rect"].width, spawn_area[1]+self.mob_data["zombie"]["hit_rect"].height, spawn_area[2]-self.mob_data["zombie"]["hit_rect"].width, spawn_area[3]-self.mob_data["zombie"]["hit_rect"].height
            spawnx, spawny = uniform(spawn_xmin, spawn_xmax), uniform(spawn_ymin, spawn_ymax)
            pos = vec(spawnx, spawny)
            dist_from_player = pos - self.player.pos
            '''
            This section needs work, specifically to determine the appropriate x/y adjustments
            Right now it's POSSIBLE (though unlikely) for a mob to still end up outside the expected range
            It is ALSO POSSIBLE (though unlikely) for a mob to spawn too close
            --This is due to the distance becoming smaller depending on if the mob is above/below or left/right
            --Since we just ADD in all cases where we're NOT outside of a wall we can move away then back towards
            --or even towards the player in both cases, reducing distance significantly
            ***Should adjust checks to include pos relative to player to determine +/-***
            ^^^Remember for this origin is 0, 0 TOP LEFT, NOT RELATIVE TO MAP CENTER^^^
            '''
            if dist_from_player.length() < MIN_SAFE_DIST:
                # special case handling so we don't spawn outside the walls
                if pos.x - MIN_SAFE_DIST / 2 < spawn_xmin:
                    pos.x += MIN_SAFE_DIST / 2
                elif pos.x + MIN_SAFE_DIST / 2 > spawn_xmax:
                    pos.x -= MIN_SAFE_DIST / 2
                else: # in case we're in bounds no matter what we do, just add for now
                    pos.x += MIN_SAFE_DIST / 2
                if pos.y - MIN_SAFE_DIST / 2 < spawn_ymin:
                    pos.y += MIN_SAFE_DIST / 2
                elif pos.y + MIN_SAFE_DIST / 2 > spawn_ymax:
                    pos.y -= MIN_SAFE_DIST / 2
                else: # in case we're in bounds no matter what we do, just add for now
                    pos.y += MIN_SAFE_DIST / 2
            # spawn the mob...
            Mob(self, pos.x, pos.y, "zombie")
            Mob(self, pos.x - 50, pos.y - 50, "piggy")
        self.camera = Camera(self.map.width, self.map.height)
        #self.effects_sounds['level_start'].play()
        self.paused = False
        self.night = False
        self.draw_debug = False

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        #pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # game over?
        if len(self.mobs) == -1:
            self.playing = False
        # player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False, collide_hit_rect)
        for hit in hits:
            if hit.type == "health" and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.player.add_health(HEALTH_PACK_AMOUNT)
                self.effects_sounds['health_up'].play()
            if hit.type == "shotgun":
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = "shotgun"
        # mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= self.mob_data["zombie"]["damage"]
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.hit()
            self.player.pos += vec(self.mob_data["zombie"]["knockback"], 0).rotate(-hits[0].rot)
        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = vec(0, 0)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        # Draw the lightmask (gradient) onto fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self):
        # FPS TRACK
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        # self.draw_grid()
        # self.all_sprites.draw(self.screen) # <- For generic use, removed for camera implementation
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            if isinstance(sprite, Player):
                sprite.rotate_to_mouse(self.camera.apply(sprite))
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug and not isinstance(sprite, MuzzleFlash):
                pg.draw.rect(self.screen, WHITE, self.camera.apply_rect(sprite.hit_rect), 1)
        # Lighting
        if self.night:
            self.render_fog()
        # HUD Functions
        hud.draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        hud.draw_osr_gauge(self.screen, 10, 30, min(1, self.player.osr_gauge / 100))
        hud.draw_inventory_boxes(self.screen, 900, 50) # TODO add inventory list to make more boxes
        self.draw_text("Zombies: {}".format(len(self.mobs)), self.hud_font, 30, WHITE, WIDTH - 10, 10, align="ne")
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH / 2, HEIGHT /2, align="center")

        p_pos = self.camera.apply_rect(self.player.hit_rect)
        pg.draw.line(self.screen, BLACK, p_pos.center, pg.mouse.get_pos(), 1)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_n:
                    self.night = not self.night

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("SHOOSTING THINGZ", self.title_font, 100, RED, WIDTH / 2, HEIGHT * 1/4,  align="center")
        # self.draw_text("Press a key to start", self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3/4, align="center")

        # BUTTONS - placement needs work, current positioning is TOP LEFT and NOT CENTER
        go_button_coords = (WIDTH * 1/4, 550)
        quit_button_coords = (WIDTH * 3/4, 550)
        waiting = True
        while(waiting):
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYUP and event.key == pg.K_ESCAPE):
                    waiting = False
                    self.quit()
            mouse = pg.mouse.get_pos()
            if go_button_coords[0]+100 > mouse[0] > go_button_coords[0] and go_button_coords[1]+50 > mouse[1] > go_button_coords[1]:
                pg.draw.rect(self.screen, LIGHT_GREEN, (WIDTH * 1/4, 550, 100, 50))
                if pg.mouse.get_pressed()[0]:
                    return
            else:
                pg.draw.rect(self.screen, GREEN, (WIDTH * 1/4, 550, 100, 50))
            self.draw_text("Start", self.hud_font, 25, WHITE, go_button_coords[0] + (100 / 2), go_button_coords[1] + (50 / 2), align="center")
            if quit_button_coords[0]+100 > mouse[0] > quit_button_coords[0] and quit_button_coords[1]+50 > mouse[1] > quit_button_coords[1]:
                pg.draw.rect(self.screen, LIGHT_RED, (WIDTH * 3/4, 550, 100, 50))
            else:
                pg.draw.rect(self.screen, RED, (WIDTH * 3/4, 550, 100, 50))
            self.draw_text("Quit", self.hud_font, 25, WHITE, quit_button_coords[0] + (100 / 2), quit_button_coords[1] + (50 / 2), align="center")
            pg.display.update()
        # pg.display.flip()
        # self.wait_for_key()

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to start", self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3/4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        '''
        Timing issue:
        pg.event.wait() will clear the keydown, but will not affect the keyup since the even wont fire until the key is lifted.
        can't use KEYDOWN because a new event is fired while key is pressed, and you want to wait until lift anyways?
        can't clear in loop otherwise user may hit key on perfect frame, causing it to clear immediately.
        --solution--
        Use a button...stop being stupid.
        '''
        pg.event.wait()
        waiting = True
        while(waiting):
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYUP and event.key == pg.K_ESCAPE):
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

# create the game object
g = Game()
#g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()