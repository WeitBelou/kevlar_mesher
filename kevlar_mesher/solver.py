import math
from typing import Generator

from . import config, geo, logger

_LOGGER = logger.get_logger()


def get_force(cfg: config.Pulse, point: geo.Vector) -> geo.Vector:
    pulse_center = cfg.center
    pulse_center.z = point.z  # pulse in XY projection, so use point.z as an ugly hack

    r = point.dist(pulse_center)
    if r <= cfg.radius:
        phase = (math.pi / 2) * (r / cfg.radius)
        return geo.Vector(0.0, 0.0, cfg.amplitude * math.cos(phase) ** 2)
    else:
        return geo.Vector(0.0, 0.0, 0.0)


def step_fiber(cfg: config.Solver, fiber: geo.Fiber, initial_fiber_state: geo.Fiber) -> geo.Fiber:
    new_points = []
    for idx, point in enumerate(fiber.points):
        # Do not touch edge points for the moment, they are quite complicated
        if idx == 0 or idx == len(fiber.points) - 1:
            new_points.append(point)
            continue

        initial_point = initial_fiber_state.points[idx]
        initial_left_point = initial_fiber_state.points[idx - 1]
        initial_left_dist = initial_point.coords.dist(
            initial_left_point.coords)
        initial_right_point = initial_fiber_state.points[idx + 1]
        initial_right_dist = initial_point.coords.dist(
            initial_right_point.coords)

        left_point = fiber.points[idx - 1]
        left_dist = point.coords.dist(left_point.coords)
        phi_left = math.asin(
            (left_point.coords.z - point.coords.z) / left_dist)

        right_point = fiber.points[idx + 1]
        right_dist = point.coords.dist(right_point.coords)
        phi_right = math.asin(
            (right_point.coords.z - point.coords.z) / right_dist)

        E = 10  # in parrots again, not real physical value

        left_eps = (left_dist - initial_left_dist) / initial_left_dist
        if left_eps < 0:
            left_eps = 0
        left_force_modulus = E * left_eps

        right_eps = (right_dist - initial_right_dist) / initial_right_dist
        if right_eps < 0:
            right_eps = 0
        right_force_modulus = E * right_eps

        Tz = left_force_modulus * \
            math.sin(phi_left) + right_force_modulus * math.sin(phi_right)
        Tplane = - left_force_modulus * \
            math.cos(phi_left) + right_force_modulus * math.cos(phi_right)

        ext_force = get_force(cfg.pulse, point.coords)
        force = geo.Vector(ext_force.x, ext_force.y, ext_force.z + Tz)

        new_point = geo.Point(
            point.coords + force * cfg.step,
        )

        new_point.data = (left_eps + right_eps) / 2

        new_points.append(new_point)

    return geo.Fiber(new_points)


def solve(initial_mesh: geo.Mesh, cfg: config.Solver) -> Generator[None, geo.Mesh, None]:
    previous_mesh = initial_mesh

    for _ in range(cfg.n_steps):
        new_weft_fibers = []
        for idx, fiber in enumerate(previous_mesh.weft.fibers):
            initial_fiber_state = initial_mesh.weft.fibers[idx]
            new_weft_fibers.append(step_fiber(cfg, fiber, initial_fiber_state))

        new_warp_fibers = []
        for idx, fiber in enumerate(previous_mesh.warp.fibers):
            initial_fiber_state = initial_mesh.warp.fibers[idx]
            new_warp_fibers.append(step_fiber(cfg, fiber, initial_fiber_state))

        previous_mesh = geo.Mesh(
            warp=geo.Layer(new_warp_fibers),
            weft=geo.Layer(new_weft_fibers),
        )
        yield previous_mesh
