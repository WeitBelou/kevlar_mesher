import json
import logging
import math
from typing import List, Callable

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from mpl_toolkits.mplot3d import Axes3D

from . import config

# Required
Axes3D

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

    def save(self):
        with open('mesh.json', mode='w+') as f:
            json.dump(self.to_json(), f)

    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_zlim(-1, 1)

        # weft
        for f in self.weft.fibers:
            xs = np.array([p.x for p in f.points])
            ys = np.array([p.y for p in f.points])
            zs = np.array([p.z for p in f.points])

            ax.plot(xs=xs, ys=ys, zs=zs, c='b')

        # warp
        for f in self.warp.fibers:
            xs = np.array([p.x for p in f.points])
            ys = np.array([p.y for p in f.points])
            zs = np.array([p.z for p in f.points])

            ax.plot(xs=xs, ys=ys, zs=zs, c='r')

        plt.show()

    def to_json(self):
        return dict(
            weft=self.weft.to_json(),
            warp=self.warp.to_json(),
        )


def create_warp(width: float, length: float, density: int, resolution: float) -> Layer:
    def fn(t: float) -> Point:
        return Point(x=t, y=0, z=0)

    fibers_step = 1 / density
    n_fibers = int(density * width)
    points_step = 1 / resolution
    n_points = int(length / points_step)
    root_fiber = create_fiber(fn, points_step, n_points)

    fibers = [root_fiber]
    dp = Point(x=0, y=fibers_step, z=0)
    for i in range(n_fibers - 1):
        fibers.append(fibers[-1].shift(dp=dp))

    return Layer(fibers=fibers)


def create_weft(width: float, length: float, density: int, diameter: float, warp_density: float,
                resolution: float) -> Layer:
    def fn(t: float) -> Point:
        r = diameter / 2
        d = 1 / warp_density

        if t < r:
            return Point(
                x=0,
                y=t,
                z=math.sqrt(r ** 2 - t ** 2),
            )
        elif t < d - r:
            return Point(
                x=0,
                y=t,
                z=0,
            )
        elif t < d + r:
            return Point(
                x=0,
                y=t,
                z=-math.sqrt(r ** 2 - (t - d) ** 2),
            )
        elif t < 2 * d - r:
            return Point(
                x=0,
                y=t,
                z=0,
            )
        elif t < 2 * d:
            return Point(
                x=0,
                y=t,
                z=math.sqrt(r ** 2 - (t - 2 * d) ** 2),
            )
        else:
            return Point(
                x=0,
                y=t,
                z=0,
            )

    fibers_step = 1 / density
    n_fibers = int(density * width)
    points_step = 1 / resolution
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

    warp = create_warp(width=cfg.width, length=cfg.length, density=cfg.warp_density, resolution=cfg.resolution)
    weft = create_weft(width=cfg.length, length=cfg.width, density=cfg.weft_density, warp_density=cfg.warp_density,
                       diameter=cfg.diameter, resolution=cfg.resolution)

    LOGGER.info('end meshing...')

    return Mesh(weft=weft, warp=warp)
