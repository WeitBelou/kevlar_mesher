import json
import logging
from typing import List, Callable

from dataclasses import dataclass

from . import config

DIM = 3

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s'
)

LOGGER = logging.getLogger('mesher')
LOGGER.setLevel(logging.INFO)


@dataclass
class Point:
    x: float
    y: float
    z: float

    def __add__(self, other: 'Point') -> 'Point':
        assert isinstance(other, Point)
        return Point(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def to_json(self):
        return dict(
            x=self.x,
            y=self.y,
            z=self.z,
        )


@dataclass
class Fiber:
    points: List[Point]

    def shift(self, dp: Point) -> 'Fiber':
        new_points = list()
        for p in self.points:
            new_points.append(p + dp)

        return Fiber(points=new_points)

    def to_json(self):
        return dict(
            points=[p.to_json() for p in self.points]
        )


@dataclass
class Layer:
    fibers: List[Fiber]

    def to_json(self):
        return dict(
            fibers=[f.to_json() for f in self.fibers]
        )


@dataclass
class Mesh:
    weft: Layer
    warp: Layer

    def draw(self):
        with open('mesh.json', mode='w+') as f:
            json.dump(self.to_json(), f)

    def to_json(self):
        return dict(
            weft=self.weft.to_json(),
            warp=self.warp.to_json(),
        )


def create_warp(width: float, length: float, density: int) -> Layer:
    def fn(t: float) -> Point:
        return Point(x=t, y=0, z=0)

    fibers_step = 1 / density
    n_fibers = int(density * width)
    points_step = 0.1
    n_points = int(length / points_step)
    root_fiber = create_fiber(fn, points_step, n_points)

    fibers = [root_fiber]
    dp = Point(x=0, y=fibers_step, z=0)
    for i in range(n_fibers - 1):
        fibers.append(fibers[-1].shift(dp=dp))

    return Layer(fibers=fibers)


def create_weft(width: float, length: float, density: int) -> Layer:
    def fn(t: float) -> Point:
        return Point(x=0, y=t, z=0)

    fibers_step = 1 / density
    n_fibers = int(density * width)
    points_step = 0.1
    n_points = int(length / points_step)
    root_fiber = create_fiber(fn, points_step, n_points)

    fibers = [root_fiber]
    dp = Point(x=fibers_step, y=0, z=0)
    for i in range(n_fibers - 1):
        fibers.append(fibers[-1].shift(dp=dp))

    return Layer(fibers=fibers)


def create_fiber(fn: Callable[[float], Point], step: float, n_points: int) -> Fiber:
    points = []

    t = 0
    for i in range(n_points):
        points.append(fn(t))
        t += step

    return Fiber(points=points)


def create_mesh(cfg: config.Config) -> Mesh:
    LOGGER.info('start meshing...')

    warp = create_warp(cfg.width, cfg.length, cfg.warp_density)
    weft = create_weft(cfg.length, cfg.width, cfg.weft_density)

    LOGGER.info('end meshing...')

    return Mesh(weft=weft, warp=warp)
