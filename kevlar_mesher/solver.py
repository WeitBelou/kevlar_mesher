import random
from typing import Iterable

from . import geo


def solve(initial_mesh: geo.Mesh, step: float, n_steps: int) -> Iterable[geo.Mesh]:
    meshes = [initial_mesh]
    for i in range(n_steps):
        new_weft_fibers = []
        for fiber in meshes[-1].weft.fibers:
            new_points = []
            for point in fiber.points:
                new_points.append(
                    point + geo.Point(step * random.random(), step * random.random(), step * random.random())
                )
            new_weft_fibers.append(geo.Fiber(new_points))

        new_warp_fibers = []
        for fiber in meshes[-1].warp.fibers:
            new_points = []
            for point in fiber.points:
                new_points.append(
                    point + geo.Point(step * random.random(), step * random.random(), step * random.random())
                )
            new_warp_fibers.append(geo.Fiber(new_points))

        meshes.append(geo.Mesh(
            warp=geo.Layer(new_warp_fibers),
            weft=geo.Layer(new_weft_fibers),
        ))

    return meshes
