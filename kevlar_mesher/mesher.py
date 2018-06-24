import math
from typing import Callable

import numpy as np

from . import config, logger
from . import geo

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
    for i in range(n_fibers):
        fibers.append(fibers[-1].shift(dp=dp))

    return geo.Layer(fibers=fibers)


def create_weft(task: config.Mesh) -> geo.Layer:
    def fn(t: float) -> geo.Vector:
        r = task.diameter / 2
        d = 1 / task.warp_density

        if t < r:
            return geo.Vector(0, t, math.sqrt(r ** 2 - t ** 2))
        elif t < d - r:
            return geo.Vector(0, t, 0)
        elif t < d + r:
            return geo.Vector(0, t, -math.sqrt(r ** 2 - (t - d) ** 2))
        elif t < 2 * d - r:
            return geo.Vector(0, t, 0)
        elif t < 2 * d:
            return geo.Vector(0, t, math.sqrt(r ** 2 - (t - 2 * d) ** 2))
        else:
            n_periods = int(t / (2 * d))
            p = fn(t - n_periods * 2 * d)

            return p + geo.Vector(0, 2 * d * n_periods, 0)

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
    _LOGGER.info('meshing warp...')
    warp = create_warp(task)
    _LOGGER.info('finish meshing warp...')

    _LOGGER.info('meshing weft...')
    weft = create_weft(task)
    _LOGGER.info('finish meshing weft...')

    return geo.Mesh(weft=weft, warp=warp)
