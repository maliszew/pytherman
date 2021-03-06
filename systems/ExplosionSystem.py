"""Explosion system"""

import math
import time

import Box2D
import esper
import pygame
from Box2D.b2 import vec2

from components import Explodable, Physics, Renderable, Bomber
from messaging import DamageMessage
import explosion_anim

NUM_RAYS = 64
BLAST_RADIUS = 2
BLAST_POWER = 1000


class ExplosionSystem(esper.Processor):
    """Responsible for exploding things up."""

    def __init__(self, screen, resolution):
        super().__init__()
        self.screen = screen
        self.resolution = resolution

    def process(self):
        for (entity, (physics,
                      explodable)) in self.world.get_components(Physics,
                                                                Explodable):
            if self._should_explode(explodable):
                hit_already = set()
                for i in range(NUM_RAYS):
                    angle = math.radians((i / NUM_RAYS) * 360)
                    ray_dir = vec2(math.sin(angle), math.cos(angle))
                    bomber = self.world.component_for_entity(explodable.planter, Bomber)
                    if bomber.bombrange == 'lg':
                        BLAST_RADIUS = 3
                    else:
                        BLAST_RADIUS = 2
                    ray_end = physics.body.position + BLAST_RADIUS * ray_dir

                    callback = RayCastClosestCallback()
                    self.world.pworld.RayCast(callback, physics.body.position,
                                              ray_end)
                    if callback.fixture and callback.fixture.body.userData not in hit_already:
                        hit_already.add(callback.fixture.body.userData)
                        self.world.msg_bus.add(DamageMessage(
                            entity,
                            callback.fixture.body.userData,
                            bomber.damage))

                # explosion_image = pygame.image.load("assets/explosion.png")
                # explosion = self.world.create_entity()
                # explosion_body = self.world.pworld.CreateStaticBody(position=physics.body.position)
                # self.world.add_component(explosion, Renderable(image=explosion_image))
                # self.world.add_component(explosion, Physics(body=explosion_body))
                x, y = physics.body.position
                x *= self.world.PPM
                y *= self.world.PPM
                y = self.world.RESOLUTION[1] - y
                bomber = self.world.component_for_entity(explodable.planter, Bomber)
                explosion_anim.run((x, y), self.screen, bomber.bombrange)

                bomber.used -= 1
                self.world.to_delete.add(entity)

    def _should_explode(self, explodable):
        if explodable.explosion_time < time.time():
            return True
        return False


class RayCastClosestCallback(Box2D.b2RayCastCallback):
    """Captures the closest hit shape"""

    def __init__(self, **kwargs):
        Box2D.b2RayCastCallback.__init__(self)
        self.fixture = None

    def ReportFixture(self, fixture, point, normal, fraction):
        self.fixture = fixture
        self.point = vec2(point)
        self.normal = vec2(normal)
        # We do not want the ray to continue
        return -1
