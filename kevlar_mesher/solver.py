import math
from typing import Generator

from . import geo
from . import logger

_LOGGER = logger.get_logger()


def get_force(point: geo.Point) -> geo.Point:
    pulse_radius = 5  # in XY projection
    pulse_center = geo.Point(50, 50, point.z)  # pulse in XY projection, so use point.z as an ugly hack
    pulse_amplitude = 1  # in parrots (or monkeys, or elephants - whatever you prefer)

    r = point.dist(pulse_center)
    if r <= pulse_radius:
        phase = (math.pi / 2) * (r / pulse_radius)
        return geo.Point(0.0, 0.0, pulse_amplitude * math.cos(phase) ** 2)
    else:
        return geo.Point(0.0, 0.0, 0.0)


def step_fiber(fiber: geo.Fiber, initial_fiber_state: geo.Fiber, step: float) -> geo.Fiber:
    new_points = []
    for idx, point in enumerate(fiber.points):
        # Do not touch edge points for the moment, they are quite complicated
        if idx == 0 or idx == len(fiber.points) - 1:
            new_points.append(point)
            continue

        initial_point = initial_fiber_state.points[idx]
        initial_left_point = initial_fiber_state.points[idx - 1]
        initial_left_dist = initial_point.dist(initial_left_point)
        initial_right_point = initial_fiber_state.points[idx + 1]
        initial_right_dist = initial_point.dist(initial_right_point)

        left_point = fiber.points[idx - 1]
        left_dist = point.dist(left_point)
        phi_left = math.asin((left_point.z - point.z) / left_dist)

        right_point = fiber.points[idx + 1]
        right_dist = point.dist(right_point)
        phi_right = math.asin((right_point.z - point.z) / right_dist)

        E = 10  # in parrots again, not real physical value

        left_force_modulus = E * (left_dist - initial_left_dist) / initial_left_dist
        if left_force_modulus < 0:
            left_force_modulus = 0

        right_force_modulus = E * (right_dist - initial_right_dist) / initial_right_dist
        if right_force_modulus < 0:
            right_force_modulus = 0

        Tz = left_force_modulus * math.sin(phi_left) + right_force_modulus * math.sin(phi_right)
        Tplane = - left_force_modulus * math.cos(phi_left) + right_force_modulus * math.cos(phi_right)

        ext_force = get_force(point)

        force = geo.Point(ext_force.x, ext_force.y, ext_force.z + Tz)

        new_points.append(
            point + force * step
        )

    return geo.Fiber(new_points)


def solve(initial_mesh: geo.Mesh, step: float, n_steps: int) -> Generator[None, geo.Mesh, None]:
    previous_mesh = initial_mesh

    for i in range(n_steps):
        new_weft_fibers = []
        for idx, fiber in enumerate(previous_mesh.weft.fibers):
            initial_fiber_state = initial_mesh.weft.fibers[idx]
            new_weft_fibers.append(step_fiber(fiber, initial_fiber_state, step))

        new_warp_fibers = []
        for idx, fiber in enumerate(previous_mesh.warp.fibers):
            initial_fiber_state = initial_mesh.warp.fibers[idx]
            new_warp_fibers.append(step_fiber(fiber, initial_fiber_state, step))

        previous_mesh = geo.Mesh(
            warp=geo.Layer(new_warp_fibers),
            weft=geo.Layer(new_weft_fibers),
        )
        _LOGGER.info('Done step %d of %d' % (i + 1, n_steps))
        yield previous_mesh
