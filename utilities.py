import pygame as pg
from tilemap import collide_hit_rect
from random import uniform, randint
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if hits[0].rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.vel.x = 0
                sprite.hit_rect.centerx = sprite.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centery > sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                if hits[0].rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                sprite.vel.y = 0
                sprite.hit_rect.centery = sprite.pos.y

def wander(sprite, minx, miny, maxx, maxy):
    newx, newy = uniform(minx, maxx), uniform(miny, maxy)
    alter_direction = (randint(0, 1), randint(0, 1))
    if alter_direction[0]:
        newx = (-1 * newx) + sprite.hit_rect.centerx
    else:
        newx += sprite.hit_rect.centerx
    if alter_direction[1]:
        newy = (-1 * newy) + sprite.hit_rect.centery
    else:
        newy += sprite.hit_rect.centery
    return (newx, newy)