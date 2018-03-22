from typing import List

from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
    z: float


@dataclass
class Fiber:
    points: List[Point]


def create_fiber():
    pass


@dataclass
class Layer:
    warp: List[Fiber]
    weft: List[Fiber]


@dataclass
class Mesh:
    layers: List[Layer]
