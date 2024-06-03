import pygame as pg
from settings import *
from random import uniform, choice, randint, random
import pytweening as tween
from itertools import chain
import math
from utilities import *
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon = 'pistol' #'pistol' or 'shotgun' for now, inventory later?
        self.damaged = False
        self.one_shot = 'bfg'
        self.osr = False
        self.osr_gauge = 0

        self.debug_timer = pg.time.get_ticks()
        self.debug_print_time = 2000
        # print(self.rect, self.rect.center, self.rect.centerx, self.rect.centery, self.rect.center)

    def get_keys(self): # used for smooth movement
        self.vel = vec(0, 0)
        self.rot_speed = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_a]:
            self.vel = vec(0, -PLAYER_SPEED).rotate(-self.rot)
        if keys[pg.K_d]:
            self.vel = vec(0, PLAYER_SPEED).rotate(-self.rot)
        if keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        # Strafe + Forward/Back - needs calculation to account for increased overall velocity?
        if keys[pg.K_w] and keys[pg.K_a]:
            self.vel = vec(PLAYER_SPEED, -PLAYER_SPEED / 2).rotate(-self.rot)
        if keys[pg.K_w] and keys[pg.K_d]:
            self.vel = vec(PLAYER_SPEED, PLAYER_SPEED / 2).rotate(-self.rot)
        if keys[pg.K_s] and keys[pg.K_a]:
            self.vel = vec(-PLAYER_SPEED / 2, -PLAYER_SPEED / 2).rotate(-self.rot)
        if keys[pg.K_s] and keys[pg.K_d]:
            self.vel = vec(-PLAYER_SPEED / 2, PLAYER_SPEED / 2).rotate(-self.rot)
        
        if keys[pg.K_SPACE] or pg.mouse.get_pressed()[0]:
            self.shoot()
        if pg.mouse.get_pressed()[2] and self.osr_gauge == 100:
            self.shoot_one_shot()
    
    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + WEAPON_OFFSET.rotate(-self.rot)
            self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
            snd = choice(self.game.weapon_sounds[self.weapon])
            if snd.get_num_channels() > 2:
                snd.stop()
            snd.play()
            MuzzleFlash(self.game, pos)

    def shoot_one_shot(self):
        self.osr_gauge = 0
        dir = vec(1, 0).rotate(-self.rot)
        pos = self.pos + WEAPON_OFFSET.rotate(-self.rot)
        #self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
        for i in range(WEAPONS['bfg']['bullet_count']):
            spread = uniform(-WEAPONS['bfg']['spread'], WEAPONS['bfg']['spread'])
            Bullet(self.game, pos, dir.rotate(spread), WEAPONS['bfg']['damage'])
        snd = choice(self.game.weapon_sounds['bfg'])
        if snd.get_num_channels() > 2:
            snd.stop()
        snd.play()
        MuzzleFlash(self.game, pos)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 2)

    def rotate_to_mouse(self, world_pos):
        mx, my = mx, my = pg.mouse.get_pos()
        dx, dy = mx - world_pos.x, my - world_pos.y
        self.rot = math.degrees(math.atan2(-dy, dx)) - 0 # Correction Angle = 0 since our sprite starts facing RIGHT

    def update(self):
        self.get_keys()
        if self.osr_gauge > 100:
            self.osr_gauge = 100
        # self.x += self.vx * self.game.dt #self.rect.x = self.x * TILESIZE <- used for step movement, current code is for smooth movement
        # self.y += self.vy * self.game.dt #self.rect.y = self.y * TILESIZE
        self.pos += self.vel * self.game.dt
        # ROTATION
        ### DEBUGGING FOR MOUSE ROTATION
        # if pg.time.get_ticks() - self.debug_timer > self.debug_print_time:
        #     print(pg.mouse.get_pos(), self.pos)
        #     mx, my = pg.mouse.get_pos()
        #     dx, dy = mx - self.hit_rect.centerx, my - self.hit_rect.centery
        #     angle = math.degrees(math.atan2(-dy, dx))
        #     print(angle)
        #     self.debug_timer = pg.time.get_ticks()    
        ###
        self.rot = (self.rot + (self.rot_speed * self.game.dt)) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        if self.damaged:
            try:
                self.image.fill((255, 0, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y, mtype):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_data[mtype]["img"].copy()
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.rot = 0
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.hit_rect = game.mob_data[mtype]["hit_rect"].copy()
        self.hit_rect.center = self.rect.center
        self.health = game.mob_data[mtype]["health"]
        self.speed = choice(game.mob_data[mtype]["speeds"])
        self.target = game.player
        self.mtype = mtype
        self.wandering = False
        self.wandering_target = self.rect.center
        self.move = False

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < self.game.mob_data[self.mtype]["avoid_radius"]:
                    self.acc += dist.normalize()

    def update(self):
        if self.wandering:
            target_dist = self.wandering_target - self.pos
            if target_dist.length() <= 10:
                self.wandering = False
                self.move = False
            else:
                self.move = True
        else:
            target_dist = self.target.pos - self.pos
            if target_dist.length_squared() < self.game.mob_data[self.mtype]["detect_radius"]**2: # a^2 + b^2 = c^2 converted to just check squares instead of sqrt
                self.move = True
            else:
                self.move = False
        #     if random() < 0.002:
        #         choice(self.game.zombie_moan_sounds).play()
        if self.move:
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.game.mob_data[self.mtype]["img"], self.rot)
            self.rect = self.image.get_rect()
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            try:
                self.acc.scale_to_length(self.speed)
                # Equations of motion
                self.acc += self.vel * -1
                self.vel += self.acc * self.game.dt
                self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
                self.hit_rect.centerx = self.pos.x
                collide_with_walls(self, self.game.walls, 'x')
                self.hit_rect.centery = self.pos.y
                collide_with_walls(self, self.game.walls, 'y')
                self.rect.center = self.hit_rect.center
            except:
                print("Broken mob somewhere!")
        if not self.wandering and not self.move:
            toWander = random()
            if toWander < 0.005:
                self.wandering = True
                self.wandering_target = wander(self, self.hit_rect.width / 2, self.hit_rect.height / 2, self.hit_rect.width + 32, self.hit_rect.height + 32)
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))
            self.game.player.osr_gauge += 10

    def draw_health(self):
        if self.health > 70:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        overlay_bar_width = int(self.hit_rect.width)
        self.overlay_bar = pg.Rect(0, 0, overlay_bar_width, 7)
        width = int(self.hit_rect.width * self.health / self.game.mob_data[self.mtype]["health"])
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < self.game.mob_data[self.mtype]["health"]:
            pg.draw.rect(self.image, TRANSPARENT, self.overlay_bar)
            pg.draw.rect(self.image, col, self.health_bar)

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            self.kill()

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self._layer = OBSTACLE_LAYER
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.post = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.rect.center = pos
        self.pos = pos
        self.hit_rect = self.rect
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1