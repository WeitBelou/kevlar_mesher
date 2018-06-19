import itertools
import math
import pathlib
from typing import List, Callable, Iterable

import numpy as np
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
    points: Iterable[Point]

    def shift(self, dp: Point) -> 'Fiber':
        return Fiber(points=[
            p + dp for p in self.points
        ])


@dataclass
class Layer:
    fibers: List[Fiber]


@dataclass
class Mesh:
    weft: Layer
    warp: Layer

    def save(self, out_dir: str, name: str):
        out = pathlib.Path(out_dir)
        out.mkdir(exist_ok=True)
        out /= pathlib.Path(f'{name}.vtu')

        grid = self.make_grid()

        writer = vtk.vtkXMLDataSetWriter()
        writer.SetFileName(str(out.absolute()))
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


def create_warp(task: config.Task) -> Layer:
    def fn(t: float) -> Point:
        return Point(x=t, y=0, z=0)

    fibers_step = 1 / task.warp_density
    n_fibers = int(task.warp_density * task.width)
    points_step = 1 / task.resolution
    root_fiber = create_parametrized_line(fn, 0, task.length, points_step)

    fibers = [root_fiber]
    dp = Point(x=0, y=fibers_step, z=0)
    for i in range(n_fibers):
        fibers.append(fibers[-1].shift(dp=dp))

    return Layer(fibers=fibers)


def create_weft(task: config.Task) -> Layer:
    def fn(t: float) -> Point:
        r = task.diameter / 2
        d = 1 / task.warp_density

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

    fibers_step = 1 / task.weft_density
    n_fibers = int(task.weft_density * task.length)
    points_step = 1 / task.resolution

    root_fiber = create_parametrized_line(fn, 0, task.width, points_step)
    fibers = [root_fiber]
    dp = Point(x=fibers_step, y=0, z=0)
    for i in range(n_fibers):
        fibers.append(fibers[-1].shift(dp=dp))

    return Layer(fibers=fibers)


def create_parametrized_line(fn: Callable[[float], Point], start: float, end: float, step: float) -> Fiber:
    t_arr = np.arange(start=start, stop=end, step=step)

    return Fiber(points=[*map(fn, t_arr)])


def create_mesh(task: config.Task) -> Mesh:
    _LOGGER.info('meshing warp...')
    warp = create_warp(task)
    _LOGGER.info('finish meshing warp...')

    _LOGGER.info('meshing weft...')
    weft = create_weft(task)
    _LOGGER.info('finish meshing weft...')

    return Mesh(weft=weft, warp=warp)
