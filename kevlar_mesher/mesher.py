import math
from typing import Callable

import numpy as np

from . import config, logger
from . import geo

_LOGGER = logger.get_logger()


def create_warp(task: config.Task) -> geo.Layer:
    def fn(t: float) -> geo.Point:
        return geo.Point(x=t, y=0, z=0)

    fibers_step = 1 / task.warp_density
    n_fibers = int(task.warp_density * task.width)
    points_step = 1 / task.resolution
    root_fiber = create_parametrized_line(fn, 0, task.length, points_step)

    fibers = [root_fiber]
    dp = geo.Point(x=0, y=fibers_step, z=0)
    for i in range(n_fibers):
        fibers.append(fibers[-1].shift(dp=dp))

    return geo.Layer(fibers=fibers)


def create_weft(task: config.Task) -> geo.Layer:
    def fn(t: float) -> geo.Point:
        r = task.diameter / 2
        d = 1 / task.warp_density

        if t < r:
            return geo.Point(
                x=0,
                y=t,
                z=math.sqrt(r ** 2 - t ** 2),
            )
        elif t < d - r:
            return geo.Point(
                x=0,
                y=t,
                z=0,
            )
        elif t < d + r:
            return geo.Point(
                x=0,
                y=t,
                z=-math.sqrt(r ** 2 - (t - d) ** 2),
            )
        elif t < 2 * d - r:
            return geo.Point(
                x=0,
                y=t,
                z=0,
            )
        elif t < 2 * d:
            return geo.Point(
                x=0,
                y=t,
                z=math.sqrt(r ** 2 - (t - 2 * d) ** 2),
            )
        else:
            n_periods = int(t / (2 * d))
            p = fn(t - n_periods * 2 * d)

            return p + geo.Point(x=0, y=2 * d * n_periods, z=0)

    fibers_step = 1 / task.weft_density
    n_fibers = int(task.weft_density * task.length)
    points_step = 1 / task.resolution

    root_fiber = create_parametrized_line(fn, 0, task.width, points_step)
    fibers = [root_fiber]
    dp = geo.Point(x=fibers_step, y=0, z=0)
    for i in range(n_fibers):
        fibers.append(fibers[-1].shift(dp=dp))

    return geo.Layer(fibers=fibers)


def create_parametrized_line(fn: Callable[[float], geo.Point], start: float, end: float, step: float) -> geo.Fiber:
    t_arr = np.arange(start=start, stop=end, step=step)

    return geo.Fiber(points=[*map(fn, t_arr)])


def create_mesh(task: config.Task) -> geo.Mesh:
    _LOGGER.info('meshing warp...')
    warp = create_warp(task)
    _LOGGER.info('finish meshing warp...')

    _LOGGER.info('meshing weft...')
    weft = create_weft(task)
    _LOGGER.info('finish meshing weft...')

    return geo.Mesh(weft=weft, warp=warp)
