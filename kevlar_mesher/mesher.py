import itertools
import math
from typing import List, Callable

import vtk
from dataclasses import dataclass

from . import config, logger

DIM = 3

_LOGGER = logger.get_logger()


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


@dataclass
class Fiber:
    points: List[Point]

    def shift(self, dp: Point) -> 'Fiber':
        new_points = list()
        for p in self.points:
            new_points.append(p + dp)

        return Fiber(points=new_points)


@dataclass
class Layer:
    fibers: List[Fiber]


@dataclass
class Mesh:
    weft: Layer
    warp: Layer

    def save(self):
        grid = self.make_grid()

        writer = vtk.vtkXMLDataSetWriter()
        writer.SetFileName('mesh.vtu')
        writer.SetInputData(grid)
        writer.Write()

    def make_grid(self):
        ug = vtk.vtkUnstructuredGrid()
        all_points = vtk.vtkPoints()
        ug.SetPoints(all_points)

        current_idx = 0
        for fiber in itertools.chain(self.weft.fibers, self.warp.fibers):
            polyline = vtk.vtkPolyLine()
            for point in fiber.points:
                all_points.InsertNextPoint(point.x, point.y, point.z)
                polyline.GetPointIds().InsertNextId(current_idx)
                current_idx += 1

            ug.InsertNextCell(polyline.GetCellType(), polyline.GetPointIds())

        return ug


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
            n_periods = int(t / (2 * d))
            p = fn(t - n_periods * 2 * d)

            return p + Point(x=0, y=2 * d * n_periods, z=0)

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
    _LOGGER.info('start meshing...')

    warp = create_warp(width=cfg.width, length=cfg.length, density=cfg.warp_density, resolution=cfg.resolution)
    weft = create_weft(width=cfg.length, length=cfg.width, density=cfg.weft_density, warp_density=cfg.warp_density,
                       diameter=cfg.diameter, resolution=cfg.resolution)

    _LOGGER.info('end meshing...')

    return Mesh(weft=weft, warp=warp)
