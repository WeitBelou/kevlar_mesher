import math
from typing import Callable

import numpy as np

from . import config, geo, logger

_LOGGER = logger.get_logger()


def create_warp(task: config.Mesh) -> geo.Layer:
    def fn(t: float) -> geo.Vector:
        return geo.Vector(t, 0, 0)

    fibers_step = 1 / task.warp_density
    n_fibers = int(task.warp_density * task.width)
    points_step = 1 / task.resolution
    root_fiber = create_parametrized_line(fn, 0, task.length, points_step)

    fibers = [root_fiber]
    dp = geo.Point(geo.Vector(0, fibers_step, 0))
    for _ in range(n_fibers):
        fibers.append(fibers[-1].shift(dp=dp))

    return geo.Layer(fibers=fibers)


def create_weft(task: config.Mesh) -> geo.Layer:
    # NOTE(i.kosolapov): Diameter too small
    def fn(t: float) -> geo.Vector:
        return geo.Vector(0, t, 0)

    fibers_step = 1 / task.weft_density
    n_fibers = int(task.weft_density * task.length)
    points_step = 1 / task.resolution

    root_fiber = create_parametrized_line(fn, 0, task.width, points_step)
    fibers = [root_fiber]
    dp = geo.Point(geo.Vector(fibers_step, 0, 0))
    for i in range(n_fibers):
        fibers.append(fibers[-1].shift(dp=dp))

    return geo.Layer(fibers=fibers)


def create_parametrized_line(fn: Callable[[float], geo.Vector], start: float, end: float, step: float) -> geo.Fiber:
    t_arr = np.arange(start=start, stop=end, step=step)

    return geo.Fiber(points=[geo.Point(fn(t)) for t in t_arr])


def create_mesh(task: config.Mesh) -> geo.Mesh:
    _LOGGER.info('Meshing warp...')
    warp = create_warp(task)
    _LOGGER.info('Finish meshing warp...')

    _LOGGER.info('Meshing weft...')
    weft = create_weft(task)
    _LOGGER.info('Finish meshing weft...')

    return geo.Mesh(weft=weft, warp=warp)
