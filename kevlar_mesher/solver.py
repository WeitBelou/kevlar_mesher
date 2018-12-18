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
    speed_of_sound_squared = 10

    new_points = []
    for idx, point in enumerate(fiber.points):
        # Do not touch edge points for the moment, they are quite complicated
        if idx == 0 or idx == len(fiber.points) - 1:
            new_points.append(point)
            continue

        initial_point = initial_fiber_state.points[idx]

        initial_left_point = initial_fiber_state.points[idx - 1]
        initial_left_dist = initial_point.coords.dist(initial_left_point.coords)

        initial_right_point = initial_fiber_state.points[idx + 1]
        initial_right_dist = initial_point.coords.dist(initial_right_point.coords)

        left_point = fiber.points[idx - 1]
        left_dist = point.coords.dist(left_point.coords)
        sin_phi_left = (left_point.coords.z - point.coords.z) / left_dist

        right_point = fiber.points[idx + 1]
        right_dist = point.coords.dist(right_point.coords)
        sin_phi_right = (right_point.coords.z - point.coords.z) / right_dist

        left_eps = (left_dist - initial_left_dist) / initial_left_dist
        if left_eps < 0:
            left_eps = 0
        left_force_modulus = speed_of_sound_squared * left_eps

        right_eps = (right_dist - initial_right_dist) / initial_right_dist
        if right_eps < 0:
            right_eps = 0
        right_force_modulus = speed_of_sound_squared * right_eps

        tension_force_normal = (left_force_modulus * sin_phi_left + right_force_modulus * sin_phi_right)

        ext_force = get_force(cfg.pulse, point.coords)
        force = geo.Vector(ext_force.x, ext_force.y, ext_force.z + tension_force_normal)

        new_points.append(geo.Point(
            coords=point.coords + point.velocity * cfg.step,
            velocity=point.velocity + force * cfg.step,
            data=(left_eps + right_eps) / 2,
        ))

    return geo.Fiber(new_points)


def solve(initial_mesh: geo.Mesh, cfg: config.Solver) -> Generator[None, geo.Mesh, None]:
    previous_mesh = initial_mesh

    while True:
        new_weft_fibers = []
        for idx, fiber in enumerate(previous_mesh.weft.fibers):
            initial_fiber_state = initial_mesh.weft.fibers[idx]
            new_weft_fibers.append(step_fiber(cfg, fiber, initial_fiber_state))
        new_weft = geo.Layer(new_weft_fibers)

        new_warp_fibers = []
        for idx, fiber in enumerate(previous_mesh.warp.fibers):
            initial_fiber_state = initial_mesh.warp.fibers[idx]
            new_warp_fibers.append(step_fiber(cfg, fiber, initial_fiber_state))
        new_warp = geo.Layer(new_warp_fibers)

        previous_mesh = geo.Mesh(
            warp=new_warp,
            weft=new_weft,
        )
        yield previous_mesh
